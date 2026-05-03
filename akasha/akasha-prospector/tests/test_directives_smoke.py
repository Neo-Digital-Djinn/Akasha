from akasha_prospector.analysis.directives import generate_directives

def test_generate_directives():
    payload = generate_directives({"event_count":5}, {"burst_count":1})
    assert payload["directive_count"] >= 1
