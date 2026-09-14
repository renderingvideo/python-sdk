"""Optional Ed25519 agent authentication. Install renderingvideo[agent]."""
import base64
import hashlib
import json
import math
import platform
import secrets
import threading
import time
import urllib.parse
import urllib.request
import uuid

from ._http import request_json, send


def encode(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def decode(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


class AgentAuth:
    def __init__(self, agent_key, device, base_url="https://renderingvideo.com", timeout=30):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        except ImportError as error:
            raise ImportError('AgentAuth requires: pip install "renderingvideo[agent]"') from error
        url = urllib.parse.urlsplit(base_url)
        local = url.hostname in ("localhost", "127.0.0.1", "::1")
        if (not url.netloc or url.username or url.password or url.query or url.fragment or
                url.path not in ("", "/") or
                (url.scheme != "https" and not (url.scheme == "http" and local))):
            raise ValueError("Agent API base_url must be an HTTPS origin (HTTP is allowed for localhost)")
        if not agent_key.startswith("ak_") or not device.get("id", "").strip():
            raise ValueError("An ak_ agent key and persistent device ID are required")
        self.base_url = urllib.parse.urlunsplit((url.scheme, url.netloc, "", "", ""))
        self._key = agent_key
        self._device = dict(device)
        self._timeout = timeout
        self._private_key = serialization.load_der_private_key(decode(device["privateKey"]), password=None)
        if not isinstance(self._private_key, Ed25519PrivateKey):
            raise ValueError("Device key must be Ed25519")
        public = self._private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        if encode(public) != device["publicKey"]:
            raise ValueError("Device public/private keys do not match")
        self._token = None
        self._expires_at = 0
        self._lock = threading.Lock()

    @staticmethod
    def generate_device():
        """Generate once, store securely, and reuse this identity across runs."""
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        key = Ed25519PrivateKey.generate()
        return {
            "id": str(uuid.uuid4()), "name": platform.node(), "platform": platform.system(), "arch": platform.machine(),
            "publicKey": encode(key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)),
            "privateKey": encode(key.private_bytes(serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())),
        }

    def _proof(self, credential, method, url):
        timestamp = str(int(time.time() * 1000))
        nonce = encode(secrets.token_bytes(24))
        parsed = urllib.parse.urlsplit(url)
        path = parsed.path + (("?" + parsed.query) if parsed.query else "")
        payload = "\n".join(("RV-AGENT-PROOF-V1", method.upper(), path, timestamp, nonce,
                             encode(hashlib.sha256(credential.encode("utf-8")).digest())))
        return {"x-agent-device-id": self._device["id"], "x-agent-timestamp": timestamp,
                "x-agent-nonce": nonce, "x-agent-signature": encode(self._private_key.sign(payload.encode("utf-8")))}

    def _exchange(self):
        url = self.base_url + "/api/agent/token"
        device = {"id": self._device["id"], "publicKey": self._device["publicKey"],
                  "name": self._device.get("name") or platform.node(),
                  "platform": self._device.get("platform") or platform.system(),
                  "arch": self._device.get("arch") or platform.machine(),
                  "agentVersion": "renderingvideo-python-sdk/1.1"}
        headers = {"Authorization": "AgentKey " + self._key, "Content-Type": "application/json",
                   **self._proof(self._key, "POST", url)}
        req = urllib.request.Request(url, data=json.dumps({"device": device}).encode("utf-8"), headers=headers, method="POST")
        data = send(req, self._timeout, no_redirect=True)
        ttl = data.get("expires_in")
        if (not isinstance(data.get("access_token"), str) or not data["access_token"].startswith("at_") or
                not isinstance(ttl, (int, float)) or isinstance(ttl, bool) or not math.isfinite(ttl) or ttl <= 0):
            raise ValueError("Invalid agent token response")
        self._token = data["access_token"]
        self._expires_at = time.time() + ttl

    def invalidate(self):
        """Discard a token explicitly. Mutating requests are never replayed automatically."""
        with self._lock:
            self._token = None

    def headers(self, method, url):
        parsed = urllib.parse.urlsplit(url)
        origin = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
        if origin != self.base_url or not parsed.path.startswith(("/api/v1/", "/api/agent/v1/")):
            raise ValueError("Agent request is outside the configured API origin")
        with self._lock:
            if not self._token or self._expires_at <= time.time() + 30:
                self._exchange()
            token = self._token
        return {"Authorization": "Bearer " + token, **self._proof(token, method, url)}


class AgentClient:
    def __init__(self, auth, timeout):
        self._auth = auth
        self._timeout = timeout

    def context(self):
        return request_json(self._auth.base_url, "", self._timeout, "GET", "/api/agent/v1/context", agent_auth=self._auth)

    def audit(self, page=1, page_size=20, risk_level=None, all_keys=False):
        return request_json(self._auth.base_url, "", self._timeout, "GET", "/api/agent/v1/audit",
                            params={"page": page, "pageSize": page_size, "riskLevel": risk_level, "allKeys": all_keys}, agent_auth=self._auth)
