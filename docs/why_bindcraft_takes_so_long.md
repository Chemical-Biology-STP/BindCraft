# Why BindCraft Takes a Long Time to Produce Results

This document explains why designing 100 protein binders between 60–150 amino acids in length
can take days of compute time, and why results may not appear until late in that process.

---

## The Core Problem: Protein Design is Not Like Graphic Design

A logo has a few hundred pixels. A protein binder has thousands of atoms, and every atom
influences every other atom. The "design space" — all possible combinations of amino acids
at all possible positions — is astronomically large. A 100 amino acid protein has 20¹⁰⁰
possible sequences. That is more combinations than there are atoms in the observable universe.
BindCraft cannot simply pick a good sequence; it has to search this space intelligently,
and verify each candidate rigorously.

---

## What BindCraft Does for Each Design Candidate

### Stage 1: Hallucination (Test Logits)
BindCraft iteratively adjusts the binder sequence while running AlphaFold2 predictions — the
same AI system that won the Nobel Prize — to check whether the designed binder would fold
correctly *and* dock onto the target protein. This stage alone involves hundreds of forward
passes through a large neural network.

### Stage 2–4: Multi-stage Optimisation
Each trajectory progresses through four optimisation stages:
- **Stage 1** – Test Logits (~50 iterations)
- **Stage 1b** – Additional Logits Optimisation (~25 iterations)
- **Stage 2** – Softmax Optimisation (~45 iterations)
- **Stage 3** – One-hot Optimisation (~5 iterations)
- **Stage 4** – PSSM Semigreedy Optimisation (~15 iterations)

Each iteration is a full AlphaFold2 inference run on a GPU.

### Structure Prediction and Scoring
Once a candidate passes optimisation, BindCraft:
- Predicts the full binder–target complex structure
- Runs PyRosetta molecular mechanics to physically relax the structure
- Calculates binding energy, surface complementarity, hydrogen bonds, buried unsatisfied
  polar atoms, and steric clashes

### Filtering
Most designs fail one or more of these checks and are discarded. A design only counts toward
the requested 100 if it passes every filter. In practice, the pass rate can be low — meaning
hundreds or thousands of trajectories must be attempted to yield 100 passing designs.

---

## Why Binder Length Makes It Worse

Longer binders (150 aa vs 60 aa) are significantly more expensive because:

- Larger input tensors slow down every AlphaFold2 inference
- More degrees of freedom make optimisation harder, requiring more iterations
- More atoms slow down PyRosetta relaxation and scoring
- More positions mean more ways to fail the quality filters

A 150 aa binder trajectory can take 2–3× longer than a 60 aa one.

---

## Why There Are No Results Until Late in the Run

BindCraft is deliberately stringent. It trades computational time upfront for a higher hit
rate in the wet lab — because a single binding assay takes weeks and significant cost.
It would rather run for days and return 10 high-confidence binders than quickly return 100
that are unlikely to bind.

A rough mental model: imagine running 100–1000 real experiments virtually, each taking
2–4 minutes of H100 GPU time, most of which fail quality control. To accumulate 100
*passing* designs, 500–1000 trajectories may need to complete first. On an NVIDIA H100 GPU
— one of the fastest available — that translates to 16–60+ hours of continuous compute.

Results only appear in the output folder once a design has passed every stage and every
filter. Until that point, the job is running normally even if the output folder is empty.

---

## Summary Table

| Factor | Impact on Runtime |
|---|---|
| 100 designs requested | Each requires passing all 4 stages + scoring + filters |
| 60–150 aa binder length | Longer = slower AlphaFold2, slower PyRosetta |
| Stringent quality filters | Most candidates are discarded; many trajectories needed |
| Multi-model consensus | Each iteration runs across 5 AlphaFold2 models |
| H100 GPU | Fast, but each trajectory still takes 2–10 minutes |

---

## How to Get Results Faster: Practical Suggestions

These are things you can think about before submitting a job that will meaningfully reduce
runtime and increase your chances of getting passing designs sooner.

### 1. Request fewer designs to start with
If you need 100 designs, consider running a pilot job requesting 10–20 first. This lets you
check that the target settings, filters, and binder length range are producing reasonable
candidates before committing days of GPU time to a full run. If the pilot produces nothing,
it is much faster to diagnose and adjust.

### 2. Narrow the binder length range
The length range 60–150 aa is very broad. Every extra amino acid adds cost, and longer
binders are disproportionately slower. Ask yourself: is there a biological reason you need
binders up to 150 aa? Many successful binders are in the 60–90 aa range. Narrowing to
60–90 aa can cut per-trajectory time by half or more.

### 3. Think carefully about which surface you want the binder to target
BindCraft allows you to specify hotspot residues on the target protein — specific amino acids
you want the binder to contact. If you have prior knowledge from the literature, mutagenesis
data, or a known binding epitope, providing hotspots dramatically focuses the search and
increases the fraction of trajectories that pass filters. Without hotspots, BindCraft
searches the entire surface, which is slower and noisier.

### 4. Use relaxed filters for an initial screen
The default filters are stringent. If you are in early-stage exploration and just want to
see what kinds of binders BindCraft produces for your target, consider running with
`relaxed_filters.json` first. This will return more designs faster, giving you something
to look at and assess before committing to a stringent run.

### 5. Check your target structure quality before submitting
BindCraft's results are only as good as the input structure. If your target PDB has missing
loops, poor resolution, or unresolved regions near the intended binding site, AlphaFold2
will struggle to design against it and more trajectories will fail. It is worth spending
time preparing a clean, well-resolved structure — trimming irrelevant chains, filling
critical loops if possible — before running a large job.

### 6. Consider the oligomeric state of your target
The multimer settings (used here with `default_4stage_multimer_hpc.json`) are designed for
targets that function as complexes. If your target is a monomer, using monomer settings will
be faster and produce cleaner results. Conversely, if your target is a homodimer and you
want binders that engage the dimer interface, make sure the multimer settings are configured
correctly — otherwise you may spend days designing binders against a surface that is buried
in the functional complex.

### 7. Submit multiple shorter jobs in parallel rather than one long job
Rather than one job requesting 100 designs, you can submit several jobs of 20–25 designs
each simultaneously (if GPU allocation allows). This distributes the search across
independent trajectories and you will start seeing results from whichever job finishes
first, rather than waiting for a single long queue.

### 8. Check the log file early
Within the first 10–15 minutes of a job running, you can already see whether trajectories
are progressing through all four stages or failing at Stage 1. If every trajectory is
failing Stage 1 with low pLDDT, that is a signal that something is wrong with the target
settings or structure — it is worth cancelling the job early and investigating rather than
letting it run for days producing nothing.

---

## Analogy for Non-Computational Scientists

Think of it like drug discovery by simulation. Instead of synthesising thousands of compounds
in the lab and testing them one by one, BindCraft is doing the equivalent virtually —
but each virtual experiment is still computationally intensive, and most candidates fail
the equivalent of toxicity or efficacy screening before they make it into your results.
The days of compute time replace what would otherwise be months of wet lab work.
