from scripts.release import check_documented_routes


def test_documented_routes_parser_extracts_method_and_path():
    routes = check_documented_routes._documented_routes(
        "\n".join(
            [
                "- `GET /calendar/today`",
                "- `GET /calendar/convert?date=YYYY-MM-DD`",
                "not a route",
            ]
        )
    )

    assert routes == [
        check_documented_routes.DocumentedRoute(method="GET", path="/calendar/today"),
        check_documented_routes.DocumentedRoute(method="GET", path="/calendar/convert?date=YYYY-MM-DD"),
    ]


def test_documented_route_canonicalization_prefixes_v3_api():
    route = check_documented_routes.DocumentedRoute(method="GET", path="/public/artifacts/manifest")
    assert route.canonical_path == "/v3/api/public/artifacts/manifest"
    assert route.request_path == "/v3/api/public/artifacts/manifest"


def test_documented_routes_check_passes_for_current_reference_doc():
    assert check_documented_routes.main() == 0
