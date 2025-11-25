"""
CLI interface for construction robotics design generation.
"""

import argparse
import json
import requests
import sys
from typing import Optional, List
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"


def print_design_brief(design: dict):
    """Pretty print design brief."""
    print("\n" + "=" * 80)
    print("DESIGN BRIEF")
    print("=" * 80)
    
    print(f"\n📋 OVERVIEW:\n{design.get('overview', 'N/A')}\n")
    
    print("🔧 MODULES:")
    for module in design.get("modules", []):
        print(f"  • {module.get('name', 'N/A')}: {module.get('function', 'N/A')}")
        if module.get("citations"):
            print(f"    Citations: {', '.join(module['citations'])}")
    
    print("\n⚙️ ACTUATION:")
    for actuation in design.get("actuation", []):
        print(f"  • {actuation.get('subsystem', 'N/A')}: {actuation.get('choice', 'N/A')}")
        print(f"    Why: {actuation.get('why', 'N/A')}")
        if actuation.get("citations"):
            print(f"    Citations: {', '.join(actuation['citations'])}")
    
    print("\n👁️ SENSING:")
    for sensing in design.get("sensing", []):
        print(f"  • {sensing.get('subsystem', 'N/A')}: {', '.join(sensing.get('sensors', []))}")
        print(f"    Why: {sensing.get('why', 'N/A')}")
        if sensing.get("citations"):
            print(f"    Citations: {', '.join(sensing['citations'])}")
    
    print("\n🎮 CONTROL:")
    for control in design.get("control", []):
        print(f"  • {control.get('layer', 'N/A')}: {control.get('approach', 'N/A')} ({control.get('teleop_or_auto', 'N/A')})")
        if control.get("citations"):
            print(f"    Citations: {', '.join(control['citations'])}")
    
    print("\n🧱 MATERIALS:")
    for material in design.get("materials", []):
        print(f"  • {material.get('part', 'N/A')}: {material.get('material', 'N/A')}")
        print(f"    Why: {material.get('why', 'N/A')}")
        if material.get("citations"):
            print(f"    Citations: {', '.join(material['citations'])}")
    
    print("\n🛡️ SAFETY:")
    for safety in design.get("safety", []):
        print(f"  • Risk: {safety.get('risk', 'N/A')}")
        print(f"    Mitigation: {safety.get('mitigation', 'N/A')}")
        if safety.get("citations"):
            print(f"    Citations: {', '.join(safety['citations'])}")
    
    print("\n📝 PROCEDURE:")
    for i, step in enumerate(design.get("procedure", []), 1):
        print(f"  {i}. {step}")
    
    print("\n💰 BILL OF MATERIALS:")
    total_cost = 0
    for item in design.get("bom", []):
        qty = item.get("qty", 1)
        cost = item.get("est_cost_usd", 0)
        total = qty * cost
        total_cost += total
        print(f"  • {item.get('item', 'N/A')}: {qty} x ${cost:.2f} = ${total:.2f}")
        if item.get("citations"):
            print(f"    Citations: {', '.join(item['citations'])}")
    print(f"\n  Total Estimated Cost: ${total_cost:.2f}")
    
    print("\n📚 CITATIONS:")
    for citation in design.get("citations", []):
        print(f"  • {citation.get('patent_number', 'N/A')}: {citation.get('title', 'N/A')}")
        print(f"    URL: {citation.get('url', 'N/A')}")
        print(f"    Reason: {citation.get('reason', 'N/A')}")
    
    print("\n" + "=" * 80)


def generate_design(
    prompt: str,
    filters: Optional[dict] = None,
    api_url: str = API_URL
) -> dict:
    """Generate design brief from API."""
    url = f"{api_url}/design"
    payload = {
        "prompt": prompt,
        "filters": filters or {}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        print("Make sure the FastAPI server is running: python app.py")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Construction Robotics Design Generator CLI"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Design specification prompt"
    )
    parser.add_argument(
        "--cpc",
        nargs="+",
        help="CPC codes to filter (e.g., B25J E04G)"
    )
    parser.add_argument(
        "--year-min",
        type=int,
        help="Minimum year filter"
    )
    parser.add_argument(
        "--year-max",
        type=int,
        help="Maximum year filter"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default=API_URL,
        help="API URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file path"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of pretty print"
    )
    
    args = parser.parse_args()
    
    # Build filters
    filters = {}
    if args.cpc:
        filters["cpc"] = args.cpc
    if args.year_min:
        filters["year_min"] = args.year_min
    if args.year_max:
        filters["year_max"] = args.year_max
    
    # Generate design
    print(f"Generating design for: {args.prompt}")
    if filters:
        print(f"Filters: {filters}")
    
    design = generate_design(args.prompt, filters, args.api_url)
    
    # Output
    if args.json:
        output = json.dumps(design, indent=2)
        print(output)
    else:
        print_design_brief(design)
    
    # Save to file if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(design, f, indent=2)
        print(f"\nDesign saved to: {args.output}")


if __name__ == "__main__":
    main()



