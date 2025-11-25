# 🏗️ Patent Design Pattern Project

A RAG (Retrieval-Augmented Generation) based system for generating construction robotics designs grounded in patent documents.

## ✨ Features

- **Patent-Grounded Design Generation**: Every design choice is backed by patent citations
- **Hybrid Retrieval**: Combines BM25 (keyword) and Vector (semantic) search
- **Modern Animated UI**: Beautiful Streamlit interface with smooth animations
- **Citation System**: Full traceability to patent sources
- **Structured Output**: JSON design briefs with modules, actuation, sensing, control, materials, safety, and BOM

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/patent-design-pattern.git
cd patent-design-pattern

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (optional)

# Run patent ingestion (first time only)
python ingest.py
```

### Running the Application

**Option 1: Using Docker (Recommended)**
```bash
docker-compose up --build
```

**Option 2: Local Python**
```bash
# Terminal 1 - Start API
python app.py

# Terminal 2 - Start Frontend
streamlit run streamlit_app.py
```

Access the website at: http://localhost:8501

## 📁 Project Structure

```
.
├── app.py                 # FastAPI backend server
├── streamlit_app.py       # Streamlit frontend UI
├── ingest.py              # Patent ingestion and indexing
├── demo.py                # CLI interface
├── eval_ragas.py          # Evaluation script
├── prompts/               # Prompt templates
│   ├── system.md
│   └── designer.md
├── data/                  # Data directory
│   ├── raw/              # Raw patent JSONL files
│   ├── chunks/           # Chunked patent data
│   ├── index/            # ChromaDB vector index
│   └── media/            # Patent figures and images
└── requirements.txt      # Python dependencies
```

## 🎨 Features

- **Animated UI**: Modern design with smooth CSS animations
- **Hybrid Search**: BM25 + Vector similarity for optimal retrieval
- **Multi-Query Expansion**: Generates diverse query variations
- **Cross-Encoder Reranking**: Fine-tunes retrieval results
- **Citation Enforcement**: Every design choice must cite patents
- **Structured Output**: Comprehensive JSON design briefs

## 🔧 Configuration

Key environment variables (`.env` file):

```env
OPENAI_API_KEY=your-key-here  # Optional but recommended
API_URL=http://localhost:8000
DATA_DIR=data
INDEX_DIR=data/index
```

## 📚 API Documentation

Once the API is running, visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 🌐 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy Options:

- **Streamlit Cloud**: Connect GitHub repo → Auto-deploy
- **Railway.app**: `railway up`
- **Render.com**: Use `render.yaml`
- **Docker**: `docker-compose -f docker-compose.prod.yml up`

## 📖 Documentation

- [HOW_TO_RUN.md](HOW_TO_RUN.md) - Running instructions
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [RUN_AND_SHARE.md](RUN_AND_SHARE.md) - Sharing guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Troubleshooting

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## 🙏 Acknowledgments

- USPTO PatentsView API for patent data
- OpenAI for embeddings and LLM
- Streamlit for the UI framework
- ChromaDB for vector storage

---

**Built with ❤️ for construction robotics innovation**
