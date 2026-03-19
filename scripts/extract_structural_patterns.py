#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import argparse
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def parse_groups(config_str: str):
    groups = []
    for g in str(config_str).split("_"):
        groups.append(set(g.split("-")))
    return groups


def knee_max_distance(rank, score):
    x = np.asarray(rank, dtype=float)
    y = np.asarray(score, dtype=float)

    x_n = (x - x.min()) / (x.max() - x.min() + 1e-12)
    y_n = (y - y.min()) / (y.max() - y.min() + 1e-12)

    p1 = np.array([x_n[0], y_n[0]])
    p2 = np.array([x_n[-1], y_n[-1]])
    v = p2 - p1
    v_norm = np.linalg.norm(v) + 1e-12

    pts = np.stack([x_n, y_n], axis=1)
    dist = np.abs(np.cross(v, pts - p1)) / v_norm

    idx = int(np.argmax(dist[1:-1]) + 1)
    return idx


def compute_pair_probs(config_series: pd.Series, services: list[str]):
    pair_counts = {(a, b): 0 for a, b in combinations(services, 2)}
    n = len(config_series)

    services_set = set(services)

    for cfg in config_series.astype(str):
        groups = parse_groups(cfg)
        for g in groups:
            g = [s for s in g if s in services_set]
            if len(g) < 2:
                continue
            for a, b in combinations(sorted(g), 2):
                pair_counts[(a, b)] += 1

    rows = []
    for (a, b), c in pair_counts.items():
        p = c / n if n > 0 else 0.0
        rows.append((a, b, p))

    out = (
        pd.DataFrame(rows, columns=["a", "b", "p"])
        .sort_values("p", ascending=False)
        .reset_index(drop=True)
    )
    return out


def probs_to_matrix(pairs_df: pd.DataFrame, services: list[str]):
    idx = {s: i for i, s in enumerate(services)}
    n = len(services)
    M = np.zeros((n, n), dtype=float)
    np.fill_diagonal(M, 1.0)

    for _, r in pairs_df.iterrows():
        i, j = idx[r["a"]], idx[r["b"]]
        M[i, j] = r["p"]
        M[j, i] = r["p"]

    return M


def plot_heatmap(M, services, title, outpath):
    plt.figure(figsize=(8.5, 7))

    im = plt.imshow(M, vmin=0, vmax=1)

    cbar = plt.colorbar(im)
    cbar.set_label("Co-location Probability P(A, B)", fontsize=12)
    cbar.ax.tick_params(labelsize=12)

    plt.rcParams.update({
        "font.size": 12,
        "axes.titlesize": 12,
        "axes.labelsize": 12
    })

    plt.xticks(range(len(services)), services, rotation=90, fontsize=10)
    plt.yticks(range(len(services)), services, fontsize=10)
    plt.title(title, fontsize=12)

    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def summarize_patterns(pairs_df, label, hi=0.8, lo=0.2, max_list=30):
    strong_together = pairs_df[pairs_df["p"] >= hi].copy()
    strong_apart = pairs_df[pairs_df["p"] <= lo].copy()

    lines = []
    lines.append(f"## {label}\n")

    lines.append(f"**Recurring co-location patterns (p ≥ {hi:.2f}):**")
    if strong_together.empty:
        lines.append("- (none)")
    else:
        st = strong_together.sort_values("p", ascending=False).head(max_list)
        for _, r in st.iterrows():
            lines.append(f"- ({r['a']}, {r['b']}) — p={r['p']:.3f}")
        lines.append(f"\nTotal: {len(strong_together)} pairs\n")

    lines.append(f"**Strong separation patterns (p ≤ {lo:.2f}):**")
    if strong_apart.empty:
        lines.append("- (none)")
    else:
        sa = strong_apart.sort_values("p", ascending=True).head(max_list)
        for _, r in sa.iterrows():
            lines.append(f"- ({r['a']}, {r['b']}) — p={r['p']:.3f}")
        lines.append(f"\nTotal: {len(strong_apart)} pairs\n")

    return "\n".join(lines)


