# BindCraft Documentation

This directory contains the source for the BindCraft user documentation,
built with [Sphinx](https://www.sphinx-doc.org) using the
[Read the Docs theme](https://sphinx-rtd-theme.readthedocs.io).

## Directory structure

```
docs/
├── conf.py                                # Sphinx configuration
├── index.rst                              # Top-level table of contents
├── Makefile                               # Build commands
│
├── why_bindcraft_takes_so_long.md         # Why jobs take days
├── settings_and_filters_guide.md          # Choosing settings and filters
├── creating_custom_filters_and_settings.md  # Creating your own files
│
├── reference/
│   ├── filter_files.md                    # Filter files reference table
│   └── advanced_settings_files.md         # Advanced settings reference table
│
└── _build/html/                           # Built HTML output (not in version control)
```

## Building the documentation

Sphinx is declared as a dependency in `pixi.toml` and is installed automatically
when you run `pixi install`. No separate installation step is needed.

Build from the `docs/` directory:

```bash
cd /nemo/stp/chemicalbiology/home/shared/software/BindCraft/docs

# Build HTML
make html

# Remove previous build
make clean
```

Or build from the BindCraft root using the pixi task:

```bash
cd /nemo/stp/chemicalbiology/home/shared/software/BindCraft
pixi run docs
```

The built site will be at `_build/html/index.html`.

To open it from a login node with X forwarding:

```bash
xdg-open _build/html/index.html
```

Or copy the `_build/html/` directory to a web server or shared location for team access.

## Rebuilding after edits

All source documents are plain Markdown (`.md`) files. Edit them directly,
then re-run `make html`. Sphinx will only rebuild pages that changed.

To force a full rebuild from scratch:

```bash
make clean && make html
```

## Adding a new page

1. Create a new `.md` file in `docs/` (or `docs/reference/` for reference material)
2. Add it to the appropriate `toctree` in `index.rst` or `reference/index.rst`
3. Run `make html`
