import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app

    return TestClient(app)


def test_muhurta_heatmap_supports_creative_focus(client):
    response = client.get('/api/muhurta/heatmap', params={
        'date': '2026-03-16',
        'lat': '27.7172',
        'lon': '85.3240',
        'tz': 'Asia/Kathmandu',
        'type': 'creative_focus',
    })

    assert response.status_code == 200
    data = response.json()
    assert 'blocks' in data
    assert data['method_profile'] == 'muhurta_heatmap_v1'


def test_festival_timeline_includes_facets_and_sort(client):
    response = client.get('/api/festivals/timeline', params={
        'from': '2026-10-01',
        'to': '2026-12-31',
        'sort': 'popular',
    })

    assert response.status_code == 200
    data = response.json()
    assert data['sort'] == 'popular'
    assert 'facets' in data
    assert {'categories', 'months', 'regions'} <= set(data['facets'].keys())


def test_personal_context_endpoint_is_resilient_to_optional_fields(client):
    response = client.get('/api/personal/context', params={
        'date': '2026-03-16',
        'lat': '27.7172',
        'lon': '85.3240',
        'tz': 'Asia/Kathmandu',
    })

    assert response.status_code == 200
    data = response.json()
    assert data['place_title']
    assert data['context_title']
    assert 'upcoming_reminders' in data
    assert 'temperature_note' in data
