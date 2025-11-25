# Quick Start Guide

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
# Copy .env.example to .env (if not exists)
# Add your OPENAI_API_KEY to .env
export OPENAI_API_KEY=sk-...
```

**Note:** The system works without OpenAI API key using local models, but performance will be better with OpenAI.

## Step 1: Ingest Patents

Download and index ~200 construction robotics patents:

```bash
python ingest.py
```

This will:
- Download patents from USPTO PatentsView API
- Chunk documents (abstract, description, claims)
- Build vector index in `data/index/`
- Create metadata files in `data/raw/` and `data/chunks/`

**Expected time:** 5-10 minutes (depends on API speed)

## Step 2: Start FastAPI Server

```bash
python app.py
```

Server will start on `http://localhost:8000`

- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Step 3: Generate Design (CLI)

```bash
python demo.py --prompt "Design a robotic bricklaying system for 3-story buildings" --cpc B25J E04G
```

## Step 4: Generate Design (API)

```bash
curl -X POST "http://localhost:8000/design" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Design an automated concrete mixing system with temperature control",
    "filters": {"cpc": ["B25J", "E04G"], "year_min": 2018}
  }'
```

## Step 5: Use Streamlit UI

```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501` in your browser.

## Step 6: Evaluate (Optional)

```bash
python eval_ragas.py
```

## Project Structure

```
.
├── ingest.py              # Patent ingestion
├── app.py                 # FastAPI server
├── demo.py                # CLI interface
├── eval_ragas.py          # Evaluation
├── streamlit_app.py       # Streamlit UI
├── prompts/               # Prompt templates
│   ├── system.md
│   └── designer.md
├── data/                  # Data directory (created after ingestion)
│   ├── raw/               # Raw patents
│   ├── chunks/            # Chunked patents
│   └── index/             # ChromaDB index
├── requirements.txt       # Dependencies
└── README.md             # Full documentation
```

## Troubleshooting

### Issue: Collection not found
**Solution:** Run `python ingest.py` first to create the index.

### Issue: API not running
**Solution:** Start the server: `python app.py`

### Issue: No OpenAI API key
**Solution:** System will use local models (sentence-transformers). Performance will be lower but functional.

### Issue: BM25 index empty
**Solution:** This is normal if collection is empty. Run ingestion first.

### Issue: Reranker not loading
**Solution:** Install sentence-transformers: `pip install sentence-transformers`

## Example Prompts

1. "Design a robotic bricklaying system for 3-story buildings"
2. "Create an automated concrete mixing system with temperature control"
3. "Design a robotic welding system for steel construction"
4. "Create an automated scaffolding assembly system with safety features"
5. "Design a robotic excavation system for foundation work"

## Output Format

Design briefs include:
- Overview
- Modules (with citations)
- Actuation (with citations)
- Sensing (with citations)
- Control (with citations)
- Materials (with citations)
- Safety (with citations)
- Procedure
- BOM (Bill of Materials)
- Citations (full patent references)

All design choices are grounded in patent citations or marked as SPECULATIVE.

## Next Steps

1. Customize prompts in `prompts/` directory
2. Adjust retrieval parameters in `app.py`
3. Add more evaluation metrics in `eval_ragas.py`
4. Extend UI in `streamlit_app.py`
5. Scale up patent database (modify `ingest.py`)

## Support

For issues or questions, please check the main README.md or open an issue.



