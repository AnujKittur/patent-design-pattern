"""
Script to download patent data for construction machinery and civil construction machines.
Uses USPTO PatentsView API and other available sources.
"""

import requests
import json
import csv
import time
from typing import List, Dict
from datetime import datetime

# USPTO PatentsView API endpoint
PATENTSVIEW_API = "https://api.patentsview.org/patents/query"

# Construction machinery related CPC codes
CONSTRUCTION_MACHINERY_CPC_CODES = [
    "E04G",  # Scaffolding; Forms; Shuttering
    "E04B",  # General Building Constructions
    "E04C",  # Building Elements
    "E04D",  # Roof Coverings
    "E04F",  # Finishing Work on Buildings
    "E04H",  # Buildings or Like Structures
    "B66C",  # Cranes; Load-Engaging Elements
    "B66F",  # Hoisting, Lifting, Hauling or Pushing
    "E02D",  # Foundations; Excavations
    "E02F",  # Earth Drilling; Mining
    "E21B",  # Earth Drilling
    "B25J",  # Manipulators (robotics for construction)
]

# Search keywords for construction machinery
CONSTRUCTION_KEYWORDS = [
    "construction machinery",
    "construction equipment",
    "construction machine",
    "building machinery",
    "civil construction",
    "excavator",
    "bulldozer",
    "crane",
    "concrete mixer",
    "construction robot",
    "automated construction",
    "bricklaying machine",
    "construction vehicle"
]


