from __future__ import annotations

import csv
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.official_inputs import load_official_inputs


def _write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _svg_header(width, height, title):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-family="Arial" font-size="18" font-weight="bold">{html.escape(title)}</text>',
    ]


def _write_q1_evidence(result):
    directory = ROOT / "questao_01" / "resultados"
    benchmark = result["benchmark"]
    _write_csv(
        directory / "brute_force_vs_ga.csv",
        ["algorithm", "sku_count", "cash", "gap_percent"],
        [
            {"algorithm": "Brute Force", "sku_count": benchmark["sku_count"],
             "cash": benchmark["brute_force_cash"], "gap_percent": 0},
            {"algorithm": "Genetic Algorithm", "sku_count": benchmark["sku_count"],
             "cash": benchmark["ga_cash"], "gap_percent": benchmark["ga_gap_percent"]},
        ],
    )
    comparison_rows = []
    for run in result["ga_comparison"]:
        config = run["configuration"]
        comparison_rows.append({
            "name": config["name"],
            "population_size": config["population_size"],
            "generations": config["generations"],
            "mutation_rate": config["mutation_rate"],
            "cash": run["cash"],
        })
    _write_csv(
        directory / "ga_configuration_comparison.csv",
        ["name", "population_size", "generations", "mutation_rate", "cash"],
        comparison_rows,
    )
    _write_csv(
        directory / "greedy_before_after.csv",
        list(result["greedy_before_after"][0]) if result["greedy_before_after"] else
        ["sku", "price", "units_before", "cash_before", "units_after",
         "cash_after_net_of_promotion", "inventory_remaining", "promotion_spend"],
        result["greedy_before_after"],
    )

    histories = [run["fitness_history"] for run in result["ga_comparison"]]
    width, height, left, right, top, bottom = 900, 480, 75, 30, 65, 65
    chart = _svg_header(width, height, "Q1 - Genetic algorithm convergence")
    maximum = max(max(history, default=0) for history in histories) or 1
    plot_w, plot_h = width - left - right, height - top - bottom
    for tick in range(5):
        y_value = maximum * tick / 4
        y = top + plot_h * (1 - tick / 4)
        chart.append(f'<line x1="{left}" y1="{y}" x2="{width-right}" y2="{y}" stroke="#dddddd"/>')
        chart.append(f'<text x="{left-8}" y="{y+4}" text-anchor="end" font-family="Arial" font-size="11">{y_value:.0f}</text>')
    colors = ["#1769aa", "#e67e22"]
    for index, (run, history) in enumerate(zip(result["ga_comparison"], histories)):
        if not history:
            continue
        points = []
        for gen, fitness in enumerate(history):
            x = left + plot_w * gen / max(1, len(history) - 1)
            y = top + plot_h * (1 - fitness / maximum)
            points.append(f"{x:.1f},{y:.1f}")
        chart.append(f'<polyline fill="none" stroke="{colors[index % len(colors)]}" stroke-width="2" points="{" ".join(points)}"/>')
        chart.append(f'<text x="{left+10}" y="{top+20+index*18}" font-family="Arial" font-size="12" fill="{colors[index % len(colors)]}">{html.escape(run["configuration"]["name"])}</text>')
    chart.append(f'<text x="{left+plot_w/2}" y="{height-20}" text-anchor="middle" font-family="Arial" font-size="12">Generation</text>')
    chart.append('</svg>')
    (directory / "ga_fitness_convergence.svg").write_text("\n".join(chart), encoding="utf-8")


