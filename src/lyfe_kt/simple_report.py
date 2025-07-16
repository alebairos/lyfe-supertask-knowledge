#!/usr/bin/env python3
"""
Simple Supertask Report Generator

Generates focused reports on supertasks created, analyzing:
1. What supertasks were produced
2. Content quality and structure
3. Format compliance with input JSON
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to load {file_path}: {str(e)}"}


def analyze_supertask_content(input_data: Dict, output_data: Dict) -> Dict[str, Any]:
    """Analyze the content transformation from input to output"""
    analysis = {
        "title": output_data.get("title", "Unknown"),
        "topic": input_data.get("title", "Unknown"),
        "content_items": 0,
        "learning_objectives": [],
        "format_compliance": False,
        "missing_fields": []
    }
    
    # Count content items
    if "flexibleItems" in input_data:
        analysis["content_items"] = len(input_data["flexibleItems"])
    
    # Get learning objectives
    if "learning_objectives" in output_data:
        analysis["learning_objectives"] = output_data["learning_objectives"]
    
    # Check format compliance
    required_fields = ["title", "dimension", "archetype", "relatedToType", 
                      "relatedToId", "estimatedDuration", "coinsReward", "flexibleItems"]
    
    missing_fields = []
    for field in required_fields:
        if field not in output_data:
            missing_fields.append(field)
    
    analysis["missing_fields"] = missing_fields
    analysis["format_compliance"] = len(missing_fields) == 0
    
    return analysis


def generate_simple_report(input_dir: str, output_dir: str) -> str:
    """Generate a simple, focused report on supertasks created"""
    
    report_lines = [
        "# Supertask Analysis Report",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Input Directory**: {input_dir}",
        f"**Output Directory**: {output_dir}",
        "",
        "## Summary"
    ]
    
    # Find all input/output pairs
    supertasks = []
    total_files = 0
    compliant_files = 0
    
    if os.path.exists(input_dir) and os.path.exists(output_dir):
        for filename in os.listdir(input_dir):
            if filename.endswith('.json'):
                input_file = os.path.join(input_dir, filename)
                output_file = os.path.join(output_dir, filename)
                
                if os.path.exists(output_file):
                    total_files += 1
                    input_data = load_json_file(input_file)
                    output_data = load_json_file(output_file)
                    
                    if "error" not in input_data and "error" not in output_data:
                        analysis = analyze_supertask_content(input_data, output_data)
                        supertasks.append({
                            "filename": filename,
                            "input_file": input_file,
                            "output_file": output_file,
                            "analysis": analysis
                        })
                        
                        if analysis["format_compliance"]:
                            compliant_files += 1
    
    # Add summary stats
    report_lines.extend([
        f"- **Total Files Processed**: {total_files}",
        f"- **Supertasks Created**: {len(supertasks)}",
        f"- **Format Compliant**: {compliant_files}/{total_files}",
        f"- **Success Rate**: {(len(supertasks)/total_files*100):.1f}%" if total_files > 0 else "- **Success Rate**: 0%",
        "",
        "## Supertasks Created"
    ])
    
    # Add details for each supertask
    for i, task in enumerate(supertasks, 1):
        analysis = task["analysis"]
        report_lines.extend([
            f"### {i}. \"{analysis['title']}\"",
            f"- **Source**: `{task['input_file']}`",
            f"- **Output**: `{task['output_file']}`",
            f"- **Topic**: {analysis['topic']}",
            f"- **Content Items**: {analysis['content_items']}",
            f"- **Learning Objectives**: {len(analysis['learning_objectives'])}",
            ""
        ])
        
        # Add learning objectives if present
        if analysis['learning_objectives']:
            report_lines.append("**Learning Objectives**:")
            for obj in analysis['learning_objectives']:
                report_lines.append(f"- {obj}")
            report_lines.append("")
    
    # Add format compliance section
    report_lines.extend([
        "## Format Compliance Analysis",
        ""
    ])
    
    compliant_count = sum(1 for task in supertasks if task["analysis"]["format_compliance"])
    non_compliant_count = len(supertasks) - compliant_count
    
    if compliant_count > 0:
        report_lines.append(f"### ✅ Compliant Files: {compliant_count}")
    
    if non_compliant_count > 0:
        report_lines.extend([
            f"### ❌ Non-Compliant Files: {non_compliant_count}",
            ""
        ])
        
        for task in supertasks:
            analysis = task["analysis"]
            if not analysis["format_compliance"]:
                report_lines.extend([
                    f"**{task['filename']}** - Missing fields:",
                    ""
                ])
                for field in analysis["missing_fields"]:
                    report_lines.append(f"- `{field}`")
                report_lines.append("")
    
    # Add recommendations
    report_lines.extend([
        "## Recommendations",
        ""
    ])
    
    if non_compliant_count > 0:
        report_lines.extend([
            "### Critical Issues",
            "- **Fix JSON Format**: Output files must maintain exact input structure",
            "- **Preserve Required Fields**: Keep all original metadata fields",
            "- **Enhance Within Structure**: Transform content inside `flexibleItems` array",
            ""
        ])
    
    report_lines.extend([
        "### Next Steps",
        "1. Review format compliance issues",
        "2. Test with multiple input files",
        "3. Validate content quality",
        "4. Ensure template structure consistency"
    ])
    
    return "\n".join(report_lines)


def main():
    """Main function for CLI usage"""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python simple_report.py <input_dir> <output_dir>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    report = generate_simple_report(input_dir, output_dir)
    print(report)


if __name__ == "__main__":
    main() 