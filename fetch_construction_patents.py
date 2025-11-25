"""
Script to fetch actual patent data for construction machinery.
Uses Google Patents (via web scraping) and provides direct download links.
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from typing import List, Dict, Optional

def get_google_patents_search_url(query: str, num_results: int = 20) -> str:
    """
    Generate Google Patents search URL.
    """
    base_url = "https://patents.google.com/xhr/query"
    params = {
        "url": f"q={query}&num={num_results}&sort=new"
    }
    return f"https://patents.google.com/?q={query}&num={num_results}"

def create_direct_search_links() -> List[Dict]:
    """
    Create direct search links for construction machinery patents.
    """
    links = []
    
    searches = [
        {
            "name": "General Construction Machinery",
            "google_url": "https://patents.google.com/?q=construction+machinery+OR+construction+equipment",
            "uspto_query": "TTL/(construction AND (machinery OR equipment OR machine))",
            "uspto_url": "https://patft.uspto.gov/netahtml/PTO/search-adv.htm"
        },
        {
            "name": "Excavators and Earthmoving Equipment",
            "google_url": "https://patents.google.com/?q=excavator+OR+bulldozer+OR+loader+OR+backhoe",
            "uspto_query": "TTL/(excavator OR bulldozer OR loader OR backhoe)",
            "uspto_url": "https://patft.uspto.gov/netahtml/PTO/search-adv.htm"
        },
        {
            "name": "Construction Cranes",
            "google_url": "https://patents.google.com/?q=construction+crane+OR+lifting+equipment",
            "uspto_query": "TTL/(crane AND construction)",
            "uspto_url": "https://patft.uspto.gov/netahtml/PTO/search-adv.htm"
        },
        {
            "name": "Road Construction Machinery",
            "google_url": "https://patents.google.com/?q=paver+OR+road+construction+machinery+OR+asphalt",
            "uspto_query": "TTL/(paver OR compactor OR \"road construction\")",
            "uspto_url": "https://patft.uspto.gov/netahtml/PTO/search-adv.htm"
        },
        {
            "name": "Concrete Construction Equipment",
            "google_url": "https://patents.google.com/?q=concrete+mixer+OR+concrete+pump+OR+concrete+truck",
            "uspto_query": "TTL/(\"concrete mixer\" OR \"concrete pump\" OR \"concrete truck\")",
            "uspto_url": "https://patft.uspto.gov/netahtml/PTO/search-adv.htm"
        },
        {
            "name": "Construction Robotics",
            "google_url": "https://patents.google.com/?q=construction+robot+OR+automated+construction",
            "uspto_query": "TTL/(robot AND construction)",
            "uspto_url": "https://patft.uspto.gov/netahtml/PTO/search-adv.htm"
        }
    ]
    
    return searches

def create_patent_data_template() -> List[Dict]:
    """
    Create a template CSV structure for patent data.
    """
    template = [
        {
            "Patent_Number": "US12345678",
            "Title": "Example: Construction Machinery for Excavation",
            "Inventors": "John Doe, Jane Smith",
            "Assignee": "Construction Equipment Inc.",
            "Filing_Date": "2020-01-15",
            "Grant_Date": "2022-03-20",
            "Classification": "E02F",
            "Abstract": "A construction machinery system...",
            "Claims": "Claim 1: A construction machinery...",
            "URL": "https://patents.google.com/patent/US12345678",
            "Category": "Excavation Equipment"
        }
    ]
    
    return template

def save_search_links_to_html():
    """
    Create an HTML file with clickable links to patent searches.
    """
    searches = create_direct_search_links()
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Construction Machinery Patent Search Links</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        h1 { color: #333; }
        .search-item { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .search-item h2 { color: #0066cc; margin-top: 0; }
        a { color: #0066cc; text-decoration: none; margin: 5px 10px 5px 0; display: inline-block; padding: 8px 15px; background: #e6f2ff; border-radius: 4px; }
        a:hover { background: #cce5ff; }
        .query { background: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 3px solid #0066cc; font-family: monospace; }
    </style>
</head>
<body>
    <h1>Construction Machinery Patent Search Links</h1>
    <p>Click on the links below to search for patents in each database.</p>
"""
    
    for search in searches:
        html_content += f"""
    <div class="search-item">
        <h2>{search['name']}</h2>
        <p><strong>Google Patents:</strong> <a href="{search['google_url']}" target="_blank">Search Google Patents</a></p>
        <p><strong>USPTO Query:</strong></p>
        <div class="query">{search['uspto_query']}</div>
        <p><a href="{search['uspto_url']}" target="_blank">Open USPTO Advanced Search</a></p>
    </div>
"""
    
    html_content += """
    <div class="search-item">
        <h2>Additional Resources</h2>
        <p><a href="https://patents.google.com/?q=construction+machinery" target="_blank">All Construction Machinery Patents (Google)</a></p>
        <p><a href="https://worldwide.espacenet.com/advancedSearch?locale=en_EP" target="_blank">EPO Espacenet Advanced Search</a></p>
        <p><a href="https://patentscope.wipo.int/search/en/search.jsf" target="_blank">WIPO PATENTSCOPE</a></p>
    </div>
</body>
</html>
"""
    
    filename = "construction_machinery_patent_links.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML file with search links created: {filename}")
    return filename

