"""
Script to download construction machinery patent data using multiple methods.
Provides instructions and sample queries for manual download.
"""

import csv
import json
from datetime import datetime
from typing import List, Dict

def create_search_queries():
    """
    Generate search queries for different patent databases.
    """
    queries = {
        "uspto_queries": [
            "CPC/E04G AND TTL/construction",
            "CPC/E04B AND TTL/machinery",
            "CPC/B66C AND TTL/construction",
            "TTL/construction AND TTL/machinery",
            "TTL/construction AND TTL/equipment",
            "TTL/excavator OR TTL/bulldozer OR TTL/crane",
            "TTL/construction AND TTL/robot",
            "CPC/E04G AND ABST/automated",
            "CPC/B25J AND ABST/construction"
        ],
        "epo_queries": [
            "CPC=E04G",
            "CPC=E04B",
            "CPC=B66C",
            'TI="construction machinery"',
            'TI="construction equipment"',
            'AB="construction robot"'
        ],
        "google_patents_queries": [
            "CPC/E04G construction",
            "CPC/E04B machinery",
            "CPC/B66C construction",
            '"construction machinery"',
            '"construction equipment"',
            '"construction robot"',
            "excavator OR bulldozer OR crane"
        ],
        "cpc_codes": [
            "E04G - Scaffolding; Forms; Shuttering",
            "E04B - General Building Constructions",
            "E04C - Building Elements",
            "E04D - Roof Coverings",
            "E04F - Finishing Work on Buildings",
            "E04H - Buildings or Like Structures",
            "B66C - Cranes; Load-Engaging Elements",
            "B66F - Hoisting, Lifting, Hauling or Pushing",
            "E02D - Foundations; Excavations",
            "E02F - Earth Drilling; Mining",
            "B25J - Manipulators (Construction Robotics)"
        ]
    }
    return queries


def generate_uspto_bulk_download_guide():
    """
    Generate guide for downloading from USPTO bulk data.
    """
    guide = """
    USPTO BULK DATA DOWNLOAD GUIDE
    ===============================
    
    1. Visit: https://bulkdata.uspto.gov/
    
    2. Navigate to Patent Grant Data:
       https://bulkdata.uspto.gov/data/patent/grant/redbook/bibliographic/
    
    3. Download XML files (organized by year/quarter)
    
    4. Filter for Construction Machinery CPC Codes:
       - E04G (Scaffolding)
       - E04B (Building Constructions)
       - E04C (Building Elements)
       - B66C (Cranes)
       - B66F (Hoisting)
       - E02D (Foundations)
       - E02F (Earth Drilling)
       - B25J (Robotics)
    
    5. Parse XML files to extract patents with these CPC codes
    
    Example XML Structure:
    <us-patent-grant>
      <us-bibliographic-data-grant>
        <classification-ipc>
          <main-classification>E04G 21/00</main-classification>
        </classification-ipc>
      </us-bibliographic-data-grant>
    </us-patent-grant>
    """
    return guide


def create_sample_patent_template():
    """
    Create a template showing what patent data fields to collect.
    """
    template = {
        "patent_number": "",
        "title": "",
        "publication_date": "",
        "application_date": "",
        "abstract": "",
        "description": "",
        "claims": "",
        "cpc_classification": [],
        "ipc_classification": [],
        "inventors": [],
        "assignees": [],
        "cited_patents": [],
        "cited_by_patents": [],
        "patent_family": []
    }
    return template


