# app.py - FitSmart AI Flask Backend
# Uses Anthropic Claude API to generate personalised fitness plans

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import anthropic

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Anthropic client using the key from .env
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file. Please add it.")

# Create the Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE: Home page — shows the fitness form
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Render the main input form page."""
    return render_template("index.html")


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE: Generate fitness plan — called via fetch() from the frontend
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/generate", methods=["POST"])
def generate():
    """
    Receives user fitness data as JSON, builds a Claude prompt,
    calls the API, and returns the fitness plan as JSON.
    """
    try:
        # Parse incoming JSON data from the frontend
        data = request.get_json()

        # Extract individual fields
        age        = data.get("age", "25")
        gender     = data.get("gender", "person")
        goal       = data.get("goal", "general fitness")
        preference = data.get("preference", "home")
        time       = data.get("time", "30")

        # ── Build the prompt ──────────────────────────────────────────────────
        prompt = (
            f"Create a beginner-friendly weekly fitness plan for a {age}-year-old {gender} "
            f"whose goal is {goal}. They prefer {preference} workouts and can exercise "
            f"{time} minutes per day. Include a weekly workout schedule, exercises, "
            f"safety tips, and lifestyle advice. Keep it simple and suitable for beginners."
        )

        # ── Call the Claude API ───────────────────────────────────────────────
        message = client.messages.create(
            model="claude-opus-4-6",   # Latest capable Claude model
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the text from the response
        fitness_plan = message.content[0].text

        # Return the plan as a JSON response
        return jsonify({"success": True, "plan": fitness_plan})

    except Exception as e:
        # Return a friendly error message if anything goes wrong
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Run the Flask development server
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
