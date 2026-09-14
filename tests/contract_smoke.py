"""Run against the application repository's local SDK contract fixture."""
import io
import os
from renderingvideo import Client
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
print('Python SDK user API contracts passed')
