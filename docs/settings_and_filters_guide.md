# BindCraft Settings and Filters: A Plain-Language Guide

This document explains what each settings file and filter file does, in plain language,
so you can make an informed choice before submitting a job.

---

## Part 1: The Three Files You Need to Provide

Every BindCraft job takes three input files:

| Argument | What it controls |
|---|---|
| `-s` / `--settings` | Your target protein and job parameters |
| `-f` / `--filters` | How strict the quality checks are |
| `-a` / `--advanced` | The design algorithm and binder type |

---

## Part 2: Your Target Settings File (`-s`)

This is the file you are most likely to need to create or modify for your own target.
It lives in `settings_target/` and contains the following fields:

| Field | What it means | Example |
|---|---|---|
| `design_path` | Where output files will be saved | `"/path/to/my/output/"` |
| `binder_name` | A label used in output file names | `"MyTarget"` |
| `starting_pdb` | Path to the 3D structure of your target protein | `"/path/to/target.pdb"` |
| `chains` | Which chain(s) in the PDB file to design against | `"A"` or `"A,B"` |
| `target_hotspot_residues` | Specific residue numbers you want the binder to contact (optional but recommended) | `"56"` or `"45,56,78"` |
| `lengths` | Range of binder lengths to try, in amino acids | `[65, 150]` |
| `number_of_final_designs` | How many passing designs to collect before stopping | `100` |

### Tips for filling in your target settings

**`target_hotspot_residues`** — this is the single most impactful thing you can provide.
If you know from the literature, from mutagenesis experiments, or from a known binding
partner which residues on your target are important for binding, enter them here. BindCraft
will focus the binder around those residues rather than searching the entire protein surface.
This dramatically increases the pass rate and reduces runtime. If you have no prior knowledge,
leave it empty — but expect longer runtimes.

**`lengths`** — keep this range as narrow as your biology allows. A range of [65, 80] is
much faster than [65, 150]. Longer binders take more compute time per trajectory and are
harder to optimise. Start narrow, and widen only if needed.

**`number_of_final_designs`** — for an initial run to test a new target, use 10–20 rather
than 100. This gives you results to look at much sooner, and lets you judge whether the
designs look promising before committing to a large job.

---

## Part 3: Understanding the Scores (Plain Language Glossary)

Before choosing a filter, it helps to understand what the scores actually mean. All of these
are produced by AlphaFold2 or PyRosetta during each design trajectory.

---

### AlphaFold2 Confidence Scores

AlphaFold2 does not just predict a structure — it also estimates how confident it is in
that prediction. These confidence estimates are what the filters use as quality gates.
They are not experimental measurements; they are the AI's own assessment of how well it
thinks the structure is determined.

---

#### pLDDT — Per-residue Local Distance Difference Test
**Range: 0 to 1. Higher is better. Threshold used: ≥ 0.80**

**What it measures:** How confident AlphaFold2 is in the local 3D position of each amino
acid in the binder. A score of 1.0 means the model is completely confident the atom
positions are correct. A score below 0.5 means the region is likely disordered or
the prediction is unreliable.

**In plain language:** Think of it as a per-residue confidence percentage. A binder with
pLDDT ≥ 0.80 is one where AlphaFold2 is saying "I am at least 80% confident this protein
folds into a well-defined shape." Disordered or misfolded regions score low. The filter
requires the entire binder to score above this threshold, not just parts of it.

**Why it matters:** A binder that doesn't fold predictably in silico is unlikely to fold
correctly when synthesised in the lab. pLDDT is the first and most fundamental check.

---

#### pTM — Predicted Template Modelling Score
**Range: 0 to 1. Higher is better. Threshold used: ≥ 0.55**

**What it measures:** A global confidence score for the overall fold of the protein complex.
It is derived from AlphaFold2's predicted error in the relative positions of all residue
pairs across the entire structure.

**In plain language:** If pLDDT is a per-residue score, pTM is a whole-structure score.
It asks: "Does AlphaFold2 think the entire binder+target complex has a well-defined,
consistent 3D arrangement?" Values above 0.5 are generally considered meaningful predictions.

---

#### i_pTM — Interface predicted Template Modelling Score
**Range: 0 to 1. Higher is better. Threshold used: ≥ 0.50**

