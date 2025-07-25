from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Load benchmarks from JSON file
@app.route("/api/benchmarks", methods=["GET"])
def get_benchmarks():
    filepath = os.path.join(os.path.dirname(__file__), "benchmarks", "benchmarks.json")
    with open(filepath, "r") as f:
        data = json.load(f)
    return jsonify(data)

# Run the scheduling algorithm
@app.route("/api/run", methods=["POST"])
def run_scheduler():
    req_data = request.get_json()

    # Example: extract benchmark data
    benchmark = req_data.get("benchmark")  # ID or name
    machine_data = req_data.get("machine_data")
    ptime_data = req_data.get("ptime_data")

    # Dummy response for now — we'll connect the real algorithm later
    result = {
        "status": "success",
        "message": f"Ran scheduler on benchmark {benchmark}",
        "schedule": []  # placeholder
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
