from scripts.release import check_route_inventory


def test_route_inventory_has_no_alias_gaps():
    inventory = check_route_inventory._build_inventory()

    assert inventory["canonical_prefix"] == "/v3/api"
    assert inventory["compat_prefix"] == "/api"
    assert inventory["v3_count"] >= inventory["compat_count"]
    assert inventory["alias_gaps"] == []
