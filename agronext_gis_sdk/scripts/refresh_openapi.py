"""Refresh `tests/openapi.json` from the API this SDK wraps.

Run it in the API's environment — it builds the API app to ask it for its
OpenAPI document, which is the one thing the SDK must never import at runtime:

    cd agronext_gis_api
    uv run python ../agronext_gis_sdk/scripts/refresh_openapi.py

Then run the SDK's tests: `tests/test_contract.py` fails on every route, query
parameter, field or enum value the SDK no longer matches.
"""

import json
from pathlib import Path

from agronext_gis_api.main import create_app
from agronext_gis_api.settings import ApiSettings, Environment

SNAPSHOT = Path(__file__).resolve().parent.parent / "tests" / "openapi.json"


def main() -> None:
    app = create_app(ApiSettings(environment=Environment.LOCAL))
    SNAPSHOT.write_text(json.dumps(app.openapi(), indent=1, sort_keys=True) + "\n")
    print(f"wrote {SNAPSHOT}")


if __name__ == "__main__":
    main()
