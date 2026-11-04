# CiviForm Program Visualizer

A standalone, zero-build U.S. Web Design System (USWDS v3) web application and CLI utility that transforms CiviForm program export JSON files into interactive vertical application flowcharts.

## Features

- **Program Overview & Application Steps**: Renders the `"Apply for <Program> program"` introduction card (extracting optional warning/notice callouts) and numbered `"How to apply"` process steps above the `Start application` node.
- **Screen Cards & Sticky Outline**: Displays screens in sequential order with localized question prompts, required indicators, `Universal Question` badges, `Enumerator` / `Controls Visibility` / `Controls Eligibility` tags, collapsible answer option pills, and a collapsible sticky `Screens` outline sidebar.
- **Eligibility Gating & Non-Gating Forks**: Connects eligibility-triggering questions via horizontal Bezier curves to side-by-side Pass (`Continue if ...`) and Stop / Warning (`Stopped if ...`) outcome cards.
- **Conditional Visibility & Parallel Branch Routing**: Automatically distinguishes mutually exclusive, exhaustive single-question parallel splits (rendered inline side-by-side beneath a routing header) from conditional follow-up screens (placed on the right and linked via dark gold dotted SVG curves from their trigger questions), with recursive `AND` / `OR` and `HIDE_BLOCK` inversion formatting.
- **Enumerator Repeater Containers**: Wraps repeated screens in dashed repeater containers linked to their parent enumerator screen.
- **Interactive Applicant Flow Simulation & Multi-Locale Switching**: Toggle **Simulate applicant flow** to test answers, eligibility gates, conditional branches, and repeater counts with live active-journey breadcrumbs, switch between locales defined in the export JSON, edit JSON live, or export/print (`Print / export PDF`).

## Usage

### 1. In the Browser (or GitHub Pages)

`index.html` is a self-contained single-file HTML/CSS/JS application using USWDS v3.13.0 via CDN—no build step or backend server is required:

1. Open `index.html` directly in your browser (or serve the repository root with any static server, e.g. `python3 -m http.server 8000`, or enable GitHub Pages on `main`).
2. Paste any CiviForm program export JSON (exported from `/admin/programs` in CiviForm) into the textarea—or drag and drop a `.json` file onto the window—and click **Generate visualization**.

### 2. Generate Pre-Baked Standalone HTML via CLI

You can also pre-inject a CiviForm program JSON file into a portable, shareable single-file HTML document using Python 3 (standard library only):

```bash
python3 scripts/generate_flowchart.py path/to/program.json -o program_flowchart.html
```

Opening `program_flowchart.html` launches directly into the rendered flowchart for that program while still allowing you to click **Input new JSON** or drag-and-drop another JSON file at any time.

## Repository Structure

```
visualizer/
├── index.html                        # Standalone interactive USWDS v3 visualizer web app & template
├── README.md
├── LICENSE
├── .gitignore
├── scripts/
│   └── generate_flowchart.py         # CLI utility to bake a program JSON into a standalone HTML file
└── references/
    └── civiform-json-schema.md       # CiviForm program export JSON schema & predicate AST reference
```
