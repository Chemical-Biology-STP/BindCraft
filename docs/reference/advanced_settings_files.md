# Advanced Settings Files Reference

Quick-reference for all advanced settings files shipped with BindCraft.
For full explanations of every parameter, see
[Creating Custom Filters and Settings](../creating_custom_filters_and_settings.md).

## Available files (`settings_advanced/`)

### Default (helical bias) — 4-stage

| File | `rm_template_seq` | `predict_initial_guess` | `mpnn_fix_interface` | `weights_helicity` |
|---|---|---|---|---|
| `default_4stage_multimer_hpc.json` | `false` | `false` | `true` | `-0.3` |
| `default_4stage_multimer.json` | `false` | `false` | `true` | `-0.3` |
| `default_4stage_multimer_flexible.json` | `true` | `false` | `true` | `-0.3` |
| `default_4stage_multimer_hardtarget.json` | `false` | `true` | `true` | `-0.3` |
| `default_4stage_multimer_mpnn.json` | `false` | `false` | `false` | `-0.3` |
| `default_4stage_multimer_mpnn_flexible.json` | `true` | `false` | `false` | `-0.3` |
| `default_4stage_multimer_mpnn_hardtarget.json` | `false` | `true` | `false` | `-0.3` |
| `default_4stage_multimer_flexible_hardtarget.json` | `true` | `true` | `true` | `-0.3` |
| `default_4stage_multimer_mpnn_flexible_hardtarget.json` | `true` | `true` | `false` | `-0.3` |

### Beta-sheet bias — 4-stage

| File | `rm_template_seq` | `predict_initial_guess` | `mpnn_fix_interface` | `weights_helicity` |
|---|---|---|---|---|
| `betasheet_4stage_multimer.json` | `false` | `false` | `true` | `+2.0` |
| `betasheet_4stage_multimer_flexible.json` | `true` | `false` | `true` | `+2.0` |
| `betasheet_4stage_multimer_hardtarget.json` | `false` | `true` | `true` | `+2.0` |
| `betasheet_4stage_multimer_mpnn.json` | `false` | `false` | `false` | `+2.0` |
| `betasheet_4stage_multimer_mpnn_flexible.json` | `true` | `false` | `false` | `+2.0` |
| `betasheet_4stage_multimer_mpnn_hardtarget.json` | `false` | `true` | `false` | `+2.0` |
| `betasheet_4stage_multimer_flexible_hardtarget.json` | `true` | `true` | `true` | `+2.0` |
| `betasheet_4stage_multimer_mpnn_flexible_hardtarget.json` | `true` | `true` | `false` | `+2.0` |

### Peptide — 3-stage

| File | `predict_initial_guess` | `mpnn_fix_interface` | `weights_helicity` | `acceptance_rate` |
|---|---|---|---|---|
| `peptide_3stage_multimer.json` | `true` | `true` | `+0.95` | `0.10` |
| `peptide_3stage_multimer_flexible.json` | `true` | `true` | `+0.95` | `0.10` |
| `peptide_3stage_multimer_mpnn.json` | `true` | `false` | `+0.95` | `0.10` |
| `peptide_3stage_multimer_mpnn_flexible.json` | `true` | `false` | `+0.95` | `0.10` |

## Key parameter defaults (all files share these unless noted)

| Parameter | Default value |
|---|---|
| `omit_AAs` | `"C"` |
| `force_reject_AA` | `false` |
| `use_multimer_design` | `true` |
| `soft_iterations` | `75` |
| `temporary_iterations` | `45` |
| `hard_iterations` | `5` |
| `greedy_iterations` | `15` |
| `num_recycles_design` | `1` |
| `num_recycles_validation` | `3` |
| `num_seqs` (MPNN) | `20` (peptide: `10`) |
| `max_mpnn_sequences` | `2` |
| `sampling_temp` | `0.1` |
| `enable_rejection_check` | `true` |
| `acceptance_rate` | `0.01` (peptide: `0.10`) |
| `max_trajectories` | `false` (no cap) |

## Keyword decoder

| Keyword in filename | What it changes |
|---|---|
| `default` | Mild helix bias (`weights_helicity: -0.3`) |
| `betasheet` | Strong beta-sheet bias (`weights_helicity: +2.0`) |
| `4stage` | Full 4-stage optimisation pipeline |
| `3stage` | 3-stage pipeline (no beta-optimisation); used for peptides |
| `multimer` | AlphaFold-Multimer models the full binder+target complex |
| `flexible` | Template sequence removed (`rm_template_seq: true`) |
| `hardtarget` | Seeded initialisation (`predict_initial_guess: true`) |
| `mpnn` | Interface residues free for MPNN redesign (`mpnn_fix_interface: false`) |
| `hpc` | HPC-specific paths pre-configured; otherwise identical to standard |
