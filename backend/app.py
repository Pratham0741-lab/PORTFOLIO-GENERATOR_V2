import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import numpy as np
from sklearn.neighbors import NearestNeighbors
import json
import random
# At the top of app.py
from dotenv import load_dotenv
load_dotenv()

# Replace the hardcoded key line with this:
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
app = Flask(__name__)
CORS(app)

# 🛑 PASTE YOUR KEY HERE
GOOGLE_API_KEY = "AIzaSyA_tnwSeusLE66HDG2kgUq_H4o3eCaBDeU"
genai.configure(api_key=GOOGLE_API_KEY)

ARCHETYPES = {
    0: "swiss", 1: "cyber", 2: "brutal", 3: "ethereal", 4: "midnight",
    5: "paper", 6: "bauhaus", 7: "y2k", 8: "botanical", 9: "obsidian"
}

X_train = np.array([
    [100, 0, 0], [100, 100, 0], [0, 100, 0], [10, 10, 100], [50, 50, 30],
    [30, 20, 90], [80, 60, 80], [40, 90, 50], [20, 10, 70], [90, 10, 20]
])

model = NearestNeighbors(n_neighbors=1).fit(X_train)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        s = int(data.get('structure', 50))
        e = int(data.get('energy', 50))
        w = int(data.get('warmth', 50))
        
        distances, indices = model.kneighbors([[s, e, w]])
        archetype_id = ARCHETYPES[indices[0][0]]
        print(f"Matched: {archetype_id.upper()}")

        # --- AI GENERATION ---
        try:
            # ✅ FIX: Updated to your available model
            model_name = 'gemini-2.5-flash' 
            gemini = genai.GenerativeModel(model_name)
            
            prompt = f"""
            You are a design engine. Generate a JSON portfolio for a designer with the '{archetype_id}' aesthetic.
            Traits: Structure {s}%, Energy {e}%, Warmth {w}%.
            
            1. Create a "User Manual" warning/fact about this personality.
            2. Generate 2 short "Articles" or "Thought Logs".
            
            Output strictly valid JSON (no markdown):
            {{
                "tagline": "Header",
                "bio": "Bio",
                "manual": "User Manual Text",
                "stats": [{{"label": "Stat 1", "value": 80}}, {{"label": "Stat 2", "value": 40}}],
                "projects": [
                    {{"title": "Project A", "desc": "Desc"}},
                    {{"title": "Project B", "desc": "Desc"}}
                ],
                "articles": [
                    {{"title": "Blog Post 1", "date": "Oct 12", "content": "Summary."}},
                    {{"title": "Blog Post 2", "date": "Nov 08", "content": "Summary."}}
                ]
            }}
            """
            response = gemini.generate_content(prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            content = json.loads(clean_json)
            
        except Exception as err:
            print(f"AI Error ({model_name}): {err}")
            
            # FALLBACK: Try Gemini 2.0 Flash if 2.5 fails
            try:
                print("Attempting fallback to gemini-2.0-flash-exp...")
                gemini = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = gemini.generate_content(prompt)
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                content = json.loads(clean_json)
            except Exception as e2:
                print(f"Fallback Error: {e2}")
                # FINAL FALLBACK (Offline Data)
                content = {
                    "tagline": "Offline Mode", 
                    "bio": "AI connection failed. Check API Key.",
                    "manual": "System Offline.",
                    "stats": [{"label": "Error", "value": 0}],
                    "projects": [],
                    "articles": []
                }

        return jsonify({"archetype": archetype_id, "content": content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)