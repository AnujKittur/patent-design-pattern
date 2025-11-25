# How to Download Construction Machinery Patent Data

## Quick Start

Run the Python script to automatically search and download construction machinery patents:

```bash
python3 download_construction_machinery_patents.py
```

## What the Script Does

1. **Searches by CPC Classification Codes** - Uses construction-related patent classification codes
2. **Searches by Keywords** - Searches patent titles and abstracts for construction machinery terms
3. **Combines Results** - Merges and deduplicates results
4. **Saves Data** - Exports to both CSV and JSON formats

## Manual Download Methods

### Method 1: USPTO Bulk Data Download

1. **Visit USPTO Bulk Data**: https://bulkdata.uspto.gov/
2. **Download Patent Grant Data**:
   - Go to: https://bulkdata.uspto.gov/data/patent/grant/redbook/bibliographic/
   - Download XML files (organized by year)
   - Filter for construction machinery CPC codes: E04G, E04B, E04C, B66C, etc.

### Method 2: USPTO PatentsView API (Used in Script)

The script uses the PatentsView API which is free and doesn't require authentication:
- API Endpoint: https://api.patentsview.org/patents/query
- Documentation: https://patentsview.org/apis/api-query-language

### Method 3: Google Patents

1. **Visit**: https://patents.google.com/
2. **Search Query Examples**:
   - `CPC/E04G` (Scaffolding)
   - `CPC/B66C` (Cranes)
   - `"construction machinery"`
   - `"construction equipment"`
3. **Export**: Use browser extensions or manual copy

### Method 4: EPO Espacenet

1. **Visit**: https://worldwide.espacenet.com/
2. **Advanced Search**:
   - Use CPC classification codes
   - Search in title/abstract for construction terms
3. **Export**: Download individual patents or use bulk export

## CPC Codes for Construction Machinery

- **E04G** - Scaffolding; Forms; Shuttering
- **E04B** - General Building Constructions  
- **E04C** - Building Elements
- **E04D** - Roof Coverings
- **E04F** - Finishing Work on Buildings
- **E04H** - Buildings or Like Structures
- **B66C** - Cranes; Load-Engaging Elements
- **B66F** - Hoisting, Lifting, Hauling or Pushing
- **E02D** - Foundations; Excavations
- **E02F** - Earth Drilling; Mining
- **B25J** - Manipulators (Construction Robotics)

## Search Keywords

- construction machinery
- construction equipment
- construction machine
- building machinery
- civil construction
- excavator
- bulldozer
- crane
- concrete mixer
- construction robot
- automated construction
- bricklaying machine
- construction vehicle

## Output Files

The script generates:
- **CSV file**: `construction_machinery_patents_YYYYMMDD_HHMMSS.csv`
  - Easy to open in Excel/Google Sheets
  - Contains: Patent Number, Title, Date, Abstract, CPC codes, Inventors, Assignees
  
- **JSON file**: `construction_machinery_patents_YYYYMMDD_HHMMSS.json`
  - Full patent data in structured format
  - Suitable for programmatic processing

## Requirements

```bash
pip install requests
```

## Limitations

- **PatentsView API**: Limited to 10,000 results per query
- **Rate Limiting**: May need delays between requests
- **Data Coverage**: PatentsView covers US patents primarily

## Alternative: Direct USPTO Bulk Download

For larger datasets, download directly from USPTO:

1. **Patent Grant Bibliographic Data**:
   ```
   https://bulkdata.uspto.gov/data/patent/grant/redbook/bibliographic/
   ```

2. **Filter by CPC Code** using XML parsing:
   ```python
   import xml.etree.ElementTree as ET
   
   # Parse USPTO XML files
   # Filter for CPC codes: E04G, E04B, B66C, etc.
   ```

## Example USPTO XML Structure

```xml
<us-patent-grant>
  <us-bibliographic-data-grant>
    <publication-reference>
      <document-id>
        <doc-number>12345678</doc-number>
      </document-id>
    </publication-reference>
    <classification-ipc>
      <main-classification>E04G 21/00</main-classification>
    </classification-ipc>
  </us-bibliographic-data-grant>
</us-patent-grant>
```

## Next Steps

1. Run the script to get initial dataset
2. Review the CSV/JSON output
3. Filter further based on specific needs
4. Use the data for LLM training or pattern analysis

## Need Help?

- Check PatentsView API docs: https://patentsview.org/apis/api-query-language
- USPTO Bulk Data Guide: https://www.uspto.gov/learning-and-resources/bulk-data-products
- EPO Bulk Data: https://www.epo.org/searching-for-patents/data/bulk-data-sets.html

