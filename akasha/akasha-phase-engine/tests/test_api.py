"""
tests/test_api.py — Basic API tests for CI
"""
import pytest
import sys
import os

from akasha_phase_engine.app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


def test_stats(client):
    r = client.get('/api/stats')
    assert r.status_code == 200
    d = r.get_json()
    assert d['total_phases'] >= 10
    assert d['total_transitions'] >= 5
    assert d['total_materials'] >= 20


def test_phases_all(client):
    r = client.get('/api/phases')
    assert r.status_code == 200
    d = r.get_json()
    assert d['count'] >= 10
    names = [p['name'] for p in d['phases']]
    assert 'Topological Insulator' in names
    assert 'BCS Superconductor' in names


def test_phases_filter_topological(client):
    r = client.get('/api/phases?topological=true')
    assert r.status_code == 200
    d = r.get_json()
    for p in d['phases']:
        assert p['topology']['has_topological_order'] is True


def test_phases_filter_equilibrium(client):
    r = client.get('/api/phases?equilibrium=false')
    assert r.status_code == 200
    d = r.get_json()
    for p in d['phases']:
        assert p['dynamics']['equilibrium'] is False


def test_phases_filter_dimensionality(client):
    r = client.get('/api/phases?dimensionality=2')
    assert r.status_code == 200
    d = r.get_json()
    for p in d['phases']:
        assert p['dimensionality'] == 2




def test_phase_detail(client):
    r = client.get('/api/phases/Topological Insulator')
    assert r.status_code == 200
    d = r.get_json()
    assert d['name'] == 'Topological Insulator'
    assert d['category'] == 'Topological'
    assert d['dimensionality'] == 3
    assert d['topology']['has_topological_order'] is True
    assert d['topology']['edge_states'] is True
    assert len(d['materials']) >= 1


def test_phase_detail_not_found(client):
    r = client.get('/api/phases/Unobtainium')
    assert r.status_code == 404

def test_transitions(client):
    r = client.get('/api/transitions')
    assert r.status_code == 200
    d = r.get_json()
    assert d['count'] >= 5
    froms = [t['from'] for t in d['transitions']]
    assert 'Ferromagnet' in froms


def test_gaps(client):
    r = client.get('/api/gaps')
    assert r.status_code == 200
    d = r.get_json()
    assert d['summary']['total_evaluated'] > 100
    assert d['summary']['forbidden'] > 0
    assert d['summary']['candidate_gaps'] > 0
    assert len(d['predictions']) >= 5
    assert len(d['forbidden_zones']) >= 3


def test_materials_post(client):
    coord = {
        "dimensionality": 3,
        "symmetry_breaking": "none",
        "topological": "Z2",
        "dynamics": "equilibrium",
        "anyons": "none",
        "edge_states": True,
        "bulk_gap": True,
        "long_range_entanglement": False,
    }
    r = client.post('/api/materials',
                    json=coord,
                    content_type='application/json')
    assert r.status_code == 200
    d = r.get_json()
    assert len(d['requirements']) > 0
    assert len(d['candidates']) > 0


def test_materials_bad_input(client):
    r = client.post('/api/materials',
                    json={"symmetry_breaking": "invalid_value"},
                    content_type='application/json')
    assert r.status_code == 400


def test_enum_options(client):
    r = client.get('/api/enum_options')
    assert r.status_code == 200
    d = r.get_json()
    assert 'dimensionality' in d
    assert 'topological' in d
    assert 3 in d['dimensionality']


def test_neighbors(client):
    r = client.get('/api/neighbors/Ferromagnet')
    assert r.status_code == 200
    d = r.get_json()
    assert d['phase'] == 'Ferromagnet'


def test_pipeline_no_key(client):
    r = client.post('/api/pipeline',
                    json={},
                    content_type='application/json')
    assert r.status_code == 400
    d = r.get_json()
    assert 'error' in d


def test_index(client):
    r = client.get('/')
    assert r.status_code == 200