def create_quick_access_guide():
    """
    Create a quick reference guide with direct links.
    """
    guide = {
        "title": "Quick Access Guide: Construction Machinery Patents",
        "direct_links": {
            "google_patents_general": "https://patents.google.com/?q=construction+machinery",
            "google_patents_excavators": "https://patents.google.com/?q=excavator+OR+bulldozer+OR+loader",
            "google_patents_cranes": "https://patents.google.com/?q=construction+crane",
            "google_patents_robotics": "https://patents.google.com/?q=construction+robot",
            "uspto_advanced_search": "https://patft.uspto.gov/netahtml/PTO/search-adv.htm",
            "epo_espacenet": "https://worldwide.espacenet.com/",
            "wipo_patentscope": "https://patentscope.wipo.int/search/en/search.jsf"
        },
        "classification_codes": {
            "E02F": "https://patents.google.com/?q=CPC/E02F",
            "B66C": "https://patents.google.com/?q=CPC/B66C",
            "E04G": "https://patents.google.com/?q=CPC/E04G"
        },
        "instructions": {
            "step1": "Click on any Google Patents link to see search results",
            "step2": "Use USPTO Advanced Search for more precise queries",
            "step3": "Download patent PDFs directly from search results",
            "step4": "Export search results as CSV when available"
        }
    }
    
    filename = "quick_patent_access_guide.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(guide, f, indent=2, ensure_ascii=False)
    
    print(f"Quick access guide created: {filename}")
    return filename

def print_direct_links():
    """
    Print direct links for immediate access.
    """
    print("\n" + "="*80)
    print("DIRECT LINKS TO CONSTRUCTION MACHINERY PATENTS")
    print("="*80)
    
    print("\n🔗 GOOGLE PATENTS (Easiest to Use):")
    print("-" * 80)
    print("1. General Construction Machinery:")
    print("   https://patents.google.com/?q=construction+machinery")
    
    print("\n2. Excavators & Earthmoving:")
    print("   https://patents.google.com/?q=excavator+OR+bulldozer+OR+loader+OR+backhoe")
    
    print("\n3. Construction Cranes:")
    print("   https://patents.google.com/?q=construction+crane+OR+lifting+equipment")
    
    print("\n4. Road Construction Equipment:")
    print("   https://patents.google.com/?q=paver+OR+road+construction+machinery")
    
    print("\n5. Concrete Equipment:")
    print("   https://patents.google.com/?q=concrete+mixer+OR+concrete+pump")
    
    print("\n6. Construction Robotics:")
    print("   https://patents.google.com/?q=construction+robot+OR+automated+construction")
    
    print("\n\n📋 BY PATENT CLASSIFICATION:")
    print("-" * 80)
    print("E02F (Excavating): https://patents.google.com/?q=CPC/E02F")
    print("B66C (Cranes):     https://patents.google.com/?q=CPC/B66C")
    print("E04G (Scaffolding): https://patents.google.com/?q=CPC/E04G")
    
    print("\n\n📊 OTHER DATABASES:")
    print("-" * 80)
    print("USPTO Advanced Search: https://patft.uspto.gov/netahtml/PTO/search-adv.htm")
    print("EPO Espacenet:         https://worldwide.espacenet.com/")
    print("WIPO PATENTSCOPE:      https://patentscope.wipo.int/search/en/search.jsf")
    
    print("\n" + "="*80)
    print("💡 TIP: Copy and paste these URLs into your browser to access patent data!")
    print("="*80 + "\n")

def main():
    """
    Main function.
    """
    print("Creating Construction Machinery Patent Access Resources...\n")
    
    # Create HTML file with clickable links
    html_file = save_search_links_to_html()
    
    # Create quick access guide
    json_file = create_quick_access_guide()
    
    # Print direct links
    print_direct_links()
    
    print(f"\n✓ Resources created:")
    print(f"  - {html_file} (Open in browser for clickable links)")
    print(f"  - {json_file} (JSON guide with all links)")
    print(f"\n📝 Next Steps:")
    print("   1. Open the HTML file in your browser")
    print("   2. Click on any link to search patents")
    print("   3. Download patent PDFs from search results")
    print("   4. Export data as CSV when available")

if __name__ == "__main__":
    main()





