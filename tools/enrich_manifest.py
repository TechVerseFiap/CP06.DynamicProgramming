from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.official_inputs import enrich_manifest, validate_official_manifest


def main():
    manifest = enrich_manifest()
    verified = validate_official_manifest()
    print(
        f"Enriched and verified instance {verified['id_instancia']}: "
        f"Q1={manifest['quantidade_skus']['q1']} SKUs, "
        f"Q2={manifest['quantidade_skus']['q2']} SKUs"
    )


if __name__ == "__main__":
    main()
