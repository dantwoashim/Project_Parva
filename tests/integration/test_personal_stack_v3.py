from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_personal_panchanga_v3_fields():
    resp = client.get('/v3/api/personal/panchanga', params={'date': '2026-02-15'})
    assert resp.status_code == 200
    body = resp.json()
    assert 'bikram_sambat' in body
    assert 'tithi' in body
    assert 'nakshatra' in body
    assert 'yoga' in body
    assert 'karana' in body
    assert 'vaara' in body
    assert 'calculation_trace_id' in body
    assert body['method_profile'] == 'personal_panchanga_v2_udaya'
    assert body['quality_band'] in {'validated', 'gold'}
    assert body['assumption_set_id']
    assert body['advisory_scope'] == 'ritual_planning'


def test_muhurta_returns_named_slots():
    resp = client.get('/v3/api/muhurta', params={'date': '2026-02-15'})
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body.get('muhurtas'), list)
    assert len(body['muhurtas']) == 30
    assert body['muhurtas'][0]['name']
    assert body['muhurtas'][0]['duration_minutes'] > 0
    assert len(body['day_muhurtas']) == 15
    assert len(body['night_muhurtas']) == 15
    assert len(body['hora']['day']) == 12
    assert len(body['hora']['night']) == 12
    assert len(body['chaughadia']['day']) == 8
    assert len(body['chaughadia']['night']) == 8
    assert 'tara_bala' in body
    assert body['method_profile'] == 'muhurta_v2_hora_chaughadia_tarabala'
    assert body['quality_band'] in {'beta', 'validated', 'gold'}


def test_rahu_kalam_changes_by_weekday():
    sunday = client.get('/v3/api/muhurta/rahu-kalam', params={'date': '2026-02-15'})
    monday = client.get('/v3/api/muhurta/rahu-kalam', params={'date': '2026-02-16'})
    assert sunday.status_code == 200
    assert monday.status_code == 200
    assert sunday.json()['rahu_kalam']['segment'] != monday.json()['rahu_kalam']['segment']


def test_muhurta_auspicious_ranked_output():
    resp = client.get(
        '/v3/api/muhurta/auspicious',
        params={
            'date': '2026-02-15',
            'type': 'vivah',
            'birth_nakshatra': '7',
            'assumption_set': 'np-mainstream-v2',
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body['method_profile'] == 'muhurta_v2_hora_chaughadia_tarabala'
    assert body['assumption_set_id'] == 'np-mainstream-v2'
    assert isinstance(body.get('ranked_muhurtas'), list)
    assert body['best_window']['score'] >= body['ranked_muhurtas'][-1]['score']
    assert 'tara_bala' in body



def test_kundali_returns_12_houses_and_navagraha():
    resp = client.get(
        '/v3/api/kundali',
        params={'datetime': '2026-02-15T06:30:00+05:45', 'lat': '27.7172', 'lon': '85.3240'},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body.get('houses', [])) == 12
    assert len(body.get('grahas', {})) == 9
    assert 'dasha' in body
    assert isinstance(body.get('aspects'), list)
    assert isinstance(body.get('yogas'), list)
    assert isinstance(body.get('doshas'), list)
    assert isinstance(body.get('consistency_checks'), list)
    assert body['dasha']['total_major_periods'] == 9
    assert len(body['dasha']['timeline'][0]['antar_dasha']) == 9
    assert body['method_profile'] == 'kundali_v2_aspects_dasha'
    assert body['assumption_set_id'] == 'np-kundali-v2'
    assert body['quality_band'] in {'validated', 'gold'}
    assert body['advisory_scope'] == 'astrology_assist'


def test_kundali_invalid_datetime_returns_400():
    resp = client.get('/v3/api/kundali', params={'datetime': 'not-a-datetime'})
    assert resp.status_code == 400


def test_invalid_coordinates_fallback_with_warning():
    resp = client.get('/v3/api/muhurta', params={'date': '2026-02-15', 'lat': '999', 'lon': 'xyz'})
    assert resp.status_code == 200
    body = resp.json()
    assert body['location']['latitude'] == 27.7172
    assert body['location']['longitude'] == 85.324
    assert body.get('warnings')
