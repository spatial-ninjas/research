# ---------- Config ----------
PANDOC       := pandoc
PDF_ENGINE   := xelatex

BUILD_DIR    := build
DOCS_DIR     := docs
TEMPLATE_DIR := template

METADATA     := report-metadata.yaml
HEADER       := $(TEMPLATE_DIR)/header.tex
BIB_FILE     := references.bib
CSL_FILE     := $(TEMPLATE_DIR)/ieee.csl

MERGED_MD    := $(BUILD_DIR)/merged.md
PDF_OUTPUT   := $(BUILD_DIR)/spatial-ninjas-report.pdf
HTML_OUTPUT  := $(BUILD_DIR)/spatial-ninjas-report.html

# ---------- Source discovery ----------
FRONTMATTER  := $(sort $(wildcard $(DOCS_DIR)/00-frontmatter/*.md))
MEMBER_NOTES := $(sort $(wildcard $(DOCS_DIR)/members/*/*.md))
SHARED_NOTES := $(sort $(wildcard $(DOCS_DIR)/shared/*.md))
BACKMATTER   := $(sort $(wildcard $(DOCS_DIR)/99-backmatter/*.md))

SOURCES      := $(FRONTMATTER) $(MEMBER_NOTES) $(SHARED_NOTES) $(BACKMATTER)

# ---------- Pandoc flags ----------
PANDOC_COMMON_FLAGS := \
	--from=markdown \
	--standalone \
	--citeproc \
	--metadata-file=$(METADATA) \
	--bibliography=$(BIB_FILE) \
	--metadata=date:"$(shell date "+%B %-d, %Y")" \
	--csl=$(CSL_FILE) \
	--resource-path=.:$(DOCS_DIR):$(TEMPLATE_DIR):$(BUILD_DIR) \
	--toc \
	--number-sections

PANDOC_PDF_FLAGS := \
	$(PANDOC_COMMON_FLAGS) \
	--include-in-header=$(HEADER)

PANDOC_HTML_FLAGS := \
	$(PANDOC_COMMON_FLAGS)

# ---------- Targets ----------
.PHONY: help all pdf html merge clean sources check

help: ## Show available make targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "%-15s %s\n", $$1, $$2}'

all: pdf html ## Build all output formats

check: ## Verify required files exist
	@test -f $(METADATA) || (echo "Missing $(METADATA)"; exit 1)
	@test -f $(HEADER) || (echo "Missing $(HEADER)"; exit 1)
	@test -f $(BIB_FILE) || (echo "Missing $(BIB_FILE)"; exit 1)
	@test -f $(CSL_FILE) || (echo "Missing $(CSL_FILE)"; exit 1)

pdf: $(PDF_OUTPUT) ## Build PDF report

$(PDF_OUTPUT): check $(MERGED_MD) $(METADATA) $(HEADER) $(BIB_FILE) $(CSL_FILE)
	$(PANDOC) $(MERGED_MD) \
		$(PANDOC_PDF_FLAGS) \
		--pdf-engine=$(PDF_ENGINE) \
		-o $(PDF_OUTPUT)

html: $(HTML_OUTPUT) ## Build HTML report

$(HTML_OUTPUT): check $(MERGED_MD) $(METADATA) $(BIB_FILE) $(CSL_FILE)
	$(PANDOC) $(MERGED_MD) \
		$(PANDOC_HTML_FLAGS) \
		-o $(HTML_OUTPUT)

merge: $(MERGED_MD) ## Merge markdown sources into a single file

$(MERGED_MD): $(SOURCES) | $(BUILD_DIR)
	@echo "Merging markdown sources..."
	@rm -f $(MERGED_MD)
	@for f in $(SOURCES); do \
		echo "Adding $$f"; \
		cat $$f >> $(MERGED_MD); \
		printf '\n\n' >> $(MERGED_MD); \
	done

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

sources: ## Print detected markdown source files
	@printf '%s\n' $(SOURCES)

clean: ## Remove build artifacts
	rm -rf $(BUILD_DIR)
