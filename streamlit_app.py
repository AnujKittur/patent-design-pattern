# pyright: reportMissingImports=false

"""
Streamlit UI for construction robotics design generation.
"""

import os
import base64
import streamlit as st
import requests
import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from openai import OpenAI
def create_preview_image(text: str) -> BytesIO:
    """Generate a simple preview image with prompt text."""
    width, height = 1200, 380
    background_color = (32, 56, 88)
    accent_color = (25, 118, 210)
    text_color = (240, 244, 255)

    img = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(img)

    # Accent bar
    draw.rectangle([(0, height - 60), (width, height)], fill=accent_color)

    # Title text
    title = "Construction Robotics Design Preview"
    font_title = ImageFont.load_default()
    draw.text((40, 40), title, fill=text_color, font=font_title)

    # Prompt text
    prompt_font = ImageFont.load_default()
    wrapped = []
    line = ""
    max_width = width - 80
    for word in text.split():
        test_line = f"{line} {word}".strip()
        if draw.textlength(test_line, font=prompt_font) <= max_width:
            line = test_line
        else:
            wrapped.append(line)
            line = word
    if line:
        wrapped.append(line)

    y = 100
    for segment in wrapped[:5]:
        draw.text((40, y), segment, fill=text_color, font=prompt_font)
        y += 28

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def build_image_prompt(user_prompt: str, design: Dict[str, Any]) -> str:
    """Compose a rich text prompt for image generation."""
    lines = [
        "Create a high-resolution patent-style technical illustration for a construction robotics design.",
        "Style: clean line art with subtle shading, blueprint aesthetics, labeled components.",
        f"Primary task: {user_prompt}",
    ]
    if design.get("modules"):
        module_desc = "; ".join(
            f"{mod.get('name', '')}: {mod.get('function', '')}"
            for mod in design["modules"][:5]
        )
        lines.append(f"Key modules: {module_desc}.")
    if design.get("actuation"):
        actuation_desc = "; ".join(
            f"{act.get('subsystem', '')} uses {act.get('choice', '')}"
            for act in design["actuation"][:3]
        )
        lines.append(f"Actuation details: {actuation_desc}.")
    if design.get("sensing"):
        sensing_desc = "; ".join(
            f"{sense.get('subsystem', '')} with {', '.join(sense.get('sensors', [])).strip()}"
            for sense in design["sensing"][:3]
        )
        lines.append(f"Sensing suite: {sensing_desc}.")
    if design.get("materials"):
        material_desc = "; ".join(
            f"{mat.get('part', '')} made of {mat.get('material', '')}"
            for mat in design["materials"][:3]
        )
        lines.append(f"Materials emphasis: {material_desc}.")
    lines.append("Include callouts and annotations for major components. Background: light blueprint grid.")
    return "\n".join(lines)

def generate_design_image(user_prompt: str, design: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """Generate an illustrative image using OpenAI's image API."""
    result: Dict[str, Any] = {"image": None, "error": None}
    if not api_key:
        result["error"] = "No OpenAI API key provided."
        return result

    try:
        client = OpenAI(api_key=api_key)
        prompt_text = build_image_prompt(user_prompt, design)
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt_text,
            size="1024x1024"
        )
        image_b64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)
        result["image"] = image_bytes
    except Exception as exc:
        result["error"] = str(exc)
    return result

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Initialize session state
st.session_state.setdefault("history", [])
st.session_state.setdefault("selected_design_id", None)
st.session_state.setdefault("design_image_cache", {})
st.session_state.setdefault("openai_api_key", os.getenv("OPENAI_API_KEY", ""))
st.session_state.setdefault("auto_generate_images", False)