**What it measures:** The same as pTM, but calculated *only* for the residues at the
interface between the binder and the target — the contact surface. It specifically asks
how confident AlphaFold2 is in the relative positioning of the binder against the target.

**In plain language:** This is the most important single score for binder design. A high
pTM with a low i_pTM means the binder folds well on its own but AlphaFold2 is not
confident it actually docks onto the target correctly. You want both to be high, but i_pTM
is the one that tells you whether the *interaction* is real. Think of it as "binding
confidence."

**Why it matters:** It is possible to design a beautifully folded binder that has no
affinity for the target. i_pTM catches this — a low i_pTM means the binder and target
are not consistently predicted to sit together in a defined orientation.

---

#### i_pAE — Interface Predicted Aligned Error
**Range: 0 to ~30 Å. Lower is better. Threshold used: ≤ 0.35**

**What it measures:** AlphaFold2's estimated positional error (in normalised units)
for residues across the binder–target interface. It is the average uncertainty in where
interface residues sit relative to each other.

**In plain language:** A complementary view to i_pTM. Low i_pAE means AlphaFold2 is
predicting a precise, well-defined interface geometry. High i_pAE means the relative
position of the binder on the target is fuzzy or inconsistent — a sign the interaction
is weak or non-specific.

---

### PyRosetta Physics-Based Scores

These are calculated by PyRosetta, which uses classical physics (molecular mechanics) to
evaluate the structure after AlphaFold2 has predicted it. They complement the AI confidence
scores with real physical chemistry reasoning.

---

#### dG — Binding Free Energy
**Units: Rosetta Energy Units (REU). Lower (more negative) is better. Threshold: < 0**

**In plain language:** This is the estimated energy released when the binder sticks to the
target. Negative values mean binding is energetically favourable — the complex is more
stable together than apart. Positive values mean the interaction is unfavourable. Think of
it as the molecular equivalent of asking "does this actually want to stick?"

---

#### dSASA — Change in Solvent Accessible Surface Area
**Units: Ų. Higher is better. Threshold: > 1**

**In plain language:** How much protein surface area gets buried when the binder binds the
target. If dSASA is near zero, the binder is barely touching the target. A higher value
means more surface is buried — indicating a real, substantive contact interface rather
than a glancing touch.

---

#### ShapeComplementarity
**Range: 0 to 1. Higher is better. Threshold: ≥ 0.60 (average), ≥ 0.55 (per model)**

**In plain language:** How well the binder's surface shape fits the target's surface, like
a key fitting a lock. A score of 1.0 is a perfect geometric fit. Natural antibody-antigen
interfaces typically score around 0.60–0.75. Low scores mean the binder and target surfaces
do not match well — there are gaps, bumps, or poor contact.

---

#### n_InterfaceHbonds — Number of Interface Hydrogen Bonds
**Higher is better. Threshold: ≥ 3**

**In plain language:** Hydrogen bonds are specific, directional interactions between polar
atoms (like N-H···O). They contribute to binding specificity — they make the binder
prefer *this* target over random other proteins. A minimum of 3 interface hydrogen bonds
is required to ensure the interaction has some chemical specificity, not just shape.

---

#### n_InterfaceUnsatHbonds — Unsatisfied Interface Hydrogen Bond Donors/Acceptors
**Lower is better. Threshold: ≤ 4**

**In plain language:** These are polar atoms at the interface that are "reaching out" for
a hydrogen bond partner but not finding one. They are energetically costly — burying a
polar atom without giving it a bonding partner destabilises the complex. Too many unsatisfied
hydrogen bonds is a common reason computationally designed binders do not work in practice.

---

#### Binder_RMSD — Binder Root Mean Square Deviation
**Units: Ångströms. Lower is better. Threshold: < 3.5 Å**

**In plain language:** This measures how similar the binder structure looks across the
multiple AlphaFold2 models run for each design. If all 5 models predict essentially the
same shape (low RMSD), the binder has a single, well-defined fold. If the models produce
wildly different shapes (high RMSD), the binder is structurally ambiguous — a warning
sign that it may not fold reliably.

---

#### Surface_Hydrophobicity
**Range: 0 to 1. Lower is better. Threshold: < 0.35**

