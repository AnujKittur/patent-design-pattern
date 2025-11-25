"""
Script to search and retrieve patent data for civil construction machinery.
Uses USPTO API and provides search queries for other databases.
"""

import requests
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional

# USPTO Patent API endpoint
USPTO_API_BASE = "https://ped.uspto.gov/api/"

# Key Patent Classification Codes for Construction Machinery
CONSTRUCTION_MACHINERY_CLASSIFICATIONS = {
    "E02F": "Dredging; Excavating; Soil-shifting",
    "E02D": "Foundations; Excavations; Embankments",
    "E04G": "Scaffolding; Forms; Shuttering",
    "E04B": "General Building Constructions",
    "B66C": "Cranes; Load-Engaging Elements",
    "B25J": "Manipulators; Robots",
    "E01C": "Construction of Roads, Railways, or Airports",
    "E21B": "Earth Drilling",
    "E21C": "Mining or Quarrying"
}

# Search keywords for construction machinery
SEARCH_KEYWORDS = [
    "construction machinery",
    "construction equipment",
    "excavator",
    "bulldozer",
    "crane",
    "loader",
    "backhoe",
    "compactor",
    "paver",
    "concrete mixer",
    "construction robot",
    "earthmoving equipment",
    "road construction machinery",
    "building construction equipment"
]

