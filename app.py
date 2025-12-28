import os
from flask import Flask, render_template, request, send_file, jsonify
import json
import io
import zipfile
import requests
from dotenv import load_dotenv
import re
from pypdf import PdfReader
import urllib.parse
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = os.getenv("GENAI_API_KEY")
print(f"🔑 KEY LOADED: {'YES' if API_KEY else 'NO'}")

# --- THEMES (Unchanged) ---
THEMES = {
    "minimalist": { "name": "Modern Minimal", "layout_type": "grid", "aos_mode": "fade-up", "--bg": "#ffffff", "--text": "#121212", "--accent": "#000000", "--font-h": "'Inter', sans-serif", "--font-b": "'Inter', sans-serif", "--radius": "0px", "--card-bg": "#f9f9f9" },
    "cyberpunk": { "name": "Neon Future", "layout_type": "sidebar", "aos_mode": "flip-left", "--bg": "#050505", "--text": "#e0e0e0", "--accent": "#00ff9d", "--font-h": "'Orbitron', sans-serif", "--font-b": "'Rajdhani', sans-serif", "--radius": "4px", "--card-bg": "rgba(0, 255, 157, 0.05)" },
    "luxury": { "name": "Golden Luxury", "layout_type": "centered", "aos_mode": "zoom-in", "--bg": "#0f0f0f", "--text": "#f0f0f0", "--accent": "#d4af37", "--font-h": "'Playfair Display', serif", "--font-b": "'Lato', sans-serif", "--radius": "2px", "--card-bg": "#1a1a1a" },
    "nature": { "name": "Organic Earth", "layout_type": "grid", "aos_mode": "fade-right", "--bg": "#f4f1ea", "--text": "#2c3e2e", "--accent": "#4a6741", "--font-h": "'DM Serif Display', serif", "--font-b": "'Nunito', sans-serif", "--radius": "20px", "--card-bg": "#e9e5db" },
    "terminal": { "name": "Hacker Console", "layout_type": "terminal", "aos_mode": "slide-up", "--bg": "#000000", "--text": "#00ff00", "--accent": "#00aa00", "--font-h": "'Fira Code', monospace", "--font-b": "'Fira Code', monospace", "--radius": "0px", "--card-bg": "#111" },
    "retro": { "name": "Retro 90s", "layout_type": "centered", "aos_mode": "flip-up", "--bg": "#2b0f3a", "--text": "#ffe6f2", "--accent": "#ff00ff", "--font-h": "'Press Start 2P', cursive", "--font-b": "'VT323', monospace", "--radius": "0px", "--card-bg": "rgba(255, 0, 255, 0.1)" },
    "corporate": { "name": "Corporate Pro", "layout_type": "grid", "aos_mode": "fade-up", "--bg": "#ffffff", "--text": "#2d3436", "--accent": "#0984e3", "--font-h": "'Roboto', sans-serif", "--font-b": "'Open Sans', sans-serif", "--radius": "6px", "--card-bg": "#f1f2f6" },
    "brutalist": { "name": "Neo-Brutalist", "layout_type": "sidebar", "aos_mode": "zoom-out-right", "--bg": "#e0e0e0", "--text": "#000000", "--accent": "#ff4757", "--font-h": "'Archivo Black', sans-serif", "--font-b": "'Courier Prime', monospace", "--radius": "0px", "--card-bg": "#ffffff" },
    "pastel": { "name": "Soft Pastel", "layout_type": "grid", "aos_mode": "fade-down", "--bg": "#fff0f5", "--text": "#5e548e", "--accent": "#9f86c0", "--font-h": "'Quicksand', sans-serif", "--font-b": "'Mulish', sans-serif", "--radius": "30px", "--card-bg": "#ffffff" },
    "saas": { "name": "Dark SaaS", "layout_type": "grid", "aos_mode": "fade-up", "--bg": "#0b0c15", "--text": "#a0a0b0", "--accent": "#7c3aed", "--font-h": "'Inter', sans-serif", "--font-b": "'Inter', sans-serif", "--radius": "12px", "--card-bg": "#151621" }
}

# --- HELPER FUNCTIONS ---
def clean_json_text(text):
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if match: return match.group(1).strip()
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match: return match.group(1).strip()
    return text.strip()

def clean_resume_text(text):
    text = re.sub(r'\s+', ' ', text) 
    return text.strip()

def sanitize_title(text):
    if not text: return "Project"
    text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
    text = re.sub(r'[^a-zA-Z0-9 \-]', '', text)
    return text.strip()

def sanitize_scene(text):
    """
    SPEED OPTIMIZATION: 
    Keeps prompts to ~5 words. 
    Short prompts = Faster Generation.
    """
    if not text: return "technology interface"
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    # Limit to 5 words for speed
    words = text.split()[:5]
    return " ".join(words)