**In plain language:** The fraction of the binder's exposed surface that is hydrophobic
(oily). Proteins with too much exposed hydrophobic surface tend to aggregate — they stick
to themselves and other proteins non-specifically, which is undesirable for a therapeutic
or research tool. This filter helps weed out binders that might work in silico but would
aggregate in solution.

---

## Part 4: Choosing a Filter File (`-f`)

> See Part 3 above for plain-language explanations of pLDDT, i_pTM, dG, and the other scores mentioned below.

Filters decide which designed binders are good enough to keep. Each filter checks a
specific property of the binder, and a design must pass all active filters to be saved.

### Available filter files

#### `default_filters.json` — recommended for most protein binders
The standard set of quality checks. Balanced between being thorough and achievable.
Use this unless you have a specific reason to deviate.

Key thresholds it enforces:
- Binder folds confidently on its own (pLDDT ≥ 0.80 — AlphaFold's confidence score, 0–1)
- Binder docks confidently with the target (i_pTM ≥ 0.50 — interface confidence, 0–1)
- Interface is geometrically complementary (shape score ≥ 0.60 — how well the surfaces fit)
- At least 7 residues at the interface (ensures a real contact surface)
- At least 3 hydrogen bonds at the interface (ensures specific, non-greasy binding)
- No more than 4 unsatisfied hydrogen bond donors/acceptors (penalises "sticky" polar atoms
  that aren't paired — a common cause of aggregation)
- Binder does not have excessive loop structure (< 90% loop)
- Binding is thermodynamically favourable (dG < 0 — negative = stabilising)
- Binding buries surface area (dSASA > 1 — confirms real burial of surface)
- Binder self-energy is favourable (binder energy score < 0)
- Surface is not too hydrophobic (< 35% hydrophobicity — reduces aggregation risk)
- Shape complementarity at interface (≥ 0.55 per model)
- Binder structure reproducible across predictions (RMSD < 3.5 Å)

#### `relaxed_filters.json` — use for early exploration or difficult targets
The same checks as default but with looser thresholds. More designs will pass, which is
useful when you want to see *something* quickly, or when your target is genuinely
challenging (disordered regions, unusual topology, very flat binding surface).

Notable differences from default:
- Interface confidence threshold lowered (i_pAE ≤ 0.40 vs 0.35)
- Shape complementarity threshold lowered (≥ 0.50 vs 0.60)
- Fewer required interface residues (≥ 6 vs 7)
- Fewer required hydrogen bonds (≥ 2 vs 3)
- More unsatisfied hydrogen bonds allowed (≤ 6 vs 4)
- Binder RMSD tolerance relaxed (< 4.5 Å vs 3.5 Å)

#### `no_filters.json` — use for benchmarking or diagnosing problems only
All thresholds are disabled. Every trajectory that completes will produce output,
regardless of quality. Useful for understanding what the raw designs look like, or for
diagnosing why a target is producing no results with tighter filters. Not recommended for
generating designs you intend to take into the lab.

#### `peptide_filters.json` — use only for short peptide binders (< ~30 aa)
Tuned for peptides, which have weaker structural signals than folded proteins:
- Lower interface contact requirement (≥ 4 residues)
- Fewer hydrogen bonds required (≥ 1)
- Higher surface hydrophobicity allowed (< 0.50)
- Stricter hotspot positioning (RMSD < 3 Å — peptides must land precisely)
- Stricter binder RMSD (< 2.5 Å — peptide structure must be very reproducible)

#### `peptide_relaxed_filters.json` — relaxed version for peptide exploration
The peptide equivalent of `relaxed_filters.json`. Even more permissive on interface
contact requirements (≥ 2 residues) and shape complementarity (not required).

### Quick decision guide

| My situation | Recommended filter |
|---|---|
| Standard folded protein binder, first serious run | `default_filters.json` |
| Difficult target or first exploratory run | `relaxed_filters.json` |
| Designing short peptides (< ~30 aa) | `peptide_filters.json` |
| Exploring peptides on a hard target | `peptide_relaxed_filters.json` |
| Diagnosing why no designs are passing | `no_filters.json` |

---

## Part 5: Choosing an Advanced Settings File (`-a`)

These files live in `settings_advanced/` and control the design algorithm itself —
what kind of binder structure to aim for, and how to run the optimisation.

The filename tells you most of what you need to know. It is built from keyword combinations:

### Keyword decoder

| Keyword in filename | What it means |
|---|---|
| `default` | Standard settings; no strong bias towards a particular secondary structure |
| `betasheet` | Actively biases the design towards beta-sheet structure (weights_helicity = -2.0). Use if you want flat, sheet-like binders or if your target binding site is a beta-sheet interface |
| `4stage` | Uses all four optimisation stages. More thorough. Recommended for most cases |
| `3stage` | Uses three stages, skipping beta-optimisation. Faster. Used for peptides |
| `multimer` | Uses AlphaFold-Multimer to model the binder + target complex together. Recommended — gives more accurate interface predictions |
| `mpnn` | Allows ProteinMPNN to redesign all residues, including those at the interface. Default files fix the interface residues during sequence design; `mpnn` variants allow more flexibility |
| `flexible` | Allows the target sequence template to be randomised during design (`rm_template_seq = true`). Useful if your target has disordered regions or if you suspect AlphaFold is over-constraining the design to a known conformation |
| `hardtarget` | Enables `predict_initial_guess = true`, which seeds each trajectory with an initial AlphaFold prediction of the binder docked to the target. Helps for targets where the default random initialisation rarely finds the right binding geometry |
| `hpc` | Same algorithm as `default_4stage_multimer` but with the HPC-specific file paths pre-configured. Use this on the cluster |

### Recommended choices for common scenarios

| Scenario | Recommended advanced settings |
|---|---|
| Standard first run on a new target (on the cluster) | `default_4stage_multimer_hpc.json` |
| Target is difficult and trajectories keep failing early | `default_4stage_multimer_hardtarget.json` |
| Target has disordered regions or poor AlphaFold confidence | `default_4stage_multimer_flexible.json` |
| You want beta-sheet binders specifically | `betasheet_4stage_multimer.json` |
| Short peptide binders (< ~30 aa) | `peptide_3stage_multimer.json` |
| You want maximum sequence diversity from MPNN | `default_4stage_multimer_mpnn.json` |
| Difficult target + disordered regions + max MPNN flexibility | `default_4stage_multimer_mpnn_flexible_hardtarget.json` |

---

## Part 6: Putting It All Together — Example Commands

### Standard run for a new target
```bash
sbatch bindcraft_gh100.slurm \
  -s settings_target/MyTarget.json \
  -f settings_filters/default_filters.json \
  -a settings_advanced/default_4stage_multimer_hpc.json
```

### Quick exploratory run to see if a target is tractable
```bash
sbatch bindcraft_gh100.slurm \
  -s settings_target/MyTarget.json \
  -f settings_filters/relaxed_filters.json \
  -a settings_advanced/default_4stage_multimer_hpc.json
```

### Difficult target where default settings produce nothing
```bash
sbatch bindcraft_gh100.slurm \
  -s settings_target/MyTarget.json \
  -f settings_filters/relaxed_filters.json \
  -a settings_advanced/default_4stage_multimer_hardtarget.json
```

### Short peptide binders
```bash
sbatch bindcraft_gh100.slurm \
  -s settings_target/MyTarget.json \
  -f settings_filters/peptide_filters.json \
  -a settings_advanced/peptide_3stage_multimer.json
```

---

## Part 7: How to Create a Target Settings File for Your Own Protein

Copy the existing example and edit the relevant fields:

```bash
cp settings_target/PDL1_hpc.json settings_target/MyTarget.json
```

Then open `settings_target/MyTarget.json` and update:
- `design_path` — where you want output saved
- `binder_name` — a short label for your protein
- `starting_pdb` — full path to your target's PDB file
- `chains` — which chain(s) to design against (check your PDB file)
- `target_hotspot_residues` — key residues if known, or remove the field entirely
- `lengths` — your desired binder length range
- `number_of_final_designs` — start with 10–20 for a new target

If you are unsure which residues to specify as hotspots, consult the literature for your
target protein. Any published binding partner, inhibitor, or mutagenesis study that
identifies key binding residues is useful input here.