def _write_q2_evidence(result):
    directory = ROOT / "questao_02" / "resultados"
    _write_csv(
        directory / "candidate_policy_comparison.csv",
        ["candidate", "probability_all_obligations_on_time", "p10_final_cash",
         "expected_final_cash", "selected"],
        [
            {
                "candidate": candidate["name"],
                "probability_all_obligations_on_time": candidate[
                    "probability_all_obligations_on_time"
                ],
                "p10_final_cash": candidate["p10_final_cash"],
                "expected_final_cash": candidate["expected_final_cash"],
                "selected": candidate["name"] == result["selected_policy"],
            }
            for candidate in result["candidate_policy_scores"]
        ],
    )
    samples = result["validation"]["final_cash_samples"]
    _write_csv(
        directory / "validation_cash_samples.csv",
        ["scenario", "final_cash"],
        ({"scenario": i + 1, "final_cash": value} for i, value in enumerate(samples)),
    )
    item_rows = []
    for week_plan in result["weekly_policy"]:
        promo_by_sku = {
            allocation["sku"]: allocation
            for allocation in next(
                (entry for entry in result["weekly_promotions"] if entry["week"] == week_plan["week"]),
                {"allocations": []},
            )["allocations"]
        }
        for decision in week_plan["items"]:
            item_rows.append({
                "week": week_plan["week"],
                "sku": decision["sku"],
                "price_multiplier": decision["multiplier"],
                "expected_units": decision["expected_units"],
                "stock_start": decision["stock_start"],
                "stock_end_before_promotion": decision["stock_end"],
                "promotion_units": promo_by_sku.get(decision["sku"], {}).get("extra_units", 0),
                "expected_cash": decision["expected_cash"],
            })
    _write_csv(
        directory / "weekly_trajectory.csv",
        ["week", "sku", "price_multiplier", "expected_units", "stock_start",
         "stock_end_before_promotion", "promotion_units", "expected_cash"],
        item_rows,
    )

    cash_min, cash_max = min(samples), max(samples)
    width, height, left, right, top, bottom = 900, 460, 80, 35, 60, 65
    chart = _svg_header(width, height, "Q2 - Independent validation final cash distribution")
    bins = 30
    span = max(1.0, cash_max - cash_min)
    counts = [0] * bins
    for value in samples:
        index = min(bins - 1, int((value - cash_min) / span * bins))
        counts[index] += 1
    max_count = max(counts) or 1
    plot_w, plot_h = width - left - right, height - top - bottom
    bar_w = plot_w / bins
    for i, count in enumerate(counts):
        bar_h = plot_h * count / max_count
        x = left + i * bar_w
        y = top + plot_h - bar_h
        chart.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w-1:.1f}" height="{bar_h:.1f}" fill="#4b86b4"/>')
    mean_cash = result["validation"]["expected_final_cash"]
    p10_cash = result["validation"]["p10_final_cash"]
    for value, color, label in ((p10_cash, "#c0392b", "P10"), (mean_cash, "#138a5b", "Mean")):
        x = left + (value - cash_min) / span * plot_w
        chart.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+plot_h}" stroke="{color}" stroke-width="2"/>')
        chart.append(f'<text x="{x+4:.1f}" y="{top+14}" font-family="Arial" font-size="12" fill="{color}">{label}: {value:.0f}</text>')
    chart.append(f'<text x="{left+plot_w/2}" y="{height-20}" text-anchor="middle" font-family="Arial" font-size="12">Final cash (BRL)</text>')
    chart.append('</svg>')
    (directory / "cash_distribution.svg").write_text("\n".join(chart), encoding="utf-8")

    items, _, _ = load_official_inputs("q2")
    prices = {item["sku"]: item["preco_atual"] for item in items}
    representative = sorted(items, key=lambda item: item["estoque_inicial"], reverse=True)[:3]
    width, height, left, right, top, bottom = 1000, 620, 80, 30, 60, 70
    chart = _svg_header(width, height, "Q2 - Weekly price and stock trajectory (representative SKUs)")
    chart.append('<text x="500" y="52" text-anchor="middle" font-family="Arial" font-size="12">Top panels: price; bottom panels: remaining stock</text>')
    colors = ["#1769aa", "#e67e22", "#138a5b"]
    plot_w = width - left - right
    price_top, price_h = 85, 180
    stock_top, stock_h = 350, 180
    for index, item in enumerate(representative):
        sku = item["sku"]
        decisions = [next(row for row in week["items"] if row["sku"] == sku) for week in result["weekly_policy"]]
        max_price = max((item["preco_atual"] * row["multiplier"] for row in decisions if row["multiplier"]), default=1)
        max_stock = item["estoque_inicial"] or 1
        price_points, stock_points = [], []
        for i, row in enumerate(decisions):
            x = left + plot_w * i / max(1, len(decisions) - 1)
            price = item["preco_atual"] * row["multiplier"] if row["multiplier"] else 0
            price_y = price_top + price_h * (1 - price / max_price)
            stock_y = stock_top + stock_h * (1 - row["stock_end"] / max_stock)
            price_points.append(f"{x:.1f},{price_y:.1f}")
            stock_points.append(f"{x:.1f},{stock_y:.1f}")
        color = colors[index % len(colors)]
        chart.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{" ".join(price_points)}"/>')
        chart.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{" ".join(stock_points)}"/>')
        chart.append(f'<text x="{left+index*150}" y="{price_top-8}" font-family="Arial" font-size="12" fill="{color}">{sku}</text>')
    for i in range(12):
        x = left + plot_w * i / 11
        chart.append(f'<text x="{x:.1f}" y="{stock_top+stock_h+22}" text-anchor="middle" font-family="Arial" font-size="10">{i+1}</text>')
    chart.append(f'<text x="{left+plot_w/2}" y="{height-20}" text-anchor="middle" font-family="Arial" font-size="12">Week</text>')
    chart.append('</svg>')
    (directory / "weekly_price_stock.svg").write_text("\n".join(chart), encoding="utf-8")


