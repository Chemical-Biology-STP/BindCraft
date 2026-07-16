# Configuration file for the Sphinx documentation builder.

import os
import sys

# -- Project information -----------------------------------------------------

project = "BindCraft"
copyright = "2024, BindCraft Contributors"
author = "BindCraft Contributors"
release = "1.0.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",           # parse Markdown files
    "sphinx.ext.autosectionlabel",  # auto-generate section labels
]

# Allow both .rst and .md source files
source_suffix = {
    ".rst": "restructuredtext",
    ".md":  "markdown",
}

# MyST configuration — enable useful extensions
myst_enable_extensions = [
    "colon_fence",       # ::: fenced directives
    "deflist",           # definition lists
    "tasklist",          # - [x] task lists
    "smartquotes",       # curly quotes
    "strikethrough",
]
myst_heading_anchors = 3   # auto-anchor headings up to h3

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md"]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

html_static_path = ["_static"]

# -- Options for autosectionlabel --------------------------------------------

autosectionlabel_prefix_document = True