# --- MODEL LIST (Speed Prioritized) ---
SAFE_MODELS = [
    "models/gemini-1.5-flash",      
    "models/gemini-1.5-flash-8b",   
    "models/gemini-2.0-flash-exp",
    "models/gemini-2.5-flash",
]

def ask_ai_robust(prompt):
    for model in SAFE_MODELS:
        print(f"   👉 Attempting with: {model}...")
        url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={API_KEY}"
        try:
            response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and data['candidates']:
                    raw = data['candidates'][0]['content']['parts'][0]['text']
                    return json.loads(clean_json_text(raw))
            elif response.status_code in [404, 429]:
                print(f"   ⚠️ {model} failed ({response.status_code}). Switching...")
                continue 
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"   ⚠️ Connection Exception: {e}")
    return None

# --- ANALYZER ---
@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['resume']
    if file.filename == '': return jsonify({"error": "No file"}), 400

    try:
        pdf = PdfReader(file)
        text = "".join([page.extract_text() for page in pdf.pages])
        clean_text = clean_resume_text(text)
        
        if len(clean_text) < 50:
            return jsonify({"error": "PDF seems empty or scanned."}), 400
        
        print(f"📄 Analyzing Resume ({len(clean_text)} chars)...")

        prompt = f"""
        You are a Professional Career Coach. Analyze this resume text to build a portfolio.
        RESUME TEXT: {clean_text[:9000]}
        
        INSTRUCTIONS:
        1. **BASIC INFO:** Extract 'name', 'role', 'tagline', 'bio', 'contact'.
        2. **STATS & SKILLS:** Extract key stats, hard_skills, soft_skills.
        3. **TIMELINE & EDUCATION:** Extract history.
        4. **PROJECTS:** Extract title, tech, desc, impact.
           - **VISUAL SCENE:** Describe the project VISUALLY in 3-5 words. 
           - Rule: Be literal. 
           - Good: "Blue medical app dashboard"
           - Good: "Drone flying over farm"
           - Bad: "Efficiency system"
        
        OUTPUT FORMAT (Strict JSON):
        {{
            "name": "...", "role": "...", "tagline": "...", "bio": "...",
            "contact": {{ "email": "...", "linkedin": "..." }},
            "stats": [ {{"label": "...", "value": "..."}} ],
            "hard_skills": [...], "soft_skills": [...],
            "timeline": [ {{"year": "...", "company": "...", "role": "...", "achievements": [...]}} ],
            "projects": [ {{"title": "...", "tech": "...", "desc": "...", "impact": "...", "visual_scene": "..."}} ],
            "education": [ {{"degree": "...", "school": "...", "year": "..."}} ],
            "testimonials": [ {{"quote": "...", "author": "..."}} ]
        }}
        """

        parsed_data = ask_ai_robust(prompt)
        
        if parsed_data:
            projects = parsed_data.get('projects', [])
            if projects:
                for p in projects:
                    p['title'] = sanitize_title(p.get('title', 'Project'))
                    p['visual_scene'] = sanitize_scene(p.get('visual_scene', 'tech project'))
            
            edu = parsed_data.get('education', [])
            for e in edu:
                if not e.get('school'): e['school'] = "University"
                if not e.get('degree'): e['degree'] = "Degree"
                if not e.get('year'): e['year'] = " "

            return jsonify(parsed_data)
        else:
            return jsonify({"error": "AI Models busy."}), 500

    except Exception as e:
        print(f"Resume Error: {e}")
        return jsonify({"error": str(e)}), 500

# --- GENERATOR ---
def generate_ai_content_fallback(name, role, skills):
    print(f"\n🚀 GENERATING FROM SCRATCH: {name}...")
    prompt = f"""
    Create a JSON portfolio for: Name: {name}, Role: {role}, Skills: {skills}.
    REQUIREMENTS: Projects must have 'visual_scene' (3-5 words).
    """
    data = ask_ai_robust(prompt) or {"name": name, "bio": "Error generation.", "projects": []}
    return data

@app.route('/')
def index():
    return render_template('index.html', themes=THEMES)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form
    theme_key = data.get('theme', 'minimalist')
    extracted_json = data.get('extracted_data')
    
    if extracted_json and len(extracted_json) > 10:
        print("⚡ USING EXTRACTED RESUME DATA")
        content = json.loads(extracted_json)
        content['name'] = data['name'] 
    else:
        content = generate_ai_content_fallback(data['name'], data['role'], data['skills'])

    styles = THEMES.get(theme_key, THEMES['minimalist'])
    return render_template('portfolio.html', name=data['name'], content=content, styles=styles)

@app.route('/download', methods=['POST'])
def download():
    html_content = request.form.get('html_source')
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        zf.writestr('index.html', html_content)
    memory_file.seek(0)
    return send_file(memory_file, download_name='portfolio.zip', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)