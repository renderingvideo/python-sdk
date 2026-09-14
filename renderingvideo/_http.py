"""Shared response and device-auth handling for JSON and multipart requests."""
import json
import urllib.error
import urllib.parse
import urllib.request

from .types import (AlreadyRenderingError, AuthenticationError, InsufficientCreditsError,
                    NotFoundError, RateLimitError, RenderingVideoError, ValidationError)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fail(data, status):
    code = data.get("code", "API_ERROR")
    kind = {400: ValidationError, 401: AuthenticationError, 402: InsufficientCreditsError,
            404: NotFoundError, 429: RateLimitError}.get(status, RenderingVideoError)
    if code == "ALREADY_RENDERING":
        kind = AlreadyRenderingError
    raise kind(data.get("error") or data.get("message") or "API request failed", code, data, status)


def send(req, timeout, no_redirect=False):
    opener = urllib.request.build_opener(NoRedirect()).open if no_redirect else urllib.request.urlopen
    try:
        with opener(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            if not isinstance(data, dict):
                raise RenderingVideoError("Invalid JSON response", "INVALID_RESPONSE")
            if data.get("success") is False:
                fail(data, getattr(response, "status", 200))
            return data
    except urllib.error.HTTPError as error:
        try:
            data = json.loads(error.read().decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            data = {"error": "API returned HTTP %s" % error.code}
        fail(data if isinstance(data, dict) else {}, error.code)
    except urllib.error.URLError as error:
        raise RenderingVideoError("Network error: %s" % error.reason, "NETWORK_ERROR") from error
    except (ValueError, UnicodeDecodeError) as error:
        raise RenderingVideoError("Invalid JSON response", "INVALID_RESPONSE") from error


def request_json(base_url, api_key, timeout, method, endpoint, data=None, params=None, agent_auth=None):
    url = base_url.rstrip("/") + endpoint
    if params:
        url += "?" + urllib.parse.urlencode({k: str(v).lower() if isinstance(v, bool) else v
                                           for k, v in params.items() if v is not None})
    headers = agent_auth.headers(method, url) if agent_auth else {"Authorization": "Bearer " + api_key}
    headers["Content-Type"] = "application/json"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    return send(req, timeout, no_redirect=agent_auth is not None)
