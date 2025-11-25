# pyright: reportMissingImports=false

"""
FastAPI server for construction robotics patent-grounded design generation.
"""

import os
import json
import logging
import importlib
from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING, cast
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import numpy as np

OpenAI = None  # type: ignore[assignment]
SentenceTransformer = None  # type: ignore[assignment]
CrossEncoderClass = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import chromadb  # noqa: F401
    from chromadb.config import Settings  # noqa: F401
    from sentence_transformers import SentenceTransformer, CrossEncoder  # noqa: F401
    from rank_bm25 import BM25Okapi  # noqa: F401
    from openai import OpenAI as OpenAIType  # noqa: F401
else:
    fastapi_module = importlib.import_module("fastapi")
    FastAPI = getattr(fastapi_module, "FastAPI")
    HTTPException = getattr(fastapi_module, "HTTPException")
    cors_module = importlib.import_module("fastapi.middleware.cors")
    CORSMiddleware = getattr(cors_module, "CORSMiddleware")
    chromadb = importlib.import_module("chromadb")
    Settings = getattr(importlib.import_module("chromadb.config"), "Settings")
    sentence_transformers_module = importlib.import_module("sentence_transformers")
    SentenceTransformer = getattr(sentence_transformers_module, "SentenceTransformer")
    CrossEncoderClass = getattr(sentence_transformers_module, "CrossEncoder", None)
    OpenAI = getattr(importlib.import_module("openai"), "OpenAI")
    BM25Okapi = getattr(importlib.import_module("rank_bm25"), "BM25Okapi")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
DATA_DIR = Path("data")
INDEX_DIR = DATA_DIR / "index"
PROMPTS_DIR = Path("prompts")

# Initialize FastAPI app
app = FastAPI(
    title="Construction Robotics Design Generator",
    description="RAG-based design generation system grounded in patent documents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class DesignRequest(BaseModel):
    prompt: str = Field(..., description="Design specification prompt")
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filters for patent retrieval (cpc, year_min, year_max)"
    )


class Citation(BaseModel):
    patent_number: str
    title: str
    url: str
    reason: str
    figure_image: Optional[str] = None


class DesignBrief(BaseModel):
    preview_image: Optional[str] = None
    overview: str
    modules: List[Dict[str, Any]]
    actuation: List[Dict[str, Any]]
    sensing: List[Dict[str, Any]]
    control: List[Dict[str, Any]]
    materials: List[Dict[str, Any]]
    safety: List[Dict[str, Any]]
    procedure: List[str]
    bom: List[Dict[str, Any]]
    citations: List[Citation]
    figures: Optional[List[str]] = None


class DesignGenerator:
    """Handles RAG-based design generation."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = None
        self.use_openai = self.openai_api_key is not None
        
        # Initialize embedding model
        if self.use_openai:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            logger.info("Using OpenAI embeddings: text-embedding-3-large")
        else:
            logger.info("Using local embeddings: sentence-transformers/all-MiniLM-L6-v2")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(INDEX_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        try:
            self.collection = self.chroma_client.get_collection("construction_robotics_patents")
        except Exception as e:
            logger.error(f"Collection not found: {e}")
            logger.error("Please run ingest.py first to create the index")
            raise
        
        # Initialize BM25 (will be built from corpus)
        self.bm25 = None
        self.corpus_texts = []
        self.corpus_ids = []
        self._build_bm25_index()
        
        # Initialize reranker
        if CrossEncoderClass is not None:
            try:
                self.reranker = CrossEncoderClass('BAAI/bge-reranker-large')
                logger.info("Using BAAI/bge-reranker-large for reranking")
            except Exception as e:
                logger.warning(f"Could not load reranker: {e}. Using no reranking.")
                logger.warning("Install with: pip install sentence-transformers")
                self.reranker = None
        else:
            logger.warning("CrossEncoder not available. Install sentence-transformers for reranking.")
            self.reranker = None
        
        # Load prompts
        self.system_prompt = self._load_prompt("system.md")
        self.designer_prompt = self._load_prompt("designer.md")
    
    def _build_bm25_index(self):
        """Build BM25 index from ChromaDB corpus."""
        logger.info("Building BM25 index...")
        try:
            results = self.collection.get()
            
            if not results["documents"]:
                logger.warning("No documents in collection. BM25 index will be empty.")
                self.corpus_texts = []
                self.corpus_ids = []
                self.bm25 = None
                return
            
            self.corpus_texts = results["documents"]
            self.corpus_ids = results["ids"]
            
            # Tokenize for BM25
            tokenized_corpus = [doc.split() for doc in self.corpus_texts]
            self.bm25 = BM25Okapi(tokenized_corpus)
            logger.info(f"Built BM25 index with {len(self.corpus_texts)} documents")
        except Exception as e:
            logger.error(f"Error building BM25 index: {e}")
            self.corpus_texts = []
            self.corpus_ids = []
            self.bm25 = None
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt from file."""
        prompt_path = PROMPTS_DIR / filename
        if prompt_path.exists():
            with open(prompt_path, "r") as f:
                return f.read()
        else:
            logger.warning(f"Prompt file not found: {prompt_path}. Using default.")
            return ""
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts."""
        if self.use_openai and self.openai_client:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=texts
            )
            return [item.embedding for item in response.data]
        else:
            return self.embedding_model.encode(texts, show_progress_bar=False).tolist()
    
    def multi_query_expansion(self, query: str, num_queries: int = 3) -> List[str]:
        """Generate multiple query variations."""
        if not self.use_openai or not self.openai_client:
            # Simple expansion: return original query
            return [query]
        
        try:
            expansion_prompt = f"""Generate {num_queries} different search queries for the following design specification.
