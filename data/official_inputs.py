from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REQUIRED_COLUMNS = {
    "q1": {
        "sku", "categoria", "custo_unitario", "preco_atual", "estoque",
        "demanda_base_90d", "elasticidade", "taxa_marketplace",
        "custo_logistico", "idade_estoque_dias",
    },
    "q2": {
        "sku", "categoria", "custo_unitario", "preco_atual",
        "estoque_inicial", "demanda_base_semanal", "elasticidade",
        "taxa_marketplace", "custo_logistico_base", "preco_concorrente_base",
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_official_manifest(data_dir: Path = ROOT) -> dict:
    """Verify all official generator outputs and their combined instance ID."""
    data_dir = Path(data_dir)
    manifest_path = data_dir / "manifesto_dados.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Official data manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    group = manifest.get("grupo")
    if not group:
        raise ValueError("Manifest does not identify the group")
    expected_files = (
        f"q1_catalogo_{group}.csv",
        f"q1_config_{group}.json",
        f"q2_catalogo_{group}.csv",
        f"q2_config_{group}.json",
    )
    hashes = manifest.get("arquivos")
    if not isinstance(hashes, dict):
        raise ValueError("Manifest has no per-file SHA-256 map ('arquivos')")

    missing = [name for name in expected_files if not (data_dir / name).is_file()]
    if missing:
        raise FileNotFoundError("Official generated input(s) missing: " + ", ".join(missing))

    for name in expected_files:
        expected = hashes.get(name)
        if not expected:
            raise ValueError(f"Manifest has no SHA-256 for {name}")
        actual = _sha256(data_dir / name)
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch for {name}: expected {expected}, got {actual}")

    combined = hashlib.sha256(
        "".join(hashes[name] for name in sorted(expected_files)).encode("utf-8")
    ).hexdigest()
    if manifest.get("sha256_conjunto") != combined:
        raise ValueError("Combined input hash does not match manifest sha256_conjunto")
    if manifest.get("id_instancia") != combined[:12]:
        raise ValueError("Instance ID does not match the combined input hash")
    group_digits = "".join(character for character in group if character.isdigit())
    if not group_digits:
        raise ValueError("Manifest group code must contain a numeric identifier")
    expected_seed = int(group_digits) * 1000 + int(manifest.get("seed_base", -1))
    if manifest.get("seed_final") != expected_seed:
        raise ValueError("Manifest seed_final does not match group number and seed_base")
    for question in ("q1", "q2"):
        if question not in manifest.get("quantidade_skus", {}):
            raise ValueError(f"Manifest is missing {question} SKU count; run tools/enrich_manifest.py")
        if question not in manifest.get("metas_financeiras", {}):
            raise ValueError(f"Manifest is missing {question} financial targets; run tools/enrich_manifest.py")
    return manifest


def _read_catalog(path: Path, required_columns: set[str]) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        missing = required_columns - columns
        if missing:
            raise ValueError(f"{path.name} is missing columns: {', '.join(sorted(missing))}")
        rows = []
        for row in reader:
            converted = {}
            for key, value in row.items():
                if value is None or value == "":
                    converted[key] = value
                    continue
                try:
                    number = float(value)
                except ValueError:
                    converted[key] = value
                else:
                    converted[key] = int(number) if number.is_integer() else number
            rows.append(converted)
    if not rows:
        raise ValueError(f"Official catalog is empty: {path}")
    return rows


def load_official_inputs(question: str, data_dir: Path = ROOT) -> tuple[list[dict], dict, dict]:
    """Load one official CSV/config pair after checking every manifest hash."""
    question = question.lower()
    if question not in {"q1", "q2"}:
        raise ValueError("question must be 'q1' or 'q2'")
    data_dir = Path(data_dir)
    manifest = validate_official_manifest(data_dir)
    group = manifest.get("grupo")
    catalog_path = data_dir / f"{question}_catalogo_{group}.csv"
    config_path = data_dir / f"{question}_config_{group}.json"
    required = REQUIRED_COLUMNS[question]
    catalog = _read_catalog(catalog_path, required)
    config = json.loads(config_path.read_text(encoding="utf-8"))

    if config.get("grupo") != group:
        raise ValueError(f"{config_path.name} group does not match the manifest")
    for key in ("seed_base", "seed_final"):
        if config.get(key) != manifest.get(key):
            raise ValueError(f"{config_path.name} {key} does not match the manifest")
    return catalog, config, manifest


def enrich_manifest(data_dir: Path = ROOT) -> dict:
    """Add deterministic SKU counts and financial targets without editing inputs."""
    data_dir = Path(data_dir)
    manifest_path = data_dir / "manifesto_dados.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hashes = manifest.get("arquivos", {})
    derived = {}
    for question in ("q1", "q2"):
        group = manifest["grupo"]
        catalog_name = f"{question}_catalogo_{group}.csv"
        config_name = f"{question}_config_{group}.json"
        if hashes.get(catalog_name) != _sha256(data_dir / catalog_name):
            raise ValueError(f"Official catalog hash mismatch: {catalog_name}")
        if hashes.get(config_name) != _sha256(data_dir / config_name):
            raise ValueError(f"Official config hash mismatch: {config_name}")
        with (data_dir / catalog_name).open("r", encoding="utf-8-sig", newline="") as source:
            sku_count = sum(1 for _ in csv.DictReader(source))
        config = json.loads((data_dir / config_name).read_text(encoding="utf-8"))
        if question == "q1":
            targets = {
                "meta_caixa_90d": config["meta_caixa_90d"],
                "divida_total_90d": config["divida_total_90d"],
            }
        else:
            targets = {
                "caixa_inicial": config["caixa_inicial"],
                "dividas": config["dividas"],
            }
        derived[question] = (sku_count, targets)

    manifest["quantidade_skus"] = {
        question: values[0] for question, values in derived.items()
    }
    manifest["metas_financeiras"] = {
        question: values[1] for question, values in derived.items()
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
