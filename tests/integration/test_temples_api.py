from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_temples_list_returns_mappable_locations():
    response = client.get('/v3/api/temples')
    assert response.status_code == 200

    payload = response.json()
    assert payload['total'] > 0
    assert isinstance(payload['temples'], list)

    sample = payload['temples'][0]
    assert 'coordinates' in sample
    assert isinstance(sample['coordinates']['lat'], (int, float))
    assert isinstance(sample['coordinates']['lng'], (int, float))


def test_temples_filtered_by_festival_dashain():
    response = client.get('/v3/api/temples', params={'festival': 'dashain'})
    assert response.status_code == 200

    payload = response.json()
    assert payload['total'] > 0
    assert any('dashain' in temple.get('festivals', []) for temple in payload['temples'])


def test_temple_roles_for_festival_include_coordinates():
    response = client.get('/v3/api/temples/for-festival/dashain')
    assert response.status_code == 200

    payload = response.json()
    assert payload['festival_id'] == 'dashain'
    assert payload['total'] > 0

    sample = payload['temples'][0]
    assert 'temple' in sample
    assert 'role' in sample
    assert isinstance(sample['temple']['coordinates']['lat'], (int, float))
    assert isinstance(sample['temple']['coordinates']['lng'], (int, float))
