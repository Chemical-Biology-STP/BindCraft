# Creating Custom Filter and Advanced Settings Files

This document walks you through the thought process and practical steps for creating your
own filter and advanced settings files. The goal is to help you think like a protein
engineer, even if you are not one.

---

## Part 1: Should You Create a Custom File?

Before creating anything custom, ask yourself these questions:

1. **Have you already run with the existing files?** If you have not run BindCraft on your
   target yet, always start with `default_filters.json` and `default_4stage_multimer_hpc.json`.
   You need a baseline result before you can know what to change.

2. **Did your run produce zero designs?** If yes, start by loosening filters (`relaxed_filters.json`),
   not by creating a custom file. Custom files are for refinement, not for fixing a broken run.

3. **Did your run produce designs, but not the kind you want?** This is the right time for
   a custom file. For example: designs that pass filters but are too hydrophobic, or you
   want binders with more beta-sheet character, or you want to exclude a specific amino acid.

4. **Do you have a specific biological requirement?** For example: the binder must avoid
   a certain surface, must contain mostly helices for stability, or must not contain
   methionine because you are doing selenomethionine labelling. These are valid reasons
   to customise.

---

## Part 2: Creating a Custom Filter File

### The thought process

A filter file is a quality checklist. Each entry in the file is a question asked about
every design: "Does this design meet this criterion?" A design must pass all active checks.

Before editing any numbers, ask yourself:

- **What is the minimum quality I am willing to send to the lab?**
  If you are doing a high-throughput screen and can afford to test 50 designs, you can
  afford to be stricter. If you can only synthesise 5 designs, you should be more stringent
  because each one matters more.

- **Is my target easy or hard for AlphaFold2 to model?**
  Targets with flat surfaces, lots of disorder, or unusual folds will produce lower
  confidence scores even for good designs. Lowering thresholds compensates for this.

- **Do I have specific chemistry requirements?**
  If you know from the literature that methionine-rich interfaces tend to oxidise, you
  can add a limit on how many methionines appear at the interface.

### Understanding the filter file format

Each entry in the filter file follows this pattern:

```json
"ScoreName": {
    "threshold": 0.8,
    "higher": true
}
```

- **`"threshold"`** — the cutoff value. Set to `null` to disable the check entirely.
- **`"higher": true`** — the design must score *above* the threshold to pass.
- **`"higher": false`** — the design must score *below* the threshold to pass.

Most scores are checked twice — once for the `Average` across all 5 AlphaFold2 models,
and once for each individual model (`1_`, `2_`, etc.). The individual model checks are
typically only applied to models 1 and 2 (the most informative). Models 3–5 usually have
`"threshold": null` meaning they are recorded but not used as gates.

### Step-by-step: creating your custom filter file

**Step 1: Copy the closest existing file**

```bash
cp settings_filters/default_filters.json settings_filters/my_custom_filters.json
```

Always start from a copy. Never edit the originals.

**Step 2: Open the file and identify what you want to change**

The key scores and what to change them to:

| If you want... | Change this | Direction |
|---|---|---|
| Stricter binding confidence | Raise `Average_i_pTM` threshold above 0.5 | Higher = more strict |
| More lenient binding confidence | Lower `Average_i_pTM` threshold below 0.5 | Lower = more lenient |
| Stricter interface precision | Lower `Average_i_pAE` threshold below 0.35 | Lower = more strict |
| More lenient interface precision | Raise `Average_i_pAE` threshold above 0.35 | Higher = more lenient |
| Fewer but better hydrogen bonds | Raise `Average_n_InterfaceHbonds` above 3 | Higher = more strict |
| Designs with more interface contact | Raise `Average_n_InterfaceResidues` above 7 | Higher = more strict |
| Less hydrophobic binders | Lower `Average_Surface_Hydrophobicity` below 0.35 | Lower = more strict |
| Better shape fit | Raise `Average_ShapeComplementarity` above 0.6 | Higher = more strict |
| Limit a specific amino acid at interface | Set threshold on `Average_InterfaceAAs` → `"K"` | Lower = fewer allowed |
| Disable a check entirely | Set `"threshold": null` | — |

**Step 3: Adjust only the `Average_` and first two model entries**

For most checks, only change:
- `Average_ScoreName`
- `1_ScoreName`
- `2_ScoreName`

Leave `3_`, `4_`, and `5_` with `"threshold": null` — this is how all the provided files
work, and changing them is not necessary unless you have a specific reason.

**Step 4: Validate your JSON**

A single misplaced comma or bracket will cause BindCraft to crash at startup. Check your
file is valid JSON before submitting:

```bash
python3 -c "import json; json.load(open('settings_filters/my_custom_filters.json')); print('Valid JSON')"
```

**Step 5: Run a small pilot first**

Submit a job with `number_of_final_designs` set to 5–10. Check that the job starts, and
that the log shows designs being evaluated. Only then scale up.

### Practical examples

**Example A: You want high-confidence designs only**

You are going to synthesise a small number of designs and want high confidence they will
work. Tighten the key interface scores:

```json
"Average_i_pTM": { "threshold": 0.65, "higher": true },
"1_i_pTM":       { "threshold": 0.65, "higher": true },
"2_i_pTM":       { "threshold": 0.65, "higher": true },

"Average_i_pAE": { "threshold": 0.25, "higher": false },
"1_i_pAE":       { "threshold": 0.25, "higher": false },
"2_i_pAE":       { "threshold": 0.25, "higher": false },

"Average_ShapeComplementarity": { "threshold": 0.70, "higher": true },
"1_ShapeComplementarity":       { "threshold": 0.65, "higher": true },
"2_ShapeComplementarity":       { "threshold": 0.65, "higher": true }
```

Note: tightening thresholds significantly will reduce your pass rate and increase runtime.

**Example B: You want to exclude methionine-rich interfaces**

Methionine (M) can oxidise in vivo. Lysine (K) at interfaces can also cause off-target
binding. Limit both to at most 2 at the interface:

```json
"Average_InterfaceAAs": {
    "M": { "threshold": 2, "higher": false },
    "K": { "threshold": 2, "higher": false }
}
```

Leave all other amino acid entries with `"threshold": null`.

**Example C: Exploring a difficult target — loosen everything non-essential**

You want to see what BindCraft can produce at all before worrying about perfection:

```json
"Average_i_pTM":               { "threshold": 0.40, "higher": true },
"Average_i_pAE":               { "threshold": 0.45, "higher": false },
"Average_n_InterfaceResidues": { "threshold": 5,    "higher": true },
"Average_n_InterfaceHbonds":   { "threshold": 1,    "higher": true },
"Average_n_InterfaceUnsatHbonds": { "threshold": 8, "higher": false },
"Average_ShapeComplementarity": { "threshold": 0.45, "higher": true },
"Average_Surface_Hydrophobicity": { "threshold": 0.45, "higher": false }
```

---

## Part 3: Creating a Custom Advanced Settings File

### The thought process for advanced settings — what kind of structure it
aims for, how hard it tries, and what tools it uses to refine sequences. These are more
powerful and more risky to change than filter thresholds. A wrong filter threshold wastes
some GPU time. A wrong algorithm setting can make the entire run produce nonsense.

Before changing anything, ask:

- **What is different about my target compared to a typical protein?**
  Is it a membrane protein? A heavily glycosylated surface? An intrinsically disordered
  region? A peptide? Each of these has a corresponding setting.

- **What structure do I want the binder to have?**
  Do you want a helix bundle? A beta-sheet. A mixed fold? This is controlled by `weights_helicity`.

- **Am I willing to trade speed for quality?**
  Increasing iterations increases quality but also runtime. Decreasing them does the reverse.

### Step-by-step: creating your custom advanced settings file

**Step 1: Copy the closest existing file**

```bash
cp settings_advanced/default_4stage_multimer_hpc.json settings_advanced/my_custom_settings.json
```

**Step 2: Understand and adjust the parameters you want to change**

Below is a plain-language guide to every parameter:

---

#### Amino acid controls

| Parameter | What it does | Default | When to change |
|---|---|---|---|
| `omit_AAs` | Amino acids never used in designs. Always includes `"C"` (cysteine causes disulfide problems) | `"C"` | Add others e.g. `"CM"` to also exclude methionine |
| `force_reject_AA` | If `true`, completely rejects any sequence containing the omitted AAs. If `false`, just discourages them | `false` | Set `true` if you have a hard requirement to exclude an amino acid |

---

#### Algorithm controls

| Parameter | What it does | Default | When to change |
|---|---|---|---|
| `design_algorithm` | Which optimisation pipeline to use. `"4stage"` is standard; `"3stage"` skips beta-sheet optimisation and is faster | `"4stage"` | Use `"3stage"` for peptides or speed |
| `sample_models` | Randomly rotates through different AlphaFold2 models during design. Increases diversity | `true` | Rarely change. Leave `true` |
| `soft_iterations` | Number of iterations in Stage 2 (Softmax). More = better optimisation but slower | `75` | Increase to 100 for difficult targets; decrease to 50 for speed |
| `temporary_iterations` | Number of iterations in Stage 1 (Logits). | `45` | Increase for hard targets |
| `hard_iterations` | Iterations in Stage 3 (One-hot) | `5` | Rarely needs changing |
| `greedy_iterations` | Iterations in Stage 4 (PSSM greedy) | `15` | Rarely needs changing |
| `greedy_percentage` | Fraction of positions mutated per greedy step | `1` | Increase slightly for more sequence diversity |