def broken_from_top(pairs_top, pairs_other, hi=0.8):
    strong_top = pairs_top[pairs_top["p"] >= hi].copy()
    merged = (
        strong_top
        .merge(pairs_other, on=["a", "b"], how="left", suffixes=("_top", "_other"))
        .fillna(0.0)
    )
    merged["breaks"] = merged["p_other"] < hi
    broken = (
        merged[merged["breaks"]]
        .sort_values("p_top", ascending=False)
        .reset_index(drop=True)
    )
    return broken


def main():
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    data_dir = repo_root / "data" / "processed"

    default_pareto_csv = data_dir / "pareto_2d_alpha_05.csv"
    default_scores_csv = data_dir / "exhaustive_configurations_alpha_05.csv"
    default_outdir = data_dir

    ap = argparse.ArgumentParser()
    ap.add_argument("--pareto_csv", default=str(default_pareto_csv))
    ap.add_argument("--scores_csv", default=str(default_scores_csv))
    ap.add_argument("--outdir", default=str(default_outdir))
    ap.add_argument("--hi", type=float, default=0.8)
    ap.add_argument("--lo", type=float, default=0.2)
    ap.add_argument(
        "--tail_pct",
        type=float,
        default=1.0,
        help="Percentage of worst-ranked global configurations (e.g., 1.0 = 1%)"
    )
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # --- Pareto: knee and mapping to global ranking
    pareto = pd.read_csv(args.pareto_csv)
    score_col = "score_alpha_05" if "score_alpha_05" in pareto.columns else "score"

    if "position" not in pareto.columns:
        raise RuntimeError("pareto_csv must contain the column 'position'.")

    pareto_sorted = pareto.sort_values(score_col, ascending=True).reset_index(drop=True).copy()
    pareto_sorted["pareto_rank"] = np.arange(1, len(pareto_sorted) + 1)

    pr = pareto_sorted["pareto_rank"].to_numpy()
    ps = pareto_sorted[score_col].to_numpy()

    knee_idx = knee_max_distance(pr, ps)
    knee_pareto_rank = int(pareto_sorted.loc[knee_idx, "pareto_rank"])
    knee_global_pos = int(pareto_sorted.loc[knee_idx, "position"])
    last_pareto_global_pos = int(pareto_sorted["position"].max())

    # --- Global ranking (all configurations)
    scores = pd.read_csv(args.scores_csv)
    if "score" not in scores.columns or "config_str" not in scores.columns:
        raise RuntimeError("scores_csv must contain columns 'score' and 'config_str'.")

    scores_sorted = scores.sort_values("score", ascending=True).reset_index(drop=True).copy()
    scores_sorted["global_rank"] = np.arange(1, len(scores_sorted) + 1)
    N = len(scores_sorted)

    # --- Sets
    top_set = scores_sorted[
        (scores_sorted["global_rank"] >= 1) &
        (scores_sorted["global_rank"] <= knee_global_pos)
    ]

    after_set = scores_sorted[
        (scores_sorted["global_rank"] > knee_global_pos) &
        (scores_sorted["global_rank"] <= last_pareto_global_pos)
    ]

    # --- Global tail by percentile
    tail_n = max(1, int(np.ceil(N * (args.tail_pct / 100.0))))
    tail_start_rank = N - tail_n + 1
    tail_set = scores_sorted[scores_sorted["global_rank"] >= tail_start_rank]

    # --- Service universe
    services = sorted({
        s for cfg in scores_sorted["config_str"].astype(str)
        for part in cfg.split("_")
        for s in part.split("-")
    })

    # --- Matrices and heatmaps
    pairs_top = compute_pair_probs(top_set["config_str"], services)
    pairs_after = compute_pair_probs(after_set["config_str"], services)
    pairs_tail = compute_pair_probs(tail_set["config_str"], services)

    M_top = probs_to_matrix(pairs_top, services)
    M_after = probs_to_matrix(pairs_after, services)
    M_tail = probs_to_matrix(pairs_tail, services)

    plot_heatmap(
        M_top,
        services,
        f"Co-location – Top Regime (Rank 1..{knee_global_pos})",
        outdir / "structural_patterns_heatmap_top.png"
    )

    plot_heatmap(
        M_after,
        services,
        f"Co-location – Post-Knee Regime (Rank {knee_global_pos + 1}..{last_pareto_global_pos})",
        outdir / "structural_patterns_heatmap_post_knee.png"
    )

    plot_heatmap(
        M_tail,
        services,
        f"Co-location – Global Tail {args.tail_pct:.2f}% (Rank {tail_start_rank}..{N})",
        outdir / "structural_patterns_heatmap_tail.png"
    )

    # --- Markdown summary
    hi, lo = args.hi, args.lo
    out_md = outdir / "structural_patterns_summary_3_regimes.md"

    broken_after = broken_from_top(pairs_top, pairs_after, hi=hi)
    broken_tail = broken_from_top(pairs_top, pairs_tail, hi=hi)

    md = []
    md.append("# Structural co-location patterns across three regimes\n")
    md.append("## Reproducible cutoffs\n")
    md.append(f"- Knee detected in the Pareto set (sorted by `{score_col}`): pareto_rank={knee_pareto_rank}")
    md.append(f"- Mapping to global ranking: knee_global_pos={knee_global_pos}")
    md.append(f"- Last global position covered by the Pareto set: last_pareto_global_pos={last_pareto_global_pos}")
    md.append(
        f"- Global tail: worst {args.tail_pct:.2f}% ⇒ {tail_n} configurations "
        f"(rank {tail_start_rank}..{N})\n"
    )

    md.append(summarize_patterns(pairs_top, "TOP", hi=hi, lo=lo))
    md.append(summarize_patterns(
        pairs_after,
        "POST-KNEE (still inside the Pareto-covered region)",
        hi=hi,
        lo=lo
    ))
    md.append(summarize_patterns(
        pairs_tail,
        f"GLOBAL TAIL (worst {args.tail_pct:.2f}%)",
        hi=hi,
        lo=lo
    ))

    md.append("\n## TOP patterns that break in the POST-KNEE regime\n")
    if broken_after.empty:
        md.append("- (none)")
    else:
        for _, r in broken_after.iterrows():
            md.append(
                f"- ({r['a']}, {r['b']}): top p={r['p_top']:.3f} → post-knee p={r['p_other']:.3f}"
            )

    md.append("\n## TOP patterns that break in the GLOBAL TAIL\n")
    if broken_tail.empty:
        md.append("- (none)")
    else:
        for _, r in broken_tail.iterrows():
            md.append(
                f"- ({r['a']}, {r['b']}): top p={r['p_top']:.3f} → tail p={r['p_other']:.3f}"
            )

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # --- CSVs
    pairs_top.to_csv(outdir / "structural_patterns_pairs_top.csv", index=False)
    pairs_after.to_csv(outdir / "structural_patterns_pairs_post_knee.csv", index=False)
    pairs_tail.to_csv(outdir / "structural_patterns_pairs_tail.csv", index=False)

    print("\n=== OK ===")
    print(f"Top: 1..{knee_global_pos}")
    print(f"Post-knee: {knee_global_pos + 1}..{last_pareto_global_pos}")
    print(f"Tail {args.tail_pct:.2f}%: {tail_start_rank}..{N} ({tail_n} configurations)")
    print(f"Outputs written to: {outdir}")
    print("- structural_patterns_heatmap_top.png")
    print("- structural_patterns_heatmap_post_knee.png")
    print("- structural_patterns_heatmap_tail.png")
    print("- structural_patterns_summary_3_regimes.md")


if __name__ == "__main__":
    main()