def search_uspto_patents(query: str, start: int = 0, rows: int = 100) -> Optional[Dict]:
    """
    Search USPTO patents using their API.
    Note: USPTO API may require authentication for some endpoints.
    """
    try:
        # USPTO Patent Public Search API
        url = f"https://ped.uspto.gov/api/queries"
        
        # Query format for USPTO
        search_query = {
            "q": query,
            "start": start,
            "rows": rows,
            "fq": ["appEarlyPubNumber:[* TO *] OR appGrantNumber:[* TO *]"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(url, json=search_query, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"USPTO API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error searching USPTO: {e}")
        return None

def generate_search_queries() -> List[Dict]:
    """
    Generate search queries for construction machinery patents.
    """
    queries = []
    
    # Query 1: General construction machinery
    queries.append({
        "name": "General Construction Machinery",
        "query": 'TTL/(construction AND (machinery OR equipment OR machine))',
        "description": "Patents with construction machinery/equipment in title"
    })
    
    # Query 2: Specific machinery types
    queries.append({
        "name": "Excavators and Earthmoving",
        "query": 'TTL/(excavator OR bulldozer OR loader OR backhoe OR "earth moving")',
        "description": "Earthmoving and excavation equipment"
    })
    
    # Query 3: Cranes and Lifting Equipment
    queries.append({
        "name": "Cranes and Lifting",
        "query": 'TTL/(crane OR "lifting equipment" OR hoist) AND TTL/construction',
        "description": "Construction cranes and lifting equipment"
    })
    
    # Query 4: Road Construction Machinery
    queries.append({
        "name": "Road Construction Equipment",
        "query": 'TTL/(paver OR compactor OR "road construction" OR "asphalt")',
        "description": "Road construction and paving equipment"
    })
    
    # Query 5: Concrete Machinery
    queries.append({
        "name": "Concrete Equipment",
        "query": 'TTL/(("concrete mixer" OR "concrete pump" OR "concrete truck") AND construction)',
        "description": "Concrete mixing and handling equipment"
    })
    
    # Query 6: Construction Robotics
    queries.append({
        "name": "Construction Robotics",
        "query": 'TTL/(robot AND construction) OR TTL/("construction robot" OR "automated construction")',
        "description": "Robotic construction machinery"
    })
    
    # Query 7: By Classification Code - E02F (Excavating)
    queries.append({
        "name": "Excavating Equipment (E02F)",
        "query": 'ICL/E02F',
        "description": "Patents classified under E02F (Dredging; Excavating)"
    })
    
    # Query 8: By Classification Code - B66C (Cranes)
    queries.append({
        "name": "Cranes (B66C)",
        "query": 'ICL/B66C AND TTL/construction',
        "description": "Crane patents related to construction"
    })
    
    return queries

def create_patent_search_guide():
    """
    Create a comprehensive guide for searching construction machinery patents.
    """
    guide = {
        "title": "Construction Machinery Patent Search Guide",
        "created": datetime.now().isoformat(),
        "databases": {
            "USPTO": {
                "url": "https://patft.uspto.gov/",
                "advanced_search": "https://patft.uspto.gov/netahtml/PTO/search-adv.htm",
                "search_queries": generate_search_queries(),
                "classification_codes": CONSTRUCTION_MACHINERY_CLASSIFICATIONS
            },
            "Google_Patents": {
                "url": "https://patents.google.com/",
                "search_terms": SEARCH_KEYWORDS,
                "example_query": "construction machinery OR construction equipment"
            },
            "EPO_Espacenet": {
                "url": "https://worldwide.espacenet.com/",
                "classification_codes": {
                    "E02F": "Dredging; Excavating",
                    "E02D": "Foundations",
                    "B66C": "Cranes"
                }
            }
        }
    }
    
    return guide

def save_search_queries_to_file(queries: List[Dict], filename: str = "construction_machinery_patent_queries.json"):
    """
    Save search queries to a JSON file.
    """
    guide = create_patent_search_guide()
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(guide, f, indent=2, ensure_ascii=False)
    
    print(f"Search queries saved to {filename}")
    return filename

def create_search_instructions_csv():
    """
    Create a CSV file with search instructions for different databases.
    """
    instructions = []
    
    # USPTO Instructions
    for query in generate_search_queries():
        instructions.append({
            "Database": "USPTO",
            "Search_Type": query["name"],
            "Query": query["query"],
            "URL": "https://patft.uspto.gov/netahtml/PTO/search-adv.htm",
            "Instructions": f"Paste query in 'Query' field: {query['query']}",
            "Description": query["description"]
        })
    
    # Google Patents Instructions
    for keyword in SEARCH_KEYWORDS[:5]:  # Top 5 keywords
        instructions.append({
            "Database": "Google Patents",
            "Search_Type": "Keyword Search",
            "Query": keyword,
            "URL": "https://patents.google.com/",
            "Instructions": f"Search for: {keyword}",
            "Description": f"Patents related to {keyword}"
        })
    
    # Classification Code Searches
    for code, description in list(CONSTRUCTION_MACHINERY_CLASSIFICATIONS.items())[:5]:
        instructions.append({
            "Database": "USPTO/EPO",
            "Search_Type": "Classification Code",
            "Query": code,
            "URL": "https://patft.uspto.gov/",
            "Instructions": f"Search by classification code: {code}",
            "Description": description
        })
    
    # Save to CSV
    csv_filename = "construction_machinery_patent_search_instructions.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        if instructions:
            writer = csv.DictWriter(f, fieldnames=instructions[0].keys())
            writer.writeheader()
            writer.writerows(instructions)
    
    print(f"Search instructions saved to {csv_filename}")
    return csv_filename

def print_search_instructions():
    """
    Print search instructions to console.
    """
    print("\n" + "="*80)
    print("CONSTRUCTION MACHINERY PATENT SEARCH INSTRUCTIONS")
    print("="*80)
    
    print("\n1. USPTO PATENT SEARCH")
    print("-" * 80)
    print("URL: https://patft.uspto.gov/netahtml/PTO/search-adv.htm")
    print("\nRecommended Search Queries:")
    
    for i, query in enumerate(generate_search_queries(), 1):
        print(f"\n{i}. {query['name']}")
        print(f"   Query: {query['query']}")
        print(f"   Description: {query['description']}")
    
    print("\n\n2. GOOGLE PATENTS")
    print("-" * 80)
    print("URL: https://patents.google.com/")
    print("\nRecommended Search Terms:")
    for keyword in SEARCH_KEYWORDS:
        print(f"   - {keyword}")
    
    print("\n\n3. PATENT CLASSIFICATION CODES")
    print("-" * 80)
    print("Key Classification Codes for Construction Machinery:")
    for code, desc in CONSTRUCTION_MACHINERY_CLASSIFICATIONS.items():
        print(f"   {code}: {desc}")
    
    print("\n\n4. EPO ESPACENET")
    print("-" * 80)
    print("URL: https://worldwide.espacenet.com/")
    print("Search by classification codes or keywords")
    
    print("\n" + "="*80)

def main():
    """
    Main function to generate search resources.
    """
    print("Generating Construction Machinery Patent Search Resources...")
    
    # Create JSON guide
    json_file = save_search_queries_to_file(generate_search_queries())
    
    # Create CSV instructions
    csv_file = create_search_instructions_csv()
    
    # Print instructions
    print_search_instructions()
    
    print(f"\n✓ Resources created successfully!")
    print(f"  - {json_file}")
    print(f"  - {csv_file}")
    print("\nNote: For actual patent data retrieval, use the provided queries")
    print("      in the respective patent databases or their APIs.")

if __name__ == "__main__":
    main()