# Page config
st.set_page_config(
    page_title="Construction Robotics Design Generator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with animations and modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated Background Pattern */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
        animation: float 20s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes float {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(30px, -30px) rotate(5deg); }
    }
    
    /* Main Title Animation */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        font-size: 3rem !important;
        animation: slideInDown 0.8s ease-out, gradientShift 3s ease infinite;
        background-size: 200% auto;
        margin-bottom: 0.5rem !important;
    }
    
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }
    
    /* Subtitle Animation */
    .subtitle {
        color: #4a5568;
        font-size: 1.2rem;
        animation: fadeInUp 1s ease-out 0.2s both;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Card Styling with Animations */
    .design-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        animation: slideInLeft 0.6s ease-out;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .design-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15), 0 10px 10px rgba(0, 0, 0, 0.1);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Button Animations */
    button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        animation: pulse 2s ease-in-out infinite !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    button[kind="primary"]:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
        animation: none !important;
    }
    
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        50% {
            box-shadow: 0 4px 25px rgba(102, 126, 234, 0.6);
        }
    }
    
    /* Input Field Styling */
    .stTextArea > div > div > textarea {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.3s ease !important;
        font-size: 1rem !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%);
    }
    
    /* Header Styling */
    h2, h3 {
        color: #2d3748 !important;
        font-weight: 700 !important;
        animation: fadeIn 0.6s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Metrics/Stats Styling */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
        animation: slideInUp 0.6s ease-out;
        transition: transform 0.3s ease;
    }
    
    .metric-container:hover {
        transform: scale(1.05);
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Expandable Sections */
    .element-container {
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Loading Spinner Enhancement */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Code Blocks */
    pre {
        background: #1a202c !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Success Messages */
    .stSuccess {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Badge/Tag Styling */
    .stMarkdown p {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Info Boxes */
    .stInfo {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        animation: slideInLeft 0.5s ease-out;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Alert/Error Styling */
    .stAlert {
        border-radius: 12px;
        animation: shake 0.5s ease-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    /* Section Dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
        animation: expandWidth 1s ease-out;
    }
    
    @keyframes expandWidth {
        from { width: 0; }
        to { width: 100%; }
    }
    
    /* Expander/Section Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        animation: fadeIn 0.6s ease-out;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
        transform: translateX(5px);
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Container animations with stagger */
    .stContainer > div {
        animation: slideInUp 0.6s ease-out;
    }
    
    .stContainer > div:nth-child(1) { animation-delay: 0.1s; }
    .stContainer > div:nth-child(2) { animation-delay: 0.2s; }
    .stContainer > div:nth-child(3) { animation-delay: 0.3s; }
    .stContainer > div:nth-child(4) { animation-delay: 0.4s; }
    
    /* Progress Bar Enhancement */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* Image Styling */
    img {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease;
        animation: fadeIn 0.8s ease-out;
    }
    
    img:hover {
        transform: scale(1.02);
    }
    
    /* List Styling */
    ul, ol {
        animation: fadeIn 0.8s ease-out;
    }
    
    li {
        margin: 0.5rem 0;
        animation: slideInLeft 0.5s ease-out;
    }
    
    /* Table Styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        animation: fadeIn 0.6s ease-out;
    }
    
    .dataframe thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Citation Links */
    a {
        color: #667eea;
        transition: all 0.3s ease;
        text-decoration: none;
    }
    
    a:hover {
        color: #764ba2;
        text-decoration: underline;
        transform: translateX(3px);
    }
    
    /* Loading States */
    [data-testid="stSpinner"] {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
</style>

<script>
// Add entrance animations to elements
document.addEventListener('DOMContentLoaded', function() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all main content sections
    document.querySelectorAll('.main .block-container > div').forEach(el => {
        observer.observe(el);
    });
});
</script>
""", unsafe_allow_html=True)

# Title with enhanced styling
st.markdown("""
<div style="animation: slideInDown 0.8s ease-out;">
    <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
               -webkit-background-clip: text; 
               -webkit-text-fill-color: transparent; 
               background-clip: text;
               font-weight: 800;
               font-size: 3rem;
               margin-bottom: 0.5rem;">
        🏗️ Construction Robotics Design Generator
    </h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="subtitle" style="color: #4a5568; font-size: 1.2rem; margin-bottom: 2rem;">
    Generate patent-grounded design briefs for construction robotics systems
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("Configuration")

# API URL
api_url = st.sidebar.text_input("API URL", value=API_URL)

# Filters
st.sidebar.subheader("Filters")
cpc_codes = st.sidebar.multiselect(
    "CPC Codes",
    options=["B25J", "E04G", "E04B", "E04C", "B66C", "E02D", "E02F"],
    default=["B25J", "E04G"]
)
year_min = st.sidebar.number_input("Year Minimum", min_value=2000, max_value=2024, value=2018)
year_max = st.sidebar.number_input("Year Maximum", min_value=2000, max_value=2024, value=2024)

st.sidebar.markdown("---")
st.sidebar.subheader("Sample Prompts")
sample_prompts = [
    "Design a robotic bricklaying system for 3-story buildings",
    "Create an automated concrete mixing system with temperature control",
    "Design a robotic welding system for steel construction",
    "Create an automated scaffolding assembly system with safety features",
    "Design a robotic excavation system for foundation work"
]
selected_sample = st.sidebar.selectbox("Quick select", options=["(choose a sample)"] + sample_prompts)
if selected_sample != "(choose a sample)":
    prompt_prefill = selected_sample
else:
    prompt_prefill = ""

st.sidebar.markdown("---")
st.sidebar.subheader("Image Generation")
api_key_input = st.sidebar.text_input(
    "OpenAI API Key",
    value=st.session_state["openai_api_key"],
    type="password",
    help="Optional: provide an OpenAI API key to render patent-style images."
)
st.session_state["openai_api_key"] = api_key_input.strip()
auto_image = st.sidebar.checkbox(
    "Automatically generate preview images",
    value=st.session_state.get("auto_generate_images", False)
)
st.session_state["auto_generate_images"] = auto_image

# Build filters
filters = {}
if cpc_codes:
    filters["cpc"] = cpc_codes
if year_min:
    filters["year_min"] = int(year_min)
if year_max:
    filters["year_max"] = int(year_max)

# Main content
st.header("Design Specification")

# Prompt input
prompt = st.text_area(
    "Enter design specification:",
    value=prompt_prefill,
    height=100,
    placeholder="Example: Design a robotic bricklaying system for 3-story buildings"
)

# Generate button with enhanced styling
st.markdown("""
<style>
.stButton > button {
    width: 100%;
    height: 60px;
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

generate_clicked = st.button("🚀 Generate Design", type="primary", use_container_width=True)

selected_history_label = None
if st.session_state["history"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Previous Designs")
    history_labels = [
        f"{idx + 1}. {entry['prompt'][:60]}{'…' if len(entry['prompt']) > 60 else ''}"
        for idx, entry in enumerate(st.session_state['history'])
    ]
    selected_history_label = st.sidebar.selectbox(
        "View saved design",
        options=history_labels,
        index=0 if st.session_state["selected_design_id"] is None else next(
            (i for i, entry in enumerate(st.session_state['history'])
             if entry["id"] == st.session_state["selected_design_id"]),
            0
        )
    )
    selected_entry = st.session_state['history'][history_labels.index(selected_history_label)]
    st.session_state["selected_design_id"] = selected_entry["id"]
else:
    selected_entry = None

if generate_clicked:
    if not prompt:
        st.error("Please enter a design specification")
    else:
        # Check API health
        try:
            health_response = requests.get(f"{api_url}/health", timeout=5)
            health_response.raise_for_status()
        except Exception as e:
            st.error(f"API is not running: {e}")
            st.error("Please start the FastAPI server: `python app.py`")
            st.stop()
        
        # Generate design
        with st.spinner("Generating design..."):
            try:
                response = requests.post(
                    f"{api_url}/design",
                    json={
                        "prompt": prompt,
                        "filters": filters
                    },
                    timeout=60
                )
                response.raise_for_status()
                design = response.json()

                # Store in session history
                entry_id = f"{time.time_ns()}"
                history_entry = {
                    "id": entry_id,
                    "prompt": prompt,
                    "filters": filters,
                    "design": design
                }
                st.session_state['history'].insert(0, history_entry)
                st.session_state["selected_design_id"] = entry_id
                selected_entry = history_entry
                st.success("🎉 Design generated successfully!")

                if st.session_state["auto_generate_images"] and st.session_state["openai_api_key"]:
                    with st.spinner("Rendering patent-style illustration..."):
                        image_result = generate_design_image(
                            prompt,
                            design,
                            st.session_state["openai_api_key"]
                        )
                    st.session_state["design_image_cache"][entry_id] = image_result
                    if image_result.get("error"):
                        st.warning(f"Image generation failed: {image_result['error']}")

            except Exception as e:
                st.error(f"Error generating design: {e}")
                st.stop()

# Determine which design to display
if st.session_state["selected_design_id"] and not selected_entry:
    selected_entry = next(
        (entry for entry in st.session_state['history'] if entry["id"] == st.session_state["selected_design_id"]),
        None
    )

if selected_entry:
    design = selected_entry["design"]
    prompt = selected_entry["prompt"]

    # Design preview image
    st.header("Design Preview")
    cache_entry = st.session_state["design_image_cache"].get(selected_entry["id"])
    preview_image_path = design.get("preview_image")
    if cache_entry and cache_entry.get("image"):
        st.image(
            BytesIO(cache_entry["image"]),
            caption="Patent-grounded design illustration",
            use_container_width=True
        )
    elif preview_image_path:
        path_obj = Path(preview_image_path)
        if path_obj.exists():
            st.image(str(path_obj), caption="Patent figure preview", use_container_width=True)
        else:
            st.warning("Preview image referenced but not found locally.")
            preview_text = design.get("overview", prompt) or prompt
            image_buffer = create_preview_image(preview_text)
            st.image(image_buffer, caption="Concept preview (no image generated yet)", use_container_width=True)
    elif design.get("figures"):
        first_figure = design["figures"][0]
        figure_path = Path(first_figure)
        if figure_path.exists():
            st.image(str(figure_path), caption="Patent figure preview", use_container_width=True)
        else:
            preview_text = design.get("overview", prompt) or prompt
            image_buffer = create_preview_image(preview_text)
            st.image(image_buffer, caption="Concept preview (no image generated yet)", use_container_width=True)
    else:
        preview_text = design.get("overview", prompt) or prompt
        image_buffer = create_preview_image(preview_text)
        st.image(image_buffer, caption="Concept preview (no image generated yet)", use_container_width=True)
        if st.session_state["openai_api_key"]:
            if st.button("Generate patent-style image", key=f"gen_image_{selected_entry['id']}"):
                with st.spinner("Generating illustration with OpenAI..."):
                    image_result = generate_design_image(
                        prompt,
                        design,
                        st.session_state["openai_api_key"]
                    )
                st.session_state["design_image_cache"][selected_entry["id"]] = image_result
                if image_result.get("error"):
                    st.error(f"Image generation failed: {image_result['error']}")
                else:
                    st.experimental_rerun()
        else:
            st.info("Provide an OpenAI API key in the sidebar to generate a patent-style illustration.")

    # Tabs
    tabs = st.tabs([
        "Overview",
        "Modules",
        "Actuation",
        "Sensing",
        "Control",
        "Materials",
        "Safety",
        "Procedure",
        "BOM",
        "Citations"
    ])
    
    # Overview tab
    with tabs[0]:
        st.header("Overview")
        st.write(design.get("overview", "N/A"))
    
    # Modules tab
    with tabs[1]:
        st.header("Modules")
        for module in design.get("modules", []):
            with st.expander(module.get("name", "N/A")):
                st.write(f"**Function:** {module.get('function', 'N/A')}")
                if module.get("citations"):
                    st.write(f"**Citations:** {', '.join(module['citations'])}")
    
    # Actuation tab
    with tabs[2]:
        st.header("Actuation")
        for actuation in design.get("actuation", []):
            with st.expander(actuation.get("subsystem", "N/A")):
                st.write(f"**Choice:** {actuation.get('choice', 'N/A')}")
                st.write(f"**Why:** {actuation.get('why', 'N/A')}")
                if actuation.get("citations"):
                    st.write(f"**Citations:** {', '.join(actuation['citations'])}")
    
    # Sensing tab
    with tabs[3]:
        st.header("Sensing")
        for sensing in design.get("sensing", []):
            with st.expander(sensing.get("subsystem", "N/A")):
                st.write(f"**Sensors:** {', '.join(sensing.get('sensors', []))}")
                st.write(f"**Why:** {sensing.get('why', 'N/A')}")
                if sensing.get("citations"):
                    st.write(f"**Citations:** {', '.join(sensing['citations'])}")
    
    # Control tab
    with tabs[4]:
        st.header("Control")
        for control in design.get("control", []):
            with st.expander(control.get("layer", "N/A")):
                st.write(f"**Approach:** {control.get('approach', 'N/A')}")
                st.write(f"**Mode:** {control.get('teleop_or_auto', 'N/A')}")
                if control.get("citations"):
                    st.write(f"**Citations:** {', '.join(control['citations'])}")
    
    # Materials tab
    with tabs[5]:
        st.header("Materials")
        for material in design.get("materials", []):
            with st.expander(material.get("part", "N/A")):
                st.write(f"**Material:** {material.get('material', 'N/A')}")
                st.write(f"**Why:** {material.get('why', 'N/A')}")
                if material.get("citations"):
                    st.write(f"**Citations:** {', '.join(material['citations'])}")
    
    # Safety tab
    with tabs[6]:
        st.header("Safety")
        for safety in design.get("safety", []):
            with st.expander(safety.get("risk", "N/A")):
                st.write(f"**Mitigation:** {safety.get('mitigation', 'N/A')}")
                if safety.get("citations"):
                    st.write(f"**Citations:** {', '.join(safety['citations'])}")
    
    # Procedure tab
    with tabs[7]:
        st.header("Procedure")
        for i, step in enumerate(design.get("procedure", []), 1):
            st.write(f"{i}. {step}")
    
    # BOM tab
    with tabs[8]:
        st.header("Bill of Materials")
        total_cost = 0
        for item in design.get("bom", []):
            qty = item.get("qty", 1)
            cost = item.get("est_cost_usd", 0)
            total = qty * cost
            total_cost += total
            with st.expander(f"{item.get('item', 'N/A')} - ${total:.2f}"):
                st.write(f"**Quantity:** {qty}")
                st.write(f"**Unit Cost:** ${cost:.2f}")
                st.write(f"**Total Cost:** ${total:.2f}")
                if item.get("citations"):
                    st.write(f"**Citations:** {', '.join(item['citations'])}")
        st.metric("Total Estimated Cost", f"${total_cost:.2f}")
    
    # Citations tab
    with tabs[9]:
        st.header("Citations")
        for citation in design.get("citations", []):
            with st.expander(f"{citation.get('patent_number', 'N/A')}: {citation.get('title', 'N/A')}"):
                st.write(f"**URL:** {citation.get('url', 'N/A')}")
                st.write(f"**Reason:** {citation.get('reason', 'N/A')}")
                fig = citation.get("figure_image")
                if fig:
                    fig_path = Path(fig)
                    if fig_path.exists():
                        st.image(str(fig_path), caption="Patent figure", use_container_width=True)
                    else:
                        st.write("_Figure file not found locally._")
    
    # Download JSON
    st.download_button(
        label="Download Design Brief (JSON)",
        data=json.dumps(design, indent=2),
        file_name="design_brief.json",
        mime="application/json"
    )
else:
    st.header("Construction Robotics Design Generator")
    splash_image = create_preview_image("Enter a prompt or choose a sample to generate a patent-grounded design.")
    st.image(splash_image, caption="Awaiting design prompt…", use_container_width=True)
    st.info(
        "Start by entering a design specification in the text area (or pick a sample prompt in the sidebar) "
        "and click **Generate Design**. The resulting brief will appear here with modules, actuation, sensing, "
        "materials, safety, procedure, BOM, and citations."
    )

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Note:** Make sure the FastAPI server is running: `python app.py`")

