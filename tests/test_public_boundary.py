import pytest
import renderingvideo
from renderingvideo import Client

@pytest.mark.parametrize('credential', ['ak_admin-fixture', 'at_admin-fixture'])
def test_administrator_credentials_are_rejected(credential):
    with pytest.raises(ValueError, match='sk-'):
        Client(credential)

def test_public_client_has_no_administrator_mode():
    with pytest.raises(TypeError):
        Client(agent_auth=object())
    assert not hasattr(renderingvideo, 'AgentAuth')
    assert not hasattr(Client('sk-user-fixture'), 'agent')
