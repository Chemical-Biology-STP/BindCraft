# Minimal Sphinx Makefile
# Uses pixi to ensure sphinx-build is always available.
# Run from the BindCraft root or docs/ directory.

PIXI        = $(HOME)/.pixi/bin/pixi
SOURCEDIR   = .
BUILDDIR    = _build

.PHONY: help html clean

help:
	@echo "Usage:"
	@echo "  make html     Build HTML documentation"
	@echo "  make clean    Remove build output"

html:
	$(PIXI) run sphinx-build -b html "$(SOURCEDIR)" "$(BUILDDIR)/html"
	@echo ""
	@echo "Build complete. Open $(BUILDDIR)/html/index.html to view."

clean:
	@rm -rf $(BUILDDIR)
	@echo "Build directory cleaned."
