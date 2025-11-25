# pyright: reportMissingImports=false

"""
Patent ingestion script: Downloads patents from USPTO PatentsView API,
chunks documents, enriches metadata, and builds vector index.
"""

import os
import json
import logging
import importlib
from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import requests
from tqdm import tqdm
from dotenv import load_dotenv
import pypdfium2 as pdfium
from bs4 import BeautifulSoup

OpenAI = None  # type: ignore[assignment]
SentenceTransformer = None  # type: ignore[assignment]

if TYPE_CHECKING:
    import chromadb  # noqa: F401
    from chromadb.config import Settings  # noqa: F401
    from sentence_transformers import SentenceTransformer as STModel  # noqa: F401
    from openai import OpenAI as OpenAIType  # noqa: F401
else:
    chromadb = importlib.import_module("chromadb")
    Settings = getattr(importlib.import_module("chromadb.config"), "Settings")
    sentence_transformers_module = importlib.import_module("sentence_transformers")
    SentenceTransformer = getattr(sentence_transformers_module, "SentenceTransformer")
    OpenAI = getattr(importlib.import_module("openai"), "OpenAI")

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
RAW_DIR = DATA_DIR / "raw"
CHUNKS_DIR = DATA_DIR / "chunks"
INDEX_DIR = DATA_DIR / "index"
MEDIA_DIR = DATA_DIR / "media"

# CPC codes for construction robotics
CPC_CODES = ["B25J", "E04G", "E04B", "E04C", "B66C", "E02D", "E02F"]

# Create directories
RAW_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