def _write_architecture():
    path = ROOT / "docs" / "arquitetura.svg"
    path.parent.mkdir(parents=True, exist_ok=True)
    parts = _svg_header(1000, 440, "Checkpoint 6 - Integrated algorithm flows")
    boxes = [
        (35, 105, "Q1 official catalog/config", "SHA-256 validated"),
        (275, 105, "Brute Force", "6-SKU exact benchmark"),
        (515, 105, "Genetic Algorithm", "reduced + full catalog"),
        (755, 105, "Greedy", "promo policy + accounting"),
        (35, 285, "Q2 official catalog/config", "SHA-256 validated"),
        (275, 285, "Monte Carlo", "price estimates / scenarios"),
        (515, 285, "Risk-aware DP", "week + stock + cash bucket"),
        (755, 285, "Greedy + validation", "weekly promos / independent MC"),
    ]
    for x, y, title, subtitle in boxes:
        parts.append(f'<rect x="{x}" y="{y}" width="205" height="80" rx="8" fill="#eaf2f8" stroke="#1769aa" stroke-width="2"/>')
        parts.append(f'<text x="{x+102}" y="{y+32}" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold">{html.escape(title)}</text>')
        parts.append(f'<text x="{x+102}" y="{y+56}" text-anchor="middle" font-family="Arial" font-size="11">{html.escape(subtitle)}</text>')
    for y in (145, 325):
        for x1, x2 in ((240, 275), (480, 515), (720, 755)):
            parts.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>')
    parts.insert(1, '<defs><marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0,10 3.5,0 7" fill="#333"/></marker></defs>')
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def main():
    q1 = json.loads((ROOT / "questao_01/resultados/resultado_q1.json").read_text(encoding="utf-8"))
    q2 = json.loads((ROOT / "questao_02/resultados/resultado_q2.json").read_text(encoding="utf-8"))
    _write_q1_evidence(q1)
    _write_q2_evidence(q2)
    _write_architecture()
    print("Generated Q1/Q2 evidence tables, SVG charts, and docs/arquitetura.svg")


if __name__ == "__main__":
    main()