def search_patents_patentsview(query_fields: Dict, max_results: int = 100) -> List[Dict]:
    """
    Search patents using PatentsView API.
    
    Args:
        query_fields: Dictionary with query parameters
        max_results: Maximum number of results to return
    
    Returns:
        List of patent records
    """
    url = PATENTSVIEW_API
    
    # Build query
    query = {
        "q": query_fields,
        "f": [
            "patent_number",
            "patent_title",
            "patent_date",
            "patent_abstract",
            "patent_type",
            "cited_patent_number",
            "cited_patent_title",
            "cited_patent_date",
            "inventor_first_name",
            "inventor_last_name",
            "assignee_organization",
            "cpc_subsection_id",
            "cpc_group_id",
            "cpc_subgroup_id"
        ],
        "o": {
            "per_page": min(max_results, 10000),
            "page": 1
        }
    }
    
    try:
        print(f"Searching PatentsView API...")
        response = requests.post(url, json=query, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        patents = data.get('patents', [])
        print(f"Found {len(patents)} patents")
        
        return patents
    
    except requests.exceptions.RequestException as e:
        print(f"Error querying PatentsView API: {e}")
        return []


def search_by_cpc_codes(cpc_codes: List[str], max_results: int = 1000) -> List[Dict]:
    """
    Search patents by CPC classification codes.
    """
    # Build query for CPC codes
    cpc_query = {
        "_or": [
            {"cpc_subsection_id": {"_eq": code}} for code in cpc_codes
        ]
    }
    
    return search_patents_patentsview(cpc_query, max_results)


def search_by_keywords(keywords: List[str], max_results: int = 1000) -> List[Dict]:
    """
    Search patents by keywords in title and abstract.
    """
    # Build query for keywords
    keyword_query = {
        "_or": [
            {
                "_or": [
                    {"patent_title": {"_contains": keyword}},
                    {"patent_abstract": {"_contains": keyword}}
                ]
            } for keyword in keywords
        ]
    }
    
    return search_patents_patentsview(keyword_query, max_results)


def combine_searches(cpc_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
    """
    Combine results from multiple searches and remove duplicates.
    """
    seen_patents = set()
    combined = []
    
    for patent in cpc_results + keyword_results:
        patent_num = patent.get('patent_number', '')
        if patent_num and patent_num not in seen_patents:
            seen_patents.add(patent_num)
            combined.append(patent)
    
    return combined


def save_to_csv(patents: List[Dict], filename: str = "construction_machinery_patents.csv"):
    """
    Save patent data to CSV file.
    """
    if not patents:
        print("No patents to save.")
        return
    
    # Extract relevant fields
    rows = []
    for patent in patents:
        row = {
            'Patent Number': patent.get('patent_number', ''),
            'Title': patent.get('patent_title', ''),
            'Date': patent.get('patent_date', ''),
            'Abstract': patent.get('patent_abstract', ''),
            'Type': patent.get('patent_type', ''),
            'CPC Subsection': ', '.join(patent.get('cpc_subsection_id', [])),
            'CPC Group': ', '.join(patent.get('cpc_group_id', [])),
            'Inventors': ', '.join([
                f"{inv.get('inventor_first_name', '')} {inv.get('inventor_last_name', '')}"
                for inv in patent.get('inventors', [])
            ]),
            'Assignee': ', '.join([
                org.get('assignee_organization', '')
                for org in patent.get('assignees', [])
            ]),
            'Cited Patents': ', '.join(patent.get('cited_patent_number', []))
        }
        rows.append(row)
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"Saved {len(rows)} patents to {filename}")


def save_to_json(patents: List[Dict], filename: str = "construction_machinery_patents.json"):
    """
    Save patent data to JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(patents, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(patents)} patents to {filename}")


def generate_search_report(patents: List[Dict]):
    """
    Generate a summary report of the search results.
    """
    print("\n" + "="*60)
    print("CONSTRUCTION MACHINERY PATENTS SEARCH REPORT")
    print("="*60)
    print(f"Total Patents Found: {len(patents)}")
    
    if patents:
        # Count by year
        years = {}
        for patent in patents:
            date = patent.get('patent_date', '')
            if date:
                year = date[:4]
                years[year] = years.get(year, 0) + 1
        
        print("\nPatents by Year:")
        for year in sorted(years.keys()):
            print(f"  {year}: {years[year]}")
        
        # Top CPC codes
        cpc_counts = {}
        for patent in patents:
            for cpc in patent.get('cpc_subsection_id', []):
                cpc_counts[cpc] = cpc_counts.get(cpc, 0) + 1
        
        print("\nTop CPC Classifications:")
        for cpc, count in sorted(cpc_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {cpc}: {count} patents")
        
        # Top assignees
        assignee_counts = {}
        for patent in patents:
            for assignee in patent.get('assignees', []):
                org = assignee.get('assignee_organization', '')
                if org:
                    assignee_counts[org] = assignee_counts.get(org, 0) + 1
        
        print("\nTop Assignees:")
        for org, count in sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {org}: {count} patents")
    
    print("="*60 + "\n")


def main():
    """
    Main function to search and download construction machinery patents.
    """
    print("Starting Construction Machinery Patents Search...")
    print(f"Search started at: {datetime.now()}")
    
    # Search by CPC codes
    print("\n1. Searching by CPC Classification Codes...")
    cpc_patents = search_by_cpc_codes(CONSTRUCTION_MACHINERY_CPC_CODES, max_results=5000)
    print(f"Found {len(cpc_patents)} patents via CPC codes")
    
    # Add delay to avoid rate limiting
    time.sleep(2)
    
    # Search by keywords
    print("\n2. Searching by Keywords...")
    keyword_patents = search_by_keywords(CONSTRUCTION_KEYWORDS, max_results=5000)
    print(f"Found {len(keyword_patents)} patents via keywords")
    
    # Combine results
    print("\n3. Combining and deduplicating results...")
    all_patents = combine_searches(cpc_patents, keyword_patents)
    print(f"Total unique patents: {len(all_patents)}")
    
    # Generate report
    generate_search_report(all_patents)
    
    # Save results
    if all_patents:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"construction_machinery_patents_{timestamp}.csv"
        json_filename = f"construction_machinery_patents_{timestamp}.json"
        
        print("\n4. Saving results...")
        save_to_csv(all_patents, csv_filename)
        save_to_json(all_patents, json_filename)
        
        print(f"\n✓ Search complete! Results saved to:")
        print(f"  - {csv_filename}")
        print(f"  - {json_filename}")
    else:
        print("\n⚠ No patents found. Please check your search criteria.")
    
    return all_patents


if __name__ == "__main__":
    # Run the search
    patents = main()
    
    # Print sample results
    if patents:
        print("\n" + "="*60)
        print("SAMPLE PATENTS (First 5):")
        print("="*60)
        for i, patent in enumerate(patents[:5], 1):
            print(f"\n{i}. Patent #{patent.get('patent_number', 'N/A')}")
            print(f"   Title: {patent.get('patent_title', 'N/A')}")
            print(f"   Date: {patent.get('patent_date', 'N/A')}")
            print(f"   CPC: {', '.join(patent.get('cpc_subsection_id', [])[:3])}")
            abstract = patent.get('patent_abstract', '')
            if abstract:
                print(f"   Abstract: {abstract[:200]}...")

