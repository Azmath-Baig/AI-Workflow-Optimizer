import os
import json
import re
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from jsonschema import validate, ValidationError

load_dotenv()

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"

# ----------------------------------------
# STRICT ENGINEERING SCHEMA
# ----------------------------------------
SCHEMA = {
    "type": "object",
    "properties": {
        "project_specification": {"type": "object"},
        "folder_structure": {"type": "object"},
        "environment_variables": {"type": "array"},
        "security_architecture": {"type": "object"},
        "optimized_prompt": {"type": "object"},
        "ai_prompt_strategy": {
            "type": "object",
            "properties": {
                "generation_sequence": {"type": "array"},
                "validation_loop": {"type": "string"},
                "self_critique_strategy": {"type": "string"},
                "hallucination_prevention_rules": {"type": "array"}
            },
            "required": [
                "generation_sequence",
                "validation_loop",
                "self_critique_strategy",
                "hallucination_prevention_rules"
            ]
        },
        "interaction_plan": {"type": "array"},
        "risks": {"type": "array"},
        "ai_failure_cases": {"type": "array"},
        "testing_checklist": {"type": "array"},
        "refactor_advice": {"type": "array"},
        "secret_hacks": {"type": "array"}
    },
    "required": [
        "project_specification",
        "folder_structure",
        "environment_variables",
        "security_architecture",
        "optimized_prompt",
        "ai_prompt_strategy",
        "interaction_plan",
        "risks",
        "ai_failure_cases",
        "testing_checklist",
        "refactor_advice",
        "secret_hacks"
    ]
}

# ----------------------------------------
# GROQ CALL
# ----------------------------------------
def call_groq(messages, temperature=0.3):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature
    }

    response = requests.post(GROQ_URL, headers=headers, json=data, timeout=20)
    response.raise_for_status()
    
    result = response.json()
    return result["choices"][0]["message"]["content"]