---

#### Template controls (important for difficult targets)

| Parameter | What it does | Default | When to change |
|---|---|---|---|
| `rm_template_seq_design` | During design, removes the known sequence of your target from AlphaFold's memory, forcing it to reason about structure only | `false` | Set `true` if your target has a known AlphaFold structure that may be over-constraining designs |
| `rm_template_seq_predict` | Same but during the validation prediction step | `false` | Set `true` together with above |
| `predict_initial_guess` | Seeds each trajectory with an initial AlphaFold prediction of the binder on the target. Helps on hard targets | `false` | Set `true` for targets where random starts keep failing Stage 1 |

---

#### Structure bias controls

| Parameter | What it does | Default | When to change |
|---|---|---|---|
| `weights_helicity` | Controls the bias toward alpha-helices vs beta-sheets. Negative = helix bias. Positive = beta-sheet bias. Zero = no bias | `-0.3` | Set to `-1.0` or lower for strong helix bias; set to `+2.0` for beta-sheet bias (as in `betasheet_4stage_multimer.json`) |
| `random_helicity` | Randomises the helicity weight each trajectory. Produces more structurally diverse output | `false` | Set `true` if you want a mixture of folds |
| `use_rg_loss` | Penalises binders that sprawl out (high radius of gyration). Encourages compact, globular binders | `true` | Set `false` for peptides or deliberately extended binders |
| `weights_rg` | How strongly to penalise non-compactness | `0.3` | Increase for more compact binders; decrease for more extended ones |

---

#### Contact distance controls

| Parameter | What it does | Default | When to change |
|---|---|---|---|
| `intra_contact_distance` | Maximum distance (Å) between binder residues to count as a contact | `14.0` | Rarely change |
| `inter_contact_distance` | Maximum distance (Å) between binder and target residues to count as an interface contact | `20.0` | Increase slightly if your target has a deep pocket you want to reach into |
| `intra_contact_number` | Minimum contacts within the binder required | `2` | Increase for more internally structured binders |
| `inter_contact_number` | Minimum contacts to the target required | `2` | Increase to force more interface contact |

---

#### ProteinMPNN sequence design controls

ProteinMPNN is a separate AI that redesigns the amino acid sequence of the binder backbone
after each trajectory, to improve stability and solubility.

| Parameter | What it does | Default | When to change |
|---|---|---|---|
| `enable_mpnn` | Whether to run ProteinMPNN sequence redesign at all | `true` | Rarely disable |
| `mpnn_fix_interface` | If `true`, MPNN does not change residues at the binder–target interface, only the rest of the binder. If `false`, it can change everything | `true` | Set `false` (as in `mpnn` variants) for more sequence diversity at the interface |
| `num_seqs` | How many sequence variants MPNN generates per backbone | `20` | Increase for more sequence diversity |
| `max_mpnn_sequences` | How many of those sequences to take forward for validation | `2` | Increase to 4–5 if you want more variants per backbone, at the cost of more compute |
| `sampling_temp` | Controls MPNN's sequence diversity. Higher = more random sequences. Lower = more conservative. `0.1` is standard | `0.1` | Increase to `0.2–0.3` for more diverse sequences; decrease for highly conserved ones |
| `mpnn_weights` | Which MPNN weight set to use. `"soluble"` is for standard soluble proteins | `"soluble"` | Leave as `"soluble"` unless designing transmembrane binders |

---

#### Validation controls

| Parameter | What it does | Default | When to change |
|---|---|---|---|
| `num_recycles_design` | AlphaFold2 recycles during design iterations. More = slower but more accurate | `1` | Leave at 1 for speed; increase to 3 for more accurate stage-by-stage evaluation |
| `num_recycles_validation` | Recycles during final structure validation | `3` | Rarely change |

---

#### Rejection and monitoring controls

