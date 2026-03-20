# Research Workspace

This repository contains the research workspace for the project

**LLM Spatial Reasoning: Evaluating and Enhancing Geographic Cognition in Language Models.**

The repository will host materials related to:

- literature reviews and research notes
- experiment code
- benchmark implementations
- datasets used for evaluation
- documentation and project outputs


## Report Build System

The project report is written in **Markdown** and compiled using **Pandoc**.

A `Makefile` is provided to automate the process of merging all documentation and generating the final outputs.

## Build the report

To build all report formats:

```bash
make all
````

This generates:

```
build/spatial-ninjas-report.pdf
build/spatial-ninjas-report.html
```

You can also build individual formats:

```bash
make pdf
make html
```

Other useful commands:

```bash
make merge     # merge markdown sources into build/merged.md
make sources   # list detected markdown source files
make clean     # remove build artifacts
make help      # list available targets
```

The build pipeline:

1. discovers markdown files in the `docs/` directory
2. merges them into a single document
3. runs Pandoc to produce PDF and HTML outputs
4. formats citations using the IEEE CSL style


## Repository Structure

```
docs/                project documentation and literature summaries
  00-frontmatter/    report introduction and overview
  members/           paper summaries written by individual members
  shared/            synthesis and next steps written collaboratively
  99-backmatter/     references and appendix
template/            Pandoc LaTeX header and citation style
references.bib       shared bibliography database
report-metadata.yaml document metadata used by Pandoc
Makefile             report build automation
```

### Member summaries

Each project member writes their paper summary in:

```
docs/members/<name>/
```

These are automatically included in the report during the build process.

### Shared sections

Collaborative sections are stored in:

```
docs/shared/
```

Examples include:

* literature synthesis
* proposed next steps for experiments


## References

Bibliographic references used in the project are stored in:

```
references.bib
```

Citations inside markdown files use standard Pandoc citation syntax:

```
@paper_key
```

The final report is formatted using the **IEEE citation style**.


## Project Management

Task planning and sprint tracking are handled via the project board:

https://github.com/orgs/spatial-ninjas/projects/1
