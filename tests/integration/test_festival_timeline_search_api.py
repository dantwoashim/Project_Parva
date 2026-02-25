from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _payload(response):
    body = response.json()
    return body['data'] if isinstance(body, dict) and 'data' in body else body


def _flatten(groups):
    rows = []
    for group in groups:
        rows.extend(group.get('items', []))
    return rows


def test_timeline_search_filters_results_and_includes_bs_dates():
    response = client.get(
        '/v3/api/festivals/timeline',
        params={
            'from': '2026-09-01',
            'to': '2026-12-01',
            'quality_band': 'all',
            'search': 'dashain',
        },
    )
    assert response.status_code == 200
    payload = _payload(response)
    rows = _flatten(payload.get('groups', []))
    assert rows, 'Expected timeline search to return at least one festival for dashain window.'

    for row in rows:
        assert 'bs_start' in row
        assert 'bs_end' in row
        assert row['bs_start']['formatted']


def test_timeline_search_with_unknown_term_returns_empty_groups():
    response = client.get(
        '/v3/api/festivals/timeline',
        params={
            'from': '2026-09-01',
            'to': '2026-12-01',
            'quality_band': 'all',
            'search': 'zzznomatchfestival',
        },
    )
    assert response.status_code == 200
    payload = _payload(response)
    assert payload['total'] == 0
    assert payload['groups'] == []
