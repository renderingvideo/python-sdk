import hashlib
from unittest.mock import patch
import pytest
from renderingvideo import AgentAuth, Client
from renderingvideo.agent import decode, encode
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def test_device_proof_binds_exact_query_and_token_and_refreshes():
    device = AgentAuth.generate_device()
    auth = AgentAuth('ak_test', device)
    url = 'https://renderingvideo.com/api/agent/v1/audit?allKeys=true&riskLevel=high%20risk'
    with patch('renderingvideo.agent.send', return_value={'access_token': 'at_test', 'expires_in': 300}) as send:
        first = auth.headers('GET', url)
        second = auth.headers('GET', url)
        assert send.call_count == 1
        assert first['x-agent-nonce'] != second['x-agent-nonce']
        assert b'privateKey' not in send.call_args.args[0].data
        payload = '\n'.join(['RV-AGENT-PROOF-V1', 'GET', '/api/agent/v1/audit?allKeys=true&riskLevel=high%20risk', first['x-agent-timestamp'], first['x-agent-nonce'], encode(hashlib.sha256(b'at_test').digest())])
        key = Ed25519PublicKey.from_public_bytes(decode(device['publicKey']))
        key.verify(decode(first['x-agent-signature']), payload.encode())
        with pytest.raises(Exception):
            key.verify(decode(first['x-agent-signature']), payload.replace('allKeys=true', 'allKeys=false').encode())
        auth.invalidate()
        auth.headers('GET', url)
        assert send.call_count == 2

def test_agent_origin_and_key_pair_are_validated():
    device = AgentAuth.generate_device()
    with pytest.raises(ValueError):
        AgentAuth('ak_test', device, base_url='http://example.com')
    with pytest.raises(ValueError):
        AgentAuth('ak_test', dict(device, publicKey=AgentAuth.generate_device()['publicKey']))
    auth = AgentAuth('ak_test', device)
    with pytest.raises(ValueError):
        auth.headers('GET', 'https://example.com/api/v1/credits')
    with pytest.raises(ValueError):
        Client('sk_test', agent_auth=auth)
    with pytest.raises(ValueError):
        Client(agent_auth=auth, base_url='https://different.example')
