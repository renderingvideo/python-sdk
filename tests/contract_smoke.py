"""Run against the application repository's local SDK contract fixture."""
import io
import os
from renderingvideo import AgentAuth, Client, RenderingVideoError
origin = os.environ['RV_TEST_ORIGIN']
assert origin.startswith('http://127.0.0.1:')
api = Client('sk-contract', base_url=origin)
config = {'meta': {'version': '2.0.0', 'width': 1280, 'height': 720, 'fps': 30}, 'tracks': [{'clips': [{'type': 'text', 'text': 'SDK launch', 'start': 0, 'duration': 2}]}]}
assert 'three' in api.get_capabilities()['schema']['clipTypes']
task = api.video.create(config, title='SDK launch', category='marketing', metadata={'campaign': 'launch'})
assert task.title == 'SDK launch'
assert api.video.list(category='all').tasks[0].category == 'marketing'
assert api.preview.create(config).temp_id == 'preview-test'
assert api.preview.get('preview-test').config['meta']
api.preview.convert('preview-test', metadata={'campaign': 'launch'})
api.preview.render('preview-test', metadata={'campaign': 'launch'}, num_workers=2)
api.video.render(task.task_id, num_workers=2)
file = io.BytesIO(b'test')
file.name = 'test.png'
assert api.files.upload(file=file).count == 1
auth = AgentAuth('ak_contract', AgentAuth.generate_device(), base_url=origin)
client = Client(agent_auth=auth)
client.agent.context()
client.get_credits()
assert client.agent.audit(all_keys=True, risk_level='high risk')['total'] == 0
try:
    client.agent.audit(risk_level='denied')
    raise AssertionError('Expected a scope error')
except RenderingVideoError as error:
    assert error.code == 'INSUFFICIENT_SCOPE'
auth.invalidate()
client.agent.context()
client.files.upload(file=file)
try:
    auth.headers('GET', 'https://different.example/api/v1/credits')
    raise AssertionError('Expected an origin error')
except ValueError:
    pass
print('Python SDK contracts and device proof passed')
