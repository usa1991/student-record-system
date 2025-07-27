# ollama_parser.py
import subprocess
import json

OLLAMA_MODEL = "mistral"  # Change if needed

def parse_pdf_with_ollama(raw_text):
    prompt = f"""
You are an intelligent document parser. Given the following PDF text, extract:

1. Student Name
2. Roll Number
3. Subject-wise marks (as a list of tuples)

PDF TEXT:
\"\"\"
{raw_text}
\"\"\"

Respond ONLY in the following JSON format:
{{
  "name": "...",
  "roll": "...",
  "marks": [ ["Subject 1", 90], ["Subject 2", 85] ]
}}
"""
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )

        output = result.stdout.decode("utf-8", errors="ignore")
        json_start = output.find("{")
        json_str = output[json_start:]
        data = json.loads(json_str)

        return data["name"], data["roll"], data["marks"]

    except Exception as e:
        raise RuntimeError("❌ Ollama parsing failed:\n" + str(e))
