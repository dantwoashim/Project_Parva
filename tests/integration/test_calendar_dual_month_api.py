from datetime import date

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _payload(response):
    body = response.json()
    return body['data'] if isinstance(body, dict) and 'data' in body else body


def test_dual_month_returns_dual_calendar_rows():
    response = client.get('/v3/api/calendar/dual-month', params={'year': 2026, 'month': 2})
    assert response.status_code == 200
    payload = _payload(response)
    assert payload['year'] == 2026
    assert payload['month'] == 2
    assert isinstance(payload['days'], list)
    assert len(payload['days']) in (28, 29)

    sample = payload['days'][0]
    assert sample['gregorian']['iso'].startswith('2026-02-')
    assert 'weekday' in sample['gregorian']
    assert sample['bikram_sambat']['formatted']
    assert isinstance(sample['bikram_sambat']['year'], int)


def test_dual_month_rejects_year_outside_dynamic_window():
    outside_year = date.today().year - 201
    response = client.get('/v3/api/calendar/dual-month', params={'year': outside_year, 'month': 1})
    assert response.status_code == 400
    assert '±200 year' in response.json()['detail']