class PatentIngester:
    """Handles patent downloading, chunking, and indexing."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_model = None
        self.openai_client = None
        self.use_openai = self.openai_api_key is not None
        self.http = requests.Session()
        self.http.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        })
        
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
        self.collection_name = "construction_robotics_patents"
        try:
            self.chroma_client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"description": "Construction robotics patent documents"}
        )
    
    @staticmethod
    def _sanitize_patent_number(patent_number: str) -> str:
        """Return patent number string suitable for constructing file paths and URLs."""
        safe = patent_number.replace("/", "").replace(" ", "")
        if not safe.upper().startswith("US"):
            safe = f"US{safe}"
        return safe.upper()

    def download_patent_figures(self, patent_number: str) -> List[str]:
        """Download patent PDF and render first page image; return list of image paths."""
        sanitized = self._sanitize_patent_number(patent_number)
        patent_dir = MEDIA_DIR / sanitized
        patent_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = patent_dir / "document.pdf"
        image_path = patent_dir / "page_1.png"

        if image_path.exists():
            try:
                rel_path = str(image_path.relative_to(Path.cwd()))
            except ValueError:
                rel_path = str(image_path)
            return [rel_path]

        figure_paths: List[str] = []

        pdf_url = None
        thumb_url = None

        page_url = f"https://patents.google.com/patent/{sanitized}/en"
        try:
            page_resp = self.http.get(page_url, timeout=30)
            page_resp.raise_for_status()
            soup = BeautifulSoup(page_resp.text, "html.parser")
            meta_pdf = soup.find("meta", attrs={"name": "citation_pdf_url"})
            if meta_pdf and meta_pdf.get("content"):
                pdf_url = meta_pdf["content"].strip()
            meta_thumb = soup.find("meta", attrs={"property": "og:image"})
            if meta_thumb and meta_thumb.get("content"):
                thumb_url = meta_thumb["content"].strip()
        except Exception as exc:
            logger.warning("Could not resolve asset URLs for %s: %s", patent_number, exc)

        if pdf_url:
            try:
                response = self.http.get(pdf_url, timeout=45)
                response.raise_for_status()
                pdf_path.write_bytes(response.content)

                pdf_doc = pdfium.PdfDocument(str(pdf_path))
                page = pdf_doc[0]
                bitmap = page.render(scale=2)
                pil_image = bitmap.to_pil()
                bitmap.close()
                pil_image.save(image_path)
                pdf_doc.close()
                try:
                    rel_path = str(image_path.relative_to(Path.cwd()))
                except ValueError:
                    rel_path = str(image_path)
                figure_paths.append(rel_path)
            except Exception as exc:
                logger.warning("Failed to download/render PDF for %s: %s", patent_number, exc)
            finally:
                if pdf_path.exists():
                    try:
                        pdf_path.unlink(missing_ok=True)  # type: ignore[attr-defined]
                    except TypeError:
                        if pdf_path.exists():
                            pdf_path.unlink()

        if thumb_url:
            try:
                thumb_resp = self.http.get(thumb_url, timeout=30)
                thumb_resp.raise_for_status()
                extension = ".png"
                content_type = thumb_resp.headers.get("Content-Type", "")
                if "jpeg" in content_type:
                    extension = ".jpg"
                thumb_path = patent_dir / f"thumbnail{extension}"
                thumb_path.write_bytes(thumb_resp.content)
                try:
                    rel_path = str(thumb_path.relative_to(Path.cwd()))
                except ValueError:
                    rel_path = str(thumb_path)
                if rel_path not in figure_paths:
                    figure_paths.append(rel_path)
            except Exception as exc:
                logger.warning("Failed to download thumbnail for %s: %s", patent_number, exc)

        return figure_paths
    def download_patents(self, limit: int = 200, year_min: int = 2018) -> List[Dict[str, Any]]:
        """Download patents from USPTO PatentsView API."""
        logger.info(f"Downloading up to {limit} patents from USPTO PatentsView API...")
        
        patents = []
        page_size = 100
        page = 1
        
        # Build query for construction robotics patents
        cpc_query = " OR ".join([f'"{code}"' for code in CPC_CODES])
        query = {
            "q": {
                "_and": [
                    {
                        "_or": [
                            {"cpc_subgroup_id": {"_contains": code}} 
                            for code in CPC_CODES
                        ]
                    },
                    {"patent_date": {"_gte": f"{year_min}-01-01"}}
                ]
            },
            "f": [
                "patent_number",
                "patent_title",
                "patent_abstract",
                "patent_date",
                "assignee_organization",
                "cpc_subgroup_id",
                "patent_number",
                "patent_url"
            ],
            "o": {
                "per_page": page_size,
                "page": page
            }
        }
        
        try:
            while len(patents) < limit:
                query["o"]["page"] = page
                response = self.http.post(
                    "https://api.patentsview.org/patents/query",
                    json=query,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                if "patents" not in data or not data["patents"]:
                    logger.info("No more patents found")
                    break
                
                for patent in data["patents"]:
                    if len(patents) >= limit:
                        break
                    
                    # Extract patent data
                    patent_number = patent.get("patent_number", "")
                    title = patent.get("patent_title", "")
                    abstract = patent.get("patent_abstract", "")
                    patent_date = patent.get("patent_date", "")
                    assignee = patent.get("assignee_organization", [""])[0] if patent.get("assignee_organization") else ""
                    cpc_codes = patent.get("cpc_subgroup_id", [])
                    url = patent.get("patent_url", f"https://patentsview.org/patents/{patent_number}")
                    
                    # Extract year
                    year = int(patent_date.split("-")[0]) if patent_date else None
                    
                    # Normalize CPC codes (get main group)
                    cpc_main = list(set([code.split("/")[0] for code in cpc_codes if "/" in code]))
                    
                    patent_data = {
                        "patent_number": patent_number,
                        "title": title,
                        "abstract": abstract,
                        "claims_text": "",  # Claims not available in basic API
                        "description": "",  # Description not available in basic API
                        "cpc": cpc_main,
                        "assignee": assignee,
                        "pub_year": year,
                        "url": url
                    }
                    
                    patents.append(patent_data)
                
                logger.info(f"Downloaded {len(patents)} patents so far...")
                page += 1
                
                if len(data["patents"]) < page_size:
                    break
        
        except Exception as e:
            logger.error(f"Error downloading patents: {e}")
            # Fallback: use mock data if API fails
            logger.info("Using mock patent data for development")
            patents = self._generate_mock_patents(limit)
        
        logger.info(f"Downloaded {len(patents)} patents")
        return patents
    
    def _generate_mock_patents(self, limit: int) -> List[Dict[str, Any]]:
        """Generate mock patent data for development/testing."""
        mock_patents = []
        for i in range(limit):
            patent_number = f"US{10000000 + i}"
            mock_patents.append({
                "patent_number": patent_number,
                "title": f"Robotic Construction System {i+1}",
                "abstract": f"This invention relates to a robotic construction system for automated building assembly. The system includes robotic arms, sensors, and control systems for precise placement of construction materials. The invention addresses challenges in automation of construction processes including safety, accuracy, and efficiency.",
                "claims_text": "",
                "description": "",
                "cpc": ["B25J", "E04G"],
                "assignee": f"Construction Robotics Inc.",
                "pub_year": 2018 + (i % 5),
                "url": f"https://patentsview.org/patents/{patent_number}"
            })
        return mock_patents
    
    def chunk_patent(self, patent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk patent document into smaller segments."""
        chunks = []
        patent_number = patent["patent_number"]
        
        # Chunk 1: Abstract (one chunk)
        if patent.get("abstract"):
            chunks.append({
                "chunk_id": f"{patent_number}_abstract_0",
                "patent_number": patent_number,
                "section": "abstract",
                "claim_no": None,
                "text": patent["abstract"],
                "metadata": {
                    "cpc": patent.get("cpc", []),
                    "year": patent.get("pub_year"),
                    "mechanism_tags": self._extract_mechanism_tags(patent["abstract"])
                }
            })
        
        # Chunk 2: Description (800-1200 tokens with 120 overlap)
        if patent.get("description"):
            description = patent["description"]
            # Simple chunking: split by sentences, aim for ~1000 tokens per chunk
            sentences = description.split(". ")
            current_chunk = []
            current_length = 0
            chunk_idx = 0
            
            for sentence in sentences:
                sentence_length = len(sentence.split())
                if current_length + sentence_length > 1000 and current_chunk:
                    # Save current chunk
                    chunk_text = ". ".join(current_chunk) + "."
                    chunks.append({
                        "chunk_id": f"{patent_number}_description_{chunk_idx}",
                        "patent_number": patent_number,
                        "section": "description",
                        "claim_no": None,
                        "text": chunk_text,
                        "metadata": {
                            "cpc": patent.get("cpc", []),
                            "year": patent.get("pub_year"),
                            "mechanism_tags": self._extract_mechanism_tags(chunk_text)
                        }
                    })
                    # Start new chunk with overlap (last 120 tokens)
                    overlap_sentences = current_chunk[-10:] if len(current_chunk) >= 10 else current_chunk
                    current_chunk = overlap_sentences + [sentence]
                    current_length = sum(len(s.split()) for s in current_chunk)
                    chunk_idx += 1
                else:
                    current_chunk.append(sentence)
                    current_length += sentence_length
            
            # Add remaining chunk
            if current_chunk:
                chunk_text = ". ".join(current_chunk) + "."
                chunks.append({
                    "chunk_id": f"{patent_number}_description_{chunk_idx}",
                    "patent_number": patent_number,
                    "section": "description",
                    "claim_no": None,
                    "text": chunk_text,
                    "metadata": {
                        "cpc": patent.get("cpc", []),
                        "year": patent.get("pub_year"),
                        "mechanism_tags": self._extract_mechanism_tags(chunk_text)
                    }
                })
        
        # Chunk 3: Claims (one chunk per claim)
        if patent.get("claims_text"):
            claims = patent["claims_text"].split("\n")
            for claim_idx, claim in enumerate(claims):
                if claim.strip():
                    chunks.append({
                        "chunk_id": f"{patent_number}_claim_{claim_idx + 1}",
                        "patent_number": patent_number,
                        "section": "claims",
                        "claim_no": claim_idx + 1,
                        "text": claim.strip(),
                        "metadata": {
                            "cpc": patent.get("cpc", []),
                            "year": patent.get("pub_year"),
                            "mechanism_tags": self._extract_mechanism_tags(claim)
                        }
                    })
        
        return chunks
    
    def _extract_mechanism_tags(self, text: str) -> List[str]:
        """Extract mechanism tags from text (simple keyword matching)."""
        mechanisms = {
            "actuator": ["actuator", "motor", "servo", "pneumatic", "hydraulic"],
            "sensor": ["sensor", "camera", "lidar", "encoder", "proximity"],
            "control": ["control", "controller", "PLC", "algorithm", "feedback"],
            "gripper": ["gripper", "end-effector", "grasp", "clamp"],
            "navigation": ["navigation", "localization", "mapping", "SLAM"],
            "safety": ["safety", "emergency", "stop", "guard", "interlock"]
        }
        
        text_lower = text.lower()
        tags = []
        for tag, keywords in mechanisms.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)
        return tags
    
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
    
    def index_patents(self, patents: List[Dict[str, Any]]):
        """Index patents in ChromaDB."""
        logger.info("Chunking and indexing patents...")
        
        all_chunks = []
        all_embeddings = []
        all_ids = []
        all_metadatas = []
        
        for patent in tqdm(patents, desc="Processing patents"):
            figures = self.download_patent_figures(patent["patent_number"])
            patent["figures"] = figures
            
            # Save raw patent
            raw_file = RAW_DIR / f"{patent['patent_number']}.jsonl"
            with open(raw_file, "w") as f:
                json.dump(patent, f)
            
            # Chunk patent
            chunks = self.chunk_patent(patent)
            for chunk in chunks:
                chunk["metadata"]["figure_path"] = figures[0] if figures else ""
                chunk["metadata"]["figures"] = figures
                chunk["metadata"]["title"] = patent.get("title", "")
            
            # Save chunks
            chunks_file = CHUNKS_DIR / f"{patent['patent_number']}_chunks.jsonl"
            with open(chunks_file, "w") as f:
                for chunk in chunks:
                    f.write(json.dumps(chunk) + "\n")
            
            # Prepare for indexing
            for chunk in chunks:
                all_chunks.append(chunk["text"])
                all_ids.append(chunk["chunk_id"])
                all_metadatas.append({
                    "patent_number": chunk["patent_number"],
                    "section": chunk["section"],
                    "claim_no": str(chunk["claim_no"]) if chunk["claim_no"] else "",
                    "cpc": ",".join(chunk["metadata"]["cpc"]),
                    "year": str(chunk["metadata"]["year"]) if chunk["metadata"]["year"] else "",
                    "mechanism_tags": ",".join(chunk["metadata"]["mechanism_tags"]),
                    "figure_path": chunk["metadata"].get("figure_path", ""),
                    "title": chunk["metadata"].get("title", "")
                })
        
        # Get embeddings in batches
        logger.info("Generating embeddings...")
        batch_size = 100
        for i in tqdm(range(0, len(all_chunks), batch_size), desc="Embedding chunks"):
            batch = all_chunks[i:i + batch_size]
            batch_embeddings = self.get_embeddings(batch)
            all_embeddings.extend(batch_embeddings)
        
        # Add to ChromaDB
        logger.info("Indexing in ChromaDB...")
        self.collection.add(
            ids=all_ids,
            embeddings=all_embeddings,
            documents=all_chunks,
            metadatas=all_metadatas
        )
        
        logger.info(f"Indexed {len(all_chunks)} chunks from {len(patents)} patents")
    
    def run(self, limit: int = 200, year_min: int = 2018):
        """Run full ingestion pipeline."""
        # Download patents
        patents = self.download_patents(limit=limit, year_min=year_min)
        
        # Index patents
        self.index_patents(patents)
        
        logger.info("Ingestion complete!")


def main():
    """Main entry point."""
    ingester = PatentIngester()
    ingester.run(limit=200, year_min=2018)


if __name__ == "__main__":
    main()