| Parameter | What it does | Default | When to change |
|---|---|---|---|
| `enable_rejection_check` | Monitors the pass rate of trajectories. If the pass rate falls below `acceptance_rate`, the job stops early to avoid wasting GPU time on a failing run | `true` | Leave `true` — it saves a lot of wasted compute |
| `acceptance_rate` | Minimum fraction of trajectories that must pass to keep running | `0.01` (1%) | For peptides this is raised to `0.1` (10%) because peptide pass rates are inherently lower |
| `start_monitoring` | How many trajectories to run before starting to check the acceptance rate | `300–600` | Increase for harder targets that need more trajectories to warm up |
| `max_trajectories` | Cap on total trajectories before stopping regardless of pass rate. `false` means no cap | `false` | Set a number e.g. `1000` if you want to limit total runtime |

---

**Step 3: Validate your JSON**

```bash
python3 -c "import json; json.load(open('settings_advanced/my_custom_settings.json')); print('Valid JSON')"
```

**Step 4: Name your file descriptively**

Use a name that captures what makes your settings different, following the existing
naming convention:

```
default_4stage_multimer_highconf_helixbias.json
betasheet_4stage_multimer_flexible_noM.json
peptide_3stage_multimer_relaxed.json
```

---

## Part 4: Common Customisation Scenarios and Recipes

### Scenario 1: I want high-confidence helix binders for a well-behaved target

**Filters:** Tighten i_pTM to 0.65, ShapeComplementarity to 0.70

**Advanced settings:** Lower `weights_helicity` to `-1.0`; keep everything else default

```bash
cp settings_advanced/default_4stage_multimer_hpc.json settings_advanced/my_helix_highconf.json
# Edit: "weights_helicity": -1.0
cp settings_filters/default_filters.json settings_filters/my_highconf_filters.json
# Edit Average/1/2_ i_pTM to 0.65, ShapeComplementarity to 0.70
```

---

### Scenario 2: I want beta-sheet binders for a flat binding surface

**Filters:** Use `default_filters.json` unchanged

**Advanced settings:** Set `weights_helicity` to `+2.0`; set `optimise_beta` to `true`

```bash
cp settings_advanced/betasheet_4stage_multimer.json settings_advanced/my_betasheet.json
# Already has weights_helicity: -2.0 (strong beta bias) — just adjust other params if needed
```

---

### Scenario 3: My target is difficult — nothing is passing

Run diagnostics first with `no_filters.json` to see raw scores, then work out which
filter is blocking the most designs. Then create a custom filter that relaxes just that
threshold, rather than relaxing everything.

```bash
# Step 1: Run with no filters to collect raw scores
# Step 2: Look at the output CSV and find which score consistently fails
# Step 3: Make a targeted relaxation file
cp settings_filters/default_filters.json settings_filters/my_relaxed_specific.json
# Edit only the specific threshold that was blocking
```

---

### Scenario 4: I want to exclude cysteine AND methionine from all designs

```bash
cp settings_advanced/default_4stage_multimer_hpc.json settings_advanced/my_noCM.json
# Edit:
# "omit_AAs": "CM",
# "force_reject_AA": true
```

---

## Part 5: What NOT to Change

Some parameters should be left alone unless you have deep expertise:

- **`weights_pae_intra`, `weights_pae_inter`, `weights_con_intra`, `weights_con_inter`** —
  These are the internal loss function weights that govern how AlphaFold2 is steered during
  optimisation. Changing these in unbalanced ways can cause trajectories to optimise for
  the wrong thing entirely.

- **`model_path`, `mpnn_weights`** — These point to specific trained model weights.
  Do not change unless you have alternative model files installed.

- **`af_params_dir`, `dssp_path`, `dalphaball_path`** — These are infrastructure paths.
  On the cluster, leave them as set in `default_4stage_multimer_hpc.json`.

- **`predict_bigbang`** — An experimental feature. Leave `false`.

---

## Part 6: Quick Reference — Parameters Most Worth Adjusting

For non-computational scientists, these are the parameters that give the most control
for the least risk:

**In filter files:**
- `Average_i_pTM` — binding confidence gate (raise for higher quality, lower for more output)
- `Average_i_pAE` — interface precision gate (lower for higher quality, raise for more output)
- `Average_n_InterfaceHbonds` — chemical specificity gate
- `Average_Surface_Hydrophobicity` — aggregation risk gate
- `Average_InterfaceAAs` → individual amino acid limits

**In advanced settings files:**
- `weights_helicity` — the single most impactful structural bias control
- `omit_AAs` — hard-exclude amino acids you do not want
- `predict_initial_guess` — turn on for difficult targets
- `rm_template_seq_design` / `rm_template_seq_predict` — turn on for targets with known structures that may be over-constraining design
- `mpnn_fix_interface` — turn off for more sequence diversity at the interface
- `max_trajectories` — set a number to cap total GPU time
