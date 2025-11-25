# pyright: reportMissingImports=false

"""
RAGAS evaluation script for construction robotics design generation.
"""

import os
import json
import logging
import importlib
from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING
import requests
from dotenv import load_dotenv

if TYPE_CHECKING:
    from ragas import evaluate  # noqa: F401
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall  # noqa: F401
    from datasets import Dataset  # noqa: F401
else:
    ragas_module = importlib.import_module("ragas")
    evaluate = getattr(ragas_module, "evaluate")
    ragas_metrics = importlib.import_module("ragas.metrics")
    faithfulness = getattr(ragas_metrics, "faithfulness")
    answer_relevancy = getattr(ragas_metrics, "answer_relevancy")
    context_precision = getattr(ragas_metrics, "context_precision")
    context_recall = getattr(ragas_metrics, "context_recall")
    Dataset = getattr(importlib.import_module("datasets"), "Dataset")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
API_URL = "http://localhost:8000"


# Evaluation prompts
EVAL_PROMPTS = [
    {
        "prompt": "Design a robotic bricklaying system for 3-story buildings",
        "filters": {"cpc": ["B25J", "E04G"], "year_min": 2018},
        "expected_context": ["robotic", "bricklaying", "construction", "automation"]
    },
    {
        "prompt": "Create an automated concrete mixing system with temperature control",
        "filters": {"cpc": ["E04G", "B25J"], "year_min": 2019},
        "expected_context": ["concrete", "mixing", "temperature", "control"]
    },
    {
        "prompt": "Design a robotic welding system for steel construction",
        "filters": {"cpc": ["B25J"], "year_min": 2020},
        "expected_context": ["welding", "robotic", "steel", "construction"]
    },
    {
        "prompt": "Create an automated scaffolding assembly system with safety features",
        "filters": {"cpc": ["E04G"], "year_min": 2018},
        "expected_context": ["scaffolding", "assembly", "safety", "automation"]
    },
    {
        "prompt": "Design a robotic excavation system for foundation work",
        "filters": {"cpc": ["E02D", "B25J"], "year_min": 2019},
        "expected_context": ["excavation", "robotic", "foundation", "earth"]
    }
]


def generate_design(prompt: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate design brief from API."""
    url = f"{API_URL}/design"
    payload = {
        "prompt": prompt,
        "filters": filters
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error calling API: {e}")
        raise


def get_context_from_design(design: Dict[str, Any]) -> str:
    """Extract context from design brief citations."""
    citations = design.get("citations", [])
    context_parts = []
    
    for citation in citations:
        context_parts.append(
            f"Patent {citation.get('patent_number', '')}: {citation.get('title', '')}"
        )
        context_parts.append(f"Reason: {citation.get('reason', '')}")
    
    return "\n".join(context_parts)


def format_answer(design: Dict[str, Any]) -> str:
    """Format design brief as answer."""
    parts = [design.get("overview", "")]
    
    # Add modules
    if design.get("modules"):
        parts.append("\nModules:")
        for module in design["modules"]:
            parts.append(f"- {module.get('name', '')}: {module.get('function', '')}")
    
    # Add actuation
    if design.get("actuation"):
        parts.append("\nActuation:")
        for actuation in design["actuation"]:
            parts.append(f"- {actuation.get('subsystem', '')}: {actuation.get('choice', '')}")
    
    # Add sensing
    if design.get("sensing"):
        parts.append("\nSensing:")
        for sensing in design["sensing"]:
            parts.append(f"- {sensing.get('subsystem', '')}: {', '.join(sensing.get('sensors', []))}")
    
    # Add control
    if design.get("control"):
        parts.append("\nControl:")
        for control in design["control"]:
            parts.append(f"- {control.get('layer', '')}: {control.get('approach', '')}")
    
    return "\n".join(parts)


def run_evaluation():
    """Run RAGAS evaluation."""
    logger.info("Starting RAGAS evaluation...")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"API is not running: {e}")
        logger.error("Please start the FastAPI server: python app.py")
        return
    
    # Generate designs and collect data
    questions = []
    answers = []
    contexts = []
    ground_truths = []
    
    logger.info(f"Evaluating {len(EVAL_PROMPTS)} prompts...")
    
    for i, eval_prompt in enumerate(EVAL_PROMPTS, 1):
        logger.info(f"Evaluating prompt {i}/{len(EVAL_PROMPTS)}: {eval_prompt['prompt']}")
        
        try:
            # Generate design
            design = generate_design(
                prompt=eval_prompt["prompt"],
                filters=eval_prompt["filters"]
            )
            
            # Extract data
            questions.append(eval_prompt["prompt"])
            answers.append(format_answer(design))
            contexts.append([get_context_from_design(design)])
            ground_truths.append("Design based on construction robotics patents")
            
        except Exception as e:
            logger.error(f"Error evaluating prompt {i}: {e}")
            continue
    
    if not questions:
        logger.error("No evaluations completed. Exiting.")
        return
    
    # Create dataset
    logger.info("Creating evaluation dataset...")
    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })
    
    # Run evaluation
    logger.info("Running RAGAS evaluation...")
    try:
        result = evaluate(
            dataset=dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            ]
        )
        
        # Print results
        print("\n" + "=" * 80)
        print("RAGAS EVALUATION RESULTS")
        print("=" * 80)
        print(f"\nFaithfulness: {result['faithfulness']:.4f}")
        print(f"Answer Relevancy: {result['answer_relevancy']:.4f}")
        print(f"Context Precision: {result['context_precision']:.4f}")
        print(f"Context Recall: {result['context_recall']:.4f}")
        print("\n" + "=" * 80)
        
        # Save results
        results_file = Path("eval_results.json")
        with open(results_file, "w") as f:
            json.dump({
                "faithfulness": float(result['faithfulness']),
                "answer_relevancy": float(result['answer_relevancy']),
                "context_precision": float(result['context_precision']),
                "context_recall": float(result['context_recall'])
            }, f, indent=2)
        
        logger.info(f"Results saved to: {results_file}")
        
    except Exception as e:
        logger.error(f"Error running evaluation: {e}")
        logger.error("Make sure RAGAS dependencies are installed: pip install ragas")
        raise


def main():
    """Main entry point."""
    run_evaluation()


if __name__ == "__main__":
    main()

