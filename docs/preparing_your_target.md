# Preparing Your Target: What to Do Before Running BindCraft

The quality of a BindCraft run depends enormously on the quality of the inputs you
provide. A well-prepared target can double or triple the pass rate of trajectories.
A poorly prepared one can mean days of GPU time with nothing to show.

This page describes what you can do *before* submitting a job — using freely available
computational tools that require no programming experience — to give BindCraft the best
possible starting point.

---

## Step 1: Get a Good 3D Structure of Your Target

BindCraft needs a 3D coordinate file (PDB format) of your target protein.

### Option A: Use an experimentally determined structure

The best starting point is always an experimentally solved structure from the
[RCSB Protein Data Bank (PDB)](https://www.rcsb.org). Search for your protein by name,
UniProt accession, or gene name.

This is the preferred input for BindCraft because the 3D coordinates are based on
real physical measurements (X-ray diffraction, cryo-EM, or NMR), not a prediction.
BindCraft uses these coordinates in two ways:

1. **As the design target** — the atomic positions of your target define the surface
   that AlphaFold2 will try to design a binder against. More accurate coordinates mean
   a more accurate surface, which means the binder is being designed against something
   closer to the real protein in solution.

2. **As the validation reference** — after each trajectory, the designed binder is
   predicted in complex with your target and the result is compared back to the input
   structure. If your input structure is noisy or inaccurate, this validation step
   becomes unreliable.

In short: experimental structure → more accurate surface → better-targeted binders →
higher wet lab success rate.

When choosing between multiple structures of the same protein, prefer:

- **Higher resolution** — for X-ray structures, ≤ 2.0 Å is excellent; ≤ 2.5 Å is good.
  Higher resolution means more precisely placed atoms, which means a more accurate
  surface for BindCraft to design against.
- **The biologically relevant form** — if your protein functions as a dimer, use the
  dimer structure, not the monomer. BindCraft will design against whatever surface you
  give it; if the functional dimer buries a large patch of chain A, you do not want
  BindCraft designing binders that target that buried patch.
- **The functionally relevant state** — if you want a binder that blocks a binding site,
  use a structure where that site is open (apo form), not one where it is already occupied
  by a ligand. The ligand-bound form will have a different surface shape.
- **Minimal missing residues** — check the PDB entry for gaps in the chain. Large gaps
  near your intended binding site mean BindCraft is designing against an incomplete
  surface — the missing residues may form part of the real binding pocket.

### Option B: Use an AlphaFold2 structure prediction

If no experimental structure exists, use the
[AlphaFold Protein Structure Database](https://alphafold.ebi.ac.uk) — it covers the
entire human proteome and many other organisms. Search by gene name or UniProt ID and
download the PDB file directly.

Check the **per-residue confidence (pLDDT)** colour coding when you view the structure:
- **Blue (pLDDT > 90)** — high confidence, reliable for design
- **Yellow (pLDDT 70–90)** — moderate confidence, use with caution
- **Orange/Red (pLDDT < 70)** — disordered or unreliable; avoid designing against these regions

If your intended binding site is coloured orange or red, AlphaFold is telling you that
region is likely disordered. BindCraft will struggle there — see Step 4 for what to do.

### Option C: Predict your own structure with ColabFold

If your protein is not in the AlphaFold database (e.g. a mutant, a fusion protein, or
a novel sequence), use [ColabFold](https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/AlphaFold2.ipynb)
— a free, browser-based AlphaFold2 interface that requires no installation. Paste in
your sequence and it returns a PDB file within minutes.

---

## Step 2: Visualise and Inspect Your Target

Before doing anything else, look at your structure. Free tools that run in a browser
or on your desktop:

- **[Mol\*](https://molstar.org/viewer/)** — browser-based, no installation, excellent
  for quick inspection. Drag and drop your PDB file.
- **[PyMOL](https://pymol.org)** — desktop application, more powerful. A free educational
  version is available.
- **[UCSF ChimeraX](https://www.cgl.ucsf.edu/chimerax/)** — free, powerful, good for
  surface visualisation.

### What to look for

**Identify the binding surface you are targeting.**
Rotate the structure and look for:
- Concave pockets or grooves — binders prefer these over flat surfaces
- The active site, if your target is an enzyme
- Known protein-protein interaction interfaces from the literature
- Regions that, if blocked, would disrupt function

**Check for problematic regions near your binding site:**
- Missing loops (gaps in the chain) — these appear as broken ribbons in the visualisation
- Very flexible regions — these will have low pLDDT in AlphaFold structures
- Glycosylation sites (N-X-S/T sequons) — sugars attached here can physically block
  binder access and are not modelled in most structures

**Check the oligomeric state.**
Is your protein a monomer, dimer, or larger complex in solution? If it functions as a
dimer and you want to block a dimer interface, you need to use the dimer PDB structure
as your input, not the monomer.

---

## Step 3: Identify and Validate Your Hotspot Residues

Hotspot residues are the specific amino acids on your target that you want the binder
to contact. Providing them to BindCraft is the single most impactful thing you can do
to increase success. Without them, BindCraft searches the entire surface.

### How to find hotspots

**From the literature (best source):**
Search for papers on your target that describe:
- Alanine scanning mutagenesis — residues where Ala substitution abolishes binding
- Known inhibitors or binding partners and the residues they contact
- Epitopes from antibody studies
- Functional residues identified from disease mutations

**From structural analysis of a known complex:**
If a structure exists of your target bound to another protein, ligand, or antibody,
that contact interface is your hotspot. You can identify contacting residues in PyMOL:

```
# In PyMOL: select residues within 4 Å of the binding partner
select hotspots, (chain A) within 4 of (chain B)
```

This gives you a list of residue numbers you can paste directly into your target
settings file as `target_hotspot_residues`.

**From sequence conservation:**
Residues that are conserved across evolution are often functionally important.
[ConSurf](https://consurf.tau.ac.il) takes your protein sequence and highlights
conserved positions on the structure. Highly conserved surface residues near your
binding site are good hotspot candidates.

**From computational docking (see Step 5):**
If you have no prior structural information, docking a known small molecule or peptide
can suggest which residues are most important for binding.

### How many hotspots to specify

- **1–3 residues** is a good starting point. More is not always better — too many
  constraints can make it impossible for BindCraft to find a binder that contacts all
  of them simultaneously.
- If you are unsure, specify the single most important residue (e.g. a catalytic
  residue, or the one where Ala mutation most abolishes binding).
- If you have a known protein-protein interface, specifying 2–4 residues at the centre
  of that interface is appropriate.

---

## Step 4: Clean and Prepare Your PDB File

Raw PDB files from the database often contain things that confuse BindCraft:
multiple chains you do not want, crystallographic waters, ligands, alternate
conformations, and missing atoms.

### Use PDBFixer (already installed in your BindCraft environment)

PDBFixer can automatically fix most common problems. It is already available in
the BindCraft pixi environment:

```bash
cd /nemo/stp/chemicalbiology/home/shared/software/BindCraft
pixi run python - <<'EOF'
from pdbfixer import PDBFixer
from openmm.app import PDBFile

fixer = PDBFixer(filename='my_target_raw.pdb')

# Remove unwanted chains — keep only the ones you need
# e.g. to keep only chain A:
chains_to_remove = [c.id for c in fixer.topology.chains() if c.id != 'A']
fixer.removeChains(chains_to_remove)

# Find and fill missing residues and atoms
fixer.findMissingResidues()
fixer.findMissingAtoms()
fixer.addMissingAtoms()

# Remove water and heteroatoms (ligands, ions)
fixer.removeHeterogens(keepWater=False)

# Write the cleaned file
with open('my_target_clean.pdb', 'w') as f:
    PDBFile.writeFile(fixer.topology, fixer.positions, f)

print("Done — my_target_clean.pdb written")
EOF
```

### Manual checks to do in PyMOL or ChimeraX

After fixing, visually check:
- The correct chain(s) are present
- No large gaps exist near your binding site (if they do, consider using the AlphaFold
  structure instead, which has no gaps)
- The structure looks physically reasonable — no atoms floating in space

---

## Step 5: Use Computational Docking to Validate Your Binding Site

If you are uncertain which surface to target, or want to confirm your hotspot residues
before running BindCraft, a quick docking experiment can help.

### Protein-protein docking: find where another protein would bind

If you have a known binding partner (e.g. a natural ligand protein, a receptor),
docking it computationally can confirm which residues form the interface.

**Recommended tool: [ClusPro](https://cluspro.bu.edu)**
- Free, web-based, no installation
- Upload two PDB files (your target + a binding partner or a known binder)
- Returns predicted complex structures with contact residue lists
- Run time: typically 15–30 minutes

**Recommended tool: [HADDOCK](https://wenmr.science.uu.nl/haddock2.4/)**
- More powerful than ClusPro, allows you to specify ambiguous interaction restraints
- You can tell it "I know residue 56 is important" and it will prioritise interfaces
  involving that residue
- Free for academic use, web-based

### Small molecule docking: identify the binding pocket

If your target is an enzyme or receptor with a known small molecule ligand:

**Recommended tool: [DockThor](https://dockthor.lncc.br)** or
**[SwissDock](http://www.swissdock.ch)**
- Both are free and web-based
- Upload your target PDB and a ligand structure (downloadable from
  [PubChem](https://pubchem.ncbi.nlm.nih.gov))
- The docking pose shows you which residues line the binding pocket
- These pocket residues are excellent hotspot candidates for BindCraft

---

## Step 6: Assess Surface Druggability

Not all protein surfaces are equally amenable to binder design. Flat, featureless
surfaces are harder than concave pockets. Knowing this beforehand saves wasted compute.

**Recommended tool: [FTMap](https://ftmap.bu.edu)**
- Free, web-based
- Probes your protein surface with small organic molecules to find "hot spots" —
  regions that bind a variety of chemical probes
- High-scoring FTMap hotspots strongly correlate with regions where designed binders
  are most likely to succeed
- Run time: ~5 minutes

**Recommended tool: [SiteMap (Schrödinger)](https://www.schrodinger.com/sitemap)**
(requires a license, but may be available through your institution)
- More detailed pocket analysis
- Scores sites by druggability, volume, and hydrophilicity

**What to look for:**
FTMap will show you clusters of probe molecules on the surface. The largest, densest
cluster is the most "druggable" site. If this coincides with your intended binding site,
that is a good sign. If your intended site shows no clustering, binder design will be
harder — consider whether a nearby pocket could serve as the target instead.

---

## Step 7: Check for Relevant Literature and Existing Binders

Before investing days of compute time, do a literature check:

1. **Search for existing binders** — has anyone published an antibody, nanobody, or
   designed protein that binds your target? If so:
   - Their binding epitope gives you excellent hotspot information
   - Their interface residues are validated experimental data
   - You can use the published complex structure directly as your input PDB

2. **Search for known mutations that affect binding** — disease mutations, resistance
   mutations, and gain-of-function mutations at the surface all suggest important residues

3. **Check UniProt for your protein** — the
   [UniProt entry](https://www.uniprot.org) for most proteins lists known binding sites,
   active sites, and mutagenesis data in a structured format

---

## Summary: Pre-Run Checklist

Work through this checklist before submitting a BindCraft job:

- [ ] I have a PDB file with resolution ≤ 2.5 Å, or a high-confidence AlphaFold structure
- [ ] I have inspected the structure in Mol\* or PyMOL
- [ ] I have identified the surface I want to target and confirmed it is accessible
      (not buried, not glycosylated, not disordered)
- [ ] I have identified 1–3 hotspot residue numbers from literature, structural analysis,
      or FTMap
- [ ] I have cleaned the PDB file to contain only the relevant chain(s)
- [ ] I have checked PDBFixer output for remaining gaps near the binding site
- [ ] I have set `target_hotspot_residues` in my settings file
- [ ] I have set `lengths` to a range appropriate for my target surface size
      (small pocket → 60–80 aa; large flat surface → 80–120 aa)
- [ ] I am starting with `number_of_final_designs` set to 10–20 for a pilot run

---

## Quick Tool Reference

| Task | Tool | URL | Cost |
|---|---|---|---|
| Browse experimental structures | RCSB PDB | rcsb.org | Free |
| Download AlphaFold structures | AlphaFold DB | alphafold.ebi.ac.uk | Free |
| Predict structure from sequence | ColabFold | via Google Colab | Free |
| Visualise PDB in browser | Mol\* Viewer | molstar.org/viewer | Free |
| Visualise and analyse structure | PyMOL | pymol.org | Free (educational) |
| Fix PDB files | PDBFixer | (installed in BindCraft env) | Free |
| Find surface hotspots | FTMap | ftmap.bu.edu | Free |
| Protein-protein docking | ClusPro | cluspro.bu.edu | Free |
| Docking with restraints | HADDOCK | wenmr.science.uu.nl/haddock2.4 | Free (academic) |
| Small molecule docking | SwissDock | swissdock.ch | Free |
| Sequence conservation | ConSurf | consurf.tau.ac.il | Free |
| Protein/binding site info | UniProt | uniprot.org | Free |
