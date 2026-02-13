"""End-to-end engine flow checks (Week 12)."""

from fastapi.testclient import TestClient

from app.main import app


def test_e2e_calendar_today_pipeline_has_metadata_and_npt_sunrise():
    client = TestClient(app)
    response = client.get('/api/calendar/today')
    assert response.status_code == 200
    assert response.headers['X-Parva-Engine'] == 'v2'

    data = response.json()
    tithi = data['tithi']

    assert tithi['method'] in {'ephemeris_udaya', 'instantaneous'}
    assert tithi['reference_time'] in {'sunrise', 'instantaneous'}
    if tithi['sunrise_used']:
        assert tithi['sunrise_used'].endswith('+05:45')


def test_e2e_calendar_tithi_endpoint_pipeline():
    client = TestClient(app)
    response = client.get('/api/calendar/tithi', params={'date': '2026-02-15'})
    assert response.status_code == 200

    data = response.json()
    assert data['engine_version'] == 'v2'
    assert 'location' in data
    assert 'tithi' in data

    t = data['tithi']
    assert 1 <= t['display_number'] <= 15
    assert t['paksha'] in {'shukla', 'krishna'}