def save_search_instructions(queries: Dict, filename: str = "patent_search_instructions.json"):
    """
    Save search queries and instructions to JSON file.
    """
    instructions = {
        "generated_date": datetime.now().isoformat(),
        "search_queries": queries,
        "uspto_bulk_download": generate_uspto_bulk_download_guide(),
        "sample_template": create_sample_patent_template(),
        "direct_links": {
            "uspto_search": "https://ppubs.uspto.gov/pubwebapp/",
            "uspto_advanced": "https://ppubs.uspto.gov/pubwebapp/static/pages/landing.html#search",
            "uspto_bulk_data": "https://bulkdata.uspto.gov/",
            "epo_espacenet": "https://worldwide.espacenet.com/",
            "epo_advanced": "https://worldwide.espacenet.com/advancedSearch?locale=en_EP",
            "wipo_patentscope": "https://patentscope.wipo.int/search/en/search.jsf",
            "google_patents": "https://patents.google.com/",
            "google_patents_advanced": "https://patents.google.com/advanced"
        },
        "recommended_approach": [
            "1. Start with USPTO Bulk Data for comprehensive dataset",
            "2. Use EPO Espacenet for European patents",
            "3. Use Google Patents for citation analysis",
            "4. Filter by CPC codes: E04G, E04B, B66C, E02F, B25J",
            "5. Search keywords: construction machinery, construction equipment, construction robot"
        ]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(instructions, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Search instructions saved to {filename}")
    return instructions


def create_csv_template(filename: str = "construction_patents_template.csv"):
    """
    Create a CSV template for storing patent data.
    """
    headers = [
        "Patent_Number",
        "Title",
        "Publication_Date",
        "Application_Date",
        "Abstract",
        "CPC_Classification",
        "IPC_Classification",
        "Inventors",
        "Assignee",
        "Cited_Patents",
        "Patent_URL",
        "Source_Database"
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
    
    print(f"✓ CSV template created: {filename}")
    return filename


def print_search_instructions(queries: Dict):
    """
    Print formatted search instructions.
    """
    print("\n" + "="*70)
    print("CONSTRUCTION MACHINERY PATENT SEARCH INSTRUCTIONS")
    print("="*70)
    
    print("\n1. USPTO SEARCH QUERIES:")
    print("-" * 70)
    for i, query in enumerate(queries["uspto_queries"], 1):
        print(f"   {i}. {query}")
    
    print("\n2. EPO ESPACENET QUERIES:")
    print("-" * 70)
    for i, query in enumerate(queries["epo_queries"], 1):
        print(f"   {i}. {query}")
    
    print("\n3. GOOGLE PATENTS QUERIES:")
    print("-" * 70)
    for i, query in enumerate(queries["google_patents_queries"], 1):
        print(f"   {i}. {query}")
    
    print("\n4. KEY CPC CLASSIFICATION CODES:")
    print("-" * 70)
    for code in queries["cpc_codes"]:
        print(f"   • {code}")
    
    print("\n5. DIRECT DATABASE LINKS:")
    print("-" * 70)
    links = {
        "USPTO Patent Search": "https://ppubs.uspto.gov/pubwebapp/",
        "USPTO Bulk Data": "https://bulkdata.uspto.gov/",
        "EPO Espacenet": "https://worldwide.espacenet.com/",
        "WIPO PATENTSCOPE": "https://patentscope.wipo.int/search/en/search.jsf",
        "Google Patents": "https://patents.google.com/"
    }
    for name, url in links.items():
        print(f"   {name}: {url}")
    
    print("\n" + "="*70)
    print("RECOMMENDED DOWNLOAD METHOD:")
    print("="*70)
    print("""
    For large-scale data collection:
    
    1. USPTO Bulk Data Download (Best for comprehensive dataset):
       - Visit: https://bulkdata.uspto.gov/
       - Download: Patent Grant Bibliographic Data
       - Filter XML files for CPC codes: E04G, E04B, B66C, E02F, B25J
       
    2. Manual Search & Export (Best for specific patents):
       - Use USPTO Patent Public Search: https://ppubs.uspto.gov/pubwebapp/
       - Use EPO Espacenet: https://worldwide.espacenet.com/
       - Export individual patents or use browser automation
       
    3. Google Patents (Best for citation analysis):
       - Visit: https://patents.google.com/
       - Search with CPC codes or keywords
       - Use browser extensions for bulk export
    """)


def main():
    """
    Main function to generate search instructions and templates.
    """
    print("Generating Construction Machinery Patent Search Resources...")
    
    # Generate queries
    queries = create_search_queries()
    
    # Print instructions
    print_search_instructions(queries)
    
    # Save to files
    instructions = save_search_instructions(queries)
    csv_template = create_csv_template()
    
    print("\n" + "="*70)
    print("FILES CREATED:")
    print("="*70)
    print(f"✓ patent_search_instructions.json - Complete search guide")
    print(f"✓ construction_patents_template.csv - CSV template for data")
    print("\nNext Steps:")
    print("1. Review patent_search_instructions.json for all queries and links")
    print("2. Use the CSV template to organize downloaded patent data")
    print("3. Start with USPTO Bulk Data for the largest dataset")
    print("4. Use manual search for specific patent types")


if __name__ == "__main__":
    main()

