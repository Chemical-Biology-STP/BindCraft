# Filter Files Reference

Quick-reference table of all filter files shipped with BindCraft.
For full plain-language explanations of every score, see the
[Settings & Filters Guide](../settings_and_filters_guide.md).

## Available files (`settings_filters/`)

| File | Use case | Overall strictness |
|---|---|---|
| `default_filters.json` | Standard folded protein binder | Strict |
| `relaxed_filters.json` | Difficult targets or early exploration | Moderate |
| `no_filters.json` | Diagnostics only — no quality gates | None |
| `peptide_filters.json` | Short peptide binders (< ~30 aa) | Strict for peptides |
| `peptide_relaxed_filters.json` | Peptide exploration | Lenient |

## Threshold comparison

| Score | default | relaxed | no_filters | peptide | peptide_relaxed |
|---|---|---|---|---|---|
| `Average_pLDDT` | ≥ 0.80 | ≥ 0.80 | — | ≥ 0.80 | ≥ 0.80 |
| `Average_i_pTM` | ≥ 0.50 | ≥ 0.50 | — | ≥ 0.50 | ≥ 0.40 |
| `Average_i_pAE` | ≤ 0.35 | ≤ 0.40 | — | ≤ 0.35 | ≤ 0.40 |
| `Average_ShapeComplementarity` | ≥ 0.60 | ≥ 0.50 | — | — | — |
| `Average_n_InterfaceResidues` | ≥ 7 | ≥ 6 | — | ≥ 4 | ≥ 2 |
| `Average_n_InterfaceHbonds` | ≥ 3 | ≥ 2 | — | ≥ 1 | — |
| `Average_n_InterfaceUnsatHbonds` | ≤ 4 | ≤ 6 | — | ≤ 4 | — |
| `Average_Surface_Hydrophobicity` | ≤ 0.35 | ≤ 0.37 | — | ≤ 0.50 | ≤ 0.50 |
| `Average_Binder_Loop%` | ≤ 90 | ≤ 90 | — | ≤ 90 | ≤ 90 |
| `Average_Hotspot_RMSD` | ≤ 3.5 Å | ≤ 6.0 Å | — | ≤ 3.0 Å | ≤ 3.0 Å |
| `Average_Binder_RMSD` | ≤ 3.5 Å | ≤ 3.5 Å | — | ≤ 2.5 Å | ≤ 2.5 Å |
| `Average_dG` | < 0 | < 0 | — | < 0 | — |
| `Average_dSASA` | > 1 | > 1 | — | > 1 | — |
| `Average_Binder_Energy_Score` | < 0 | < 0 | — | < 0 | — |
| `InterfaceAAs K (avg)` | ≤ 3 | ≤ 5 | — | — | — |
| `InterfaceAAs M (avg)` | ≤ 3 | ≤ 5 | — | — | — |

`—` means no threshold is applied for that filter/score combination.

## JSON format reminder

Each score entry follows this pattern:

```json
"Average_i_pTM": {
    "threshold": 0.5,
    "higher": true
}
```

- `"threshold": null` — check is disabled (score is recorded but not used as a gate)
- `"higher": true` — design must score **above** the threshold
- `"higher": false` — design must score **below** the threshold

Scores are checked for `Average_`, `1_`, and `2_` (models 1 and 2).
Models 3–5 always have `"threshold": null`.