Each query should focus on different aspects of the design.

Original query: {query}

Generate {num_queries} diverse queries:"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a search query generator. Generate diverse search queries."},
                    {"role": "user", "content": expansion_prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            expanded_queries = response.choices[0].message.content.strip().split("\n")
            expanded_queries = [q.strip("- ").strip() for q in expanded_queries if q.strip()]
            return [query] + expanded_queries[:num_queries]
        except Exception as e:
            logger.warning(f"Query expansion failed: {e}. Using original query.")
            return [query]
    
    def hybrid_retrieve(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 50
    ) -> List[Dict[str, Any]]:
        """Hybrid retrieval: BM25 + Vector search."""
        # Multi-query expansion
        queries = self.multi_query_expansion(query, num_queries=3)
        
        # BM25 retrieval
        bm25_scores = {}
        if self.bm25 and self.corpus_ids:
            for q in queries:
                tokenized_query = q.split()
                try:
                    scores = self.bm25.get_scores(tokenized_query)
                    for idx, score in enumerate(scores):
                        if idx < len(self.corpus_ids):
                            doc_id = self.corpus_ids[idx]
                            if doc_id not in bm25_scores:
                                bm25_scores[doc_id] = 0
                            bm25_scores[doc_id] += score
                except Exception as e:
                    logger.warning(f"BM25 retrieval failed: {e}")
                    break
        
        # Vector retrieval
        try:
            query_embeddings = self.get_embeddings(queries)
            avg_embedding = np.mean(query_embeddings, axis=0).tolist()
            
            # Build where clause for filters
            where_clause = {}
            if filters:
                if "cpc" in filters:
                    where_clause["cpc"] = {"$in": filters["cpc"]}
                if "year_min" in filters:
                    where_clause["year"] = {"$gte": str(filters["year_min"])}
                if "year_max" in filters:
                    if "year" in where_clause:
                        where_clause["year"]["$lte"] = str(filters["year_max"])
                    else:
                        where_clause["year"] = {"$lte": str(filters["year_max"])}
            
            # Vector search
            vector_results = self.collection.query(
                query_embeddings=[avg_embedding],
                n_results=top_k * 2,  # Get more for filtering
                where=where_clause if where_clause else None
            )
        except Exception as e:
            logger.error(f"Vector retrieval failed: {e}")
            vector_results = {"ids": [[]], "distances": [[]], "documents": [[]], "metadatas": [[]]}
        
        # Combine scores
        combined_scores = {}
        if vector_results["ids"] and len(vector_results["ids"][0]) > 0:
            vector_ids = vector_results["ids"][0]
            vector_distances = vector_results["distances"][0]
            
            # Normalize BM25 scores
            if bm25_scores:
                max_bm25 = max(bm25_scores.values())
                min_bm25 = min(bm25_scores.values())
                bm25_range = max_bm25 - min_bm25 if max_bm25 != min_bm25 else 1
                bm25_scores = {
                    k: (v - min_bm25) / bm25_range 
                    for k, v in bm25_scores.items()
                }
            
            # Normalize vector distances (convert to similarity)
            if vector_distances:
                max_dist = max(vector_distances)
                min_dist = min(vector_distances)
                dist_range = max_dist - min_dist if max_dist != min_dist else 1
                vector_similarities = {
                    vid: 1 - (d - min_dist) / dist_range 
                    for vid, d in zip(vector_ids, vector_distances)
                }
            else:
                vector_similarities = {}
            
            # Combine scores (weighted average)
            all_ids = set(list(bm25_scores.keys()) + list(vector_similarities.keys()))
            for doc_id in all_ids:
                bm25_score = bm25_scores.get(doc_id, 0)
                vector_score = vector_similarities.get(doc_id, 0)
                # Weight: 40% BM25, 60% Vector (if BM25 exists, else 100% vector)
                if bm25_scores:
                    combined_scores[doc_id] = 0.4 * bm25_score + 0.6 * vector_score
                else:
                    combined_scores[doc_id] = vector_score
        else:
            # Fallback: use BM25 only if available
            if bm25_scores:
                max_bm25 = max(bm25_scores.values())
                min_bm25 = min(bm25_scores.values())
                bm25_range = max_bm25 - min_bm25 if max_bm25 != min_bm25 else 1
                combined_scores = {
                    k: (v - min_bm25) / bm25_range 
                    for k, v in bm25_scores.items()
                }
            else:
                logger.error("No retrieval results available")
                return []
        
        # Get top K
        sorted_ids = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Retrieve documents
        retrieved_docs = []
        retrieved_ids = [doc_id for doc_id, _ in sorted_ids]
        
        # Get documents from ChromaDB
        results = self.collection.get(ids=retrieved_ids)
        
        for doc_id, score in sorted_ids:
            idx = retrieved_ids.index(doc_id)
            retrieved_docs.append({
                "chunk_id": doc_id,
                "text": results["documents"][idx],
                "metadata": results["metadatas"][idx],
                "score": score
            })
        
        # Dedupe by patent_number
        seen_patents = set()
        deduped_docs = []
        for doc in retrieved_docs:
            patent_num = doc["metadata"]["patent_number"]
            if patent_num not in seen_patents:
                seen_patents.add(patent_num)
                deduped_docs.append(doc)
        
        return deduped_docs[:top_k]
    
    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """Rerank documents using cross-encoder."""
        if not self.reranker or len(documents) == 0:
            return documents[:top_k]
        
        try:
            # Prepare pairs for reranking
            pairs = [[query, doc["text"]] for doc in documents]
            
            # Rerank
            scores = self.reranker.predict(pairs)
            
            # Sort by score
            scored_docs = [(doc, score) for doc, score in zip(documents, scores)]
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            return [doc for doc, _ in scored_docs[:top_k]]
        except Exception as e:
            logger.warning(f"Reranking failed: {e}. Returning original documents.")
            return documents[:top_k]
    
    def generate_design(
        self,
        prompt: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate design brief using LLM."""
        # Build context from retrieved documents
        context_parts = []
        citations_map: Dict[str, Dict[str, Any]] = {}
        figure_paths: List[str] = []
        
        for doc in retrieved_docs:
            patent_num = doc["metadata"]["patent_number"]
            section = doc["metadata"]["section"]
            claim_no = doc["metadata"].get("claim_no", "")
            
            citation_key = f"US{patent_num}"
            if claim_no:
                citation_key += f", {section}, claim_{claim_no}"
            else:
                citation_key += f", {section}"
            
            context_parts.append(f"[{citation_key}]\n{doc['text']}")
            if patent_num not in citations_map:
                citations_map[patent_num] = {
                    "patent_number": f"US{patent_num}",
                    "title": doc["metadata"].get("title", f"Patent {patent_num}"),
                    "url": f"https://patentsview.org/patents/{patent_num}",
                    "reason": f"Relevant to {prompt[:50]}...",
                    "figure_image": None
                }
            figure_path = doc["metadata"].get("figure_path")
            if figure_path:
                citations_map[patent_num]["figure_image"] = figure_path
                if figure_path not in figure_paths:
                    figure_paths.append(figure_path)
        
        context = "\n\n".join(context_parts)
        
        # Build full prompt
        full_prompt = self.designer_prompt.format(
            user_prompt=prompt,
            context=context
        )
        
        # Generate design
        if self.use_openai and self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                design_text = response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                design_text = self._generate_mock_design(prompt, retrieved_docs)
        else:
            # Fallback: mock design
            design_text = self._generate_mock_design(prompt, retrieved_docs)
        
        # Parse JSON from response
        try:
            # Extract JSON from markdown code block if present
            if "```json" in design_text:
                design_text = design_text.split("```json")[1].split("```")[0].strip()
            elif "```" in design_text:
                design_text = design_text.split("```")[1].split("```")[0].strip()
            
            design_json = json.loads(design_text)
        except Exception as e:
            logger.error(f"Failed to parse design JSON: {e}")
            design_json = self._generate_mock_design_json(prompt, retrieved_docs)
        
        # Add citations
        citations = list(citations_map.values())
        design_json["citations"] = citations
        design_json["preview_image"] = figure_paths[0] if figure_paths else None
        design_json["figures"] = figure_paths if figure_paths else None
        
        return design_json
    
    def _generate_mock_design(self, prompt: str, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Generate mock design for fallback."""
        return json.dumps(self._generate_mock_design_json(prompt, retrieved_docs), indent=2)
    
    def _generate_mock_design_json(self, prompt: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate mock design JSON."""
        patent_nums = [doc["metadata"]["patent_number"] for doc in retrieved_docs[:3]]
        citations = [f"US{num}, abstract" for num in patent_nums]
        
        return {
            "preview_image": None,
            "figures": None,
            "overview": f"Design system for {prompt}. Based on {len(retrieved_docs)} patent documents.",
            "modules": [
                {
                    "name": "Robotic Arm Module",
                    "function": "Handles material placement and manipulation",
                    "citations": citations[:1] if citations else ["SPECULATIVE"]
                }
            ],
            "actuation": [
                {
                    "subsystem": "Arm Actuation",
                    "choice": "Electric servo motors",
                    "why": "Precise control and high torque",
                    "citations": citations[:1] if citations else ["SPECULATIVE"]
                }
            ],
            "sensing": [
                {
                    "subsystem": "Position Sensing",
                    "sensors": ["Encoders", "Camera"],
                    "why": "Accurate positioning and visual feedback",
                    "citations": citations[:1] if citations else ["SPECULATIVE"]
                }
            ],
            "control": [
                {
                    "layer": "Motion Control",
                    "approach": "PID control",
                    "teleop_or_auto": "Autonomous",
                    "citations": citations[:1] if citations else ["SPECULATIVE"]
                }
            ],
            "materials": [
                {
                    "part": "Frame",
                    "material": "Aluminum",
                    "why": "Lightweight and strong",
                    "citations": citations[:1] if citations else ["SPECULATIVE"]
                }
            ],
            "safety": [
                {
                    "risk": "Collision",
                    "mitigation": "Emergency stop and safety barriers",
                    "citations": citations[:1] if citations else ["SPECULATIVE"]
                }
            ],
            "procedure": [
                "Initialize system",
                "Calibrate sensors",
                "Begin construction sequence"
            ],
            "bom": [
                {
                    "item": "Robotic Arm",
                    "qty": 1,
                    "est_cost_usd": 50000.0,
                    "citations": citations[:1] if citations else ["SPECULATIVE"]
                }
            ]
        }
    
    def generate(self, prompt: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Full pipeline: retrieve -> rerank -> generate."""
        # Retrieve
        retrieved_docs = self.hybrid_retrieve(prompt, filters=filters, top_k=50)
        
        # Rerank
        reranked_docs = self.rerank(prompt, retrieved_docs, top_k=10)
        
        # Generate
        design = self.generate_design(prompt, reranked_docs)
        
        return design


# Initialize generator (lazy initialization)
generator = None

def get_generator():
    """Get or create generator instance."""
    global generator
    if generator is None:
        generator = DesignGenerator()
    return generator


@app.get("/")
async def root():
    """Default route with basic instructions."""
    return {
        "message": "Construction Robotics Design Generator API",
        "endpoints": {
            "health": "/health",
            "design": "POST /design",
            "docs": "/docs"
        },
        "usage": "Send POST /design with JSON {\"prompt\": \"...\", \"filters\": {...}}"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/design", response_model=DesignBrief)
async def generate_design(request: DesignRequest):
    """Generate design brief from patent-grounded RAG system."""
    try:
        gen = get_generator()
        design = gen.generate(
            prompt=request.prompt,
            filters=request.filters
        )
        return design
    except Exception as e:
        logger.error(f"Error generating design: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

