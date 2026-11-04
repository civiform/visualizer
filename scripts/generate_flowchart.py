#!/usr/bin/env python3
"""CLI utility to generate a standalone interactive USWDS flowchart HTML file from a CiviForm program export JSON.

Usage:
    python3 scripts/generate_flowchart.py input_program.json [-o output.html]
"""

import argparse
import html
import json
import os
import sys


def resolve_default_template(script_dir):
    repo_root = os.path.dirname(script_dir)
    candidates = [
        os.path.join(repo_root, "index.html"),
        os.path.join(repo_root, "assets", "civiform-flowchart-template.html"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    raise FileNotFoundError(
        "Could not locate visualizer HTML template (checked 'index.html' and 'assets/civiform-flowchart-template.html')."
    )


def generate_visualizer_html(json_data, template_path, output_path):
    if not isinstance(json_data, dict) or "program" not in json_data:
        raise ValueError("Invalid CiviForm JSON: missing 'program' root object.")

    prog = json_data["program"]
    blocks = prog.get("blockDefinitions", [])
    questions = json_data.get("questions", [])

    if not isinstance(blocks, list):
        raise ValueError("Invalid CiviForm JSON: 'program.blockDefinitions' must be an array.")

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Format JSON and prevent any embedded closing script tags from terminating the inline script block
    json_str = json.dumps(json_data, indent=2)
    json_str = json_str.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")

    # Replace placeholder CIVIFORM_PROGRAM_DATA
    start_marker = "/* START_CIVIFORM_PROGRAM_DATA */"
    end_marker = "/* END_CIVIFORM_PROGRAM_DATA */"
    start_idx = template_content.find(start_marker)
    end_idx = template_content.find(end_marker)

    if start_idx != -1 and end_idx != -1:
        replacement = (
            f"/* START_CIVIFORM_PROGRAM_DATA */\n"
            f"    let CIVIFORM_PROGRAM_DATA = {json_str};\n"
            f"    /* END_CIVIFORM_PROGRAM_DATA */"
        )
        new_html = template_content[:start_idx] + replacement + template_content[end_idx + len(end_marker):]
    else:
        marker = "let CIVIFORM_PROGRAM_DATA = {"
        start_idx = template_content.find(marker)
        if start_idx == -1:
            raise RuntimeError("Could not find CIVIFORM_PROGRAM_DATA marker in template HTML.")
        state_idx = template_content.find("const state = {", start_idx)
        if state_idx == -1:
            raise RuntimeError("Could not find const state marker in template HTML.")
        replacement = f"let CIVIFORM_PROGRAM_DATA = {json_str};\n\n    "
        new_html = template_content[:start_idx] + replacement + template_content[state_idx:]

    # Update document <title> with program localizedName if present
    name_obj = prog.get("localizedName", {}).get("translations", {})
    title = name_obj.get("en_US") or (list(name_obj.values())[0] if name_obj else "CiviForm Program")
    if title:
        escaped_title = html.escape(str(title))
        new_html = new_html.replace(
            "<title>CiviForm Program Visualizer</title>",
            f"<title>{escaped_title} — CiviForm Program Visualizer</title>",
        )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"Generated CiviForm flowchart visualization for '{title}':")
    print(f"  - Screens: {len(blocks)}")
    print(f"  - Questions: {len(questions)}")
    print(f"  - Output HTML: {os.path.abspath(output_path)}")


def main():
    parser = argparse.ArgumentParser(description="Generate USWDS CiviForm Flowchart Visualization HTML")
    parser.add_argument("json_file", help="Path to input CiviForm program export JSON")
    parser.add_argument("-o", "--output", help="Path to output HTML file (default: <input>_flowchart.html)", default=None)
    parser.add_argument("-t", "--template", help="Optional custom HTML template path", default=None)

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = args.template or resolve_default_template(script_dir)

    if not os.path.exists(args.json_file):
        print(f"Error: input file '{args.json_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or os.path.splitext(args.json_file)[0] + "_flowchart.html"

    try:
        with open(args.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        generate_visualizer_html(data, template_path, output_path)
    except Exception as e:
        print(f"Error generating flowchart: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