# ----------------------------------------
# SAFE JSON EXTRACTION
# ----------------------------------------
def extract_json(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
    return None

# ----------------------------------------
# SELF CRITIQUE PASS
# ----------------------------------------
def critique_plan(plan_json):
    critique_prompt = f"""
You are a strict senior software architect.

Critique this plan for:

- Security completeness
- Architecture clarity
- Production readiness
- Specificity (no vague wording)
- Hallucination risks

Return STRICT JSON:

{{
  "weaknesses": [],
  "security_gaps": [],
  "architecture_issues": [],
  "hallucination_risk_score": "1-10",
  "overall_score": "1-10",
  "improvement_suggestions": []
}}

Plan:
{json.dumps(plan_json)}
"""

    messages = [
        {"role": "system", "content": "You are a strict backend architecture reviewer."},
        {"role": "user", "content": critique_prompt}
    ]

    response = call_groq(messages, temperature=0.2)
    return extract_json(response)

# ----------------------------------------
# ENGINEERING SCORE PASS
# ----------------------------------------
def engineering_score(plan_json):
    score_prompt = f"""
Score this engineering plan from 1-10 based on:

- Production readiness
- Security depth
- Architecture quality
- Anti-hallucination discipline
- Specificity

Return STRICT JSON:

{{
  "production_score": "1-10",
  "security_score": "1-10",
  "architecture_score": "1-10",
  "specificity_score": "1-10",
  "overall_engineering_score": "1-10"
}}

Plan:
{json.dumps(plan_json)}
"""
    messages = [
        {"role": "system", "content": "You are a senior engineering evaluator."},
        {"role": "user", "content": score_prompt}
    ]

    response = call_groq(messages, temperature=0.2)
    return extract_json(response)

# ----------------------------------------
# REGENERATION PASS
# ----------------------------------------
def regenerate_if_invalid(original_output, goal, stack, experience, constraints):
    repair_prompt = f"""
The following output failed JSON validation.

Fix it strictly according to required structure.

DO NOT add explanations.

Invalid Output:
{original_output}

Goal: {goal}
Tech Stack: {stack}
Experience Level: {experience}
Constraints: {constraints}

Return ONLY valid JSON.
"""

    messages = [
        {"role": "system", "content": "You repair invalid structured engineering JSON."},
        {"role": "user", "content": repair_prompt}
    ]

    return call_groq(messages, temperature=0.2)

# ----------------------------------------
# ROUTES
# ----------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/optimize", methods=["POST"])
def optimize_workflow():
    try:
        user_input = request.json

        goal = user_input.get("goal", "")
        stack = user_input.get("stack", "")
        experience = user_input.get("experience", "")
        constraints = user_input.get("constraints", "")

        system_prompt = """
You are a senior backend architect and AI-assisted engineering workflow designer.

This is NOT a machine learning research task.

STRICT RULES:
- Do NOT mention training models, fine-tuning, adversarial learning, or ML pipelines.
- No buzzwords.
- No vague language.
- All architecture must be concrete and framework-specific.
- Must include environment variable usage.
- Must include security architecture.
- Must include deployment considerations.
- Must include validation and testing strategy.

Return STRICT JSON with EXACT structure:

{
  "project_specification": {},
  "folder_structure": {},
  "environment_variables": [],
  "security_architecture": {},
  "optimized_prompt": {},
  "ai_prompt_strategy": {
    "generation_sequence": [],
    "validation_loop": "",
    "self_critique_strategy": "",
    "hallucination_prevention_rules": []
  },
  "interaction_plan": [],
  "risks": [],
  "ai_failure_cases": [],
  "testing_checklist": [],
  "refactor_advice": [],
  "secret_hacks": []
}

No explanation outside JSON.
Be production-oriented.
"""

        user_prompt = f"""
Goal: {goal}
Tech Stack: {stack}
Experience Level: {experience}
Constraints: {constraints}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # PASS 1 – GENERATE
        ai_response = call_groq(messages)
        parsed_json = extract_json(ai_response)

        # PASS 2 – REPAIR IF INVALID
        if not parsed_json:
            repaired = regenerate_if_invalid(ai_response, goal, stack, experience, constraints)
            parsed_json = extract_json(repaired)

        if not parsed_json:
            return jsonify({
                "error": "Failed to produce valid JSON",
                "raw": ai_response
            }), 500

        try:
            validate(instance=parsed_json, schema=SCHEMA)
        except ValidationError:
            repaired = regenerate_if_invalid(ai_response, goal, stack, experience, constraints)
            parsed_json = extract_json(repaired)

        # PASS 3 – SELF CRITIQUE
        critique = critique_plan(parsed_json)
        parsed_json["ai_self_critique"] = critique

        # PASS 4 – ENGINEERING SCORE
        score = engineering_score(parsed_json)
        parsed_json["engineering_review"] = score

        # PASS 5 – SCORE-BASED AUTONOMOUS REGENERATION
        regeneration_applied = False
        if score:
            try:
                score_val_str = str(score.get("overall_engineering_score", "0"))
                score_val = int(score_val_str.split("/")[0].strip() if "/" in score_val_str else score_val_str)
                
                if score_val < 6:
                    improved = regenerate_if_invalid(
                        json.dumps(parsed_json),
                        goal,
                        stack,
                        experience,
                        constraints
                    )
                    improved_json = extract_json(improved)
                    if improved_json:
                        parsed_json = improved_json
                        regeneration_applied = True
                        # Re-score the improved version
                        improved_score = engineering_score(parsed_json)
                        parsed_json["engineering_review"] = improved_score
            except (ValueError, AttributeError):
                pass  # If score parsing fails, skip regeneration

        # META
        parsed_json["meta"] = {
            "model_used": MODEL_NAME,
            "temperature": 0.3,
            "multi_pass": True,
            "schema_enforced": True,
            "auto_regeneration_applied": regeneration_applied
        }

        return jsonify(parsed_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
