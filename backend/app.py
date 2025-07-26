from flask import Flask, request, jsonify
import json
import os
from algorithm.JobShopScheduler import JobShopScheduler
from flask_cors import CORS
import numpy as np

app = Flask(__name__ , static_folder='static')
CORS(app)

BENCHMARKS_PATH = os.path.join(os.path.dirname(__file__), 'benchmarks', 'benchmarks.json')
with open(BENCHMARKS_PATH, 'r') as f:
    BENCHMARKS = json.load(f)
    
# # Global state
# global_state = {
#     "machine_data": None,
#     "ptime_data": None,
#     "distance_matrix": None
# }

def chromosome_to_dict(chromo_obj):
    return {
        "encoded_list": chromo_obj.encoded_list,
        "ranked_list": chromo_obj.ranked_list,
        "operation_index_list": chromo_obj.operation_index_list,
        # "job_list": chromo_obj.job_list,
        # "amr_list": chromo_obj.amr_list,
        # "operation_schedule": chromo_obj.operation_schedule,
        "machine_sequence": chromo_obj.machine_sequence,
        # "machine_list": chromo_obj.machine_list,
        "ptime_sequence": chromo_obj.ptime_sequence,
        "Cmax": chromo_obj.Cmax,
        "penalty": chromo_obj.penalty,
        "fitness": chromo_obj.fitness,
        "amr_machine_sequences": chromo_obj.amr_machine_sequences,
        "amr_ptime_sequences": chromo_obj.amr_ptime_sequences
    }


# Fetch available benchmarks
@app.route('/api/benchmarks', methods=['GET'])
def get_benchmarks():
    try:
        benchmark_list = list(BENCHMARKS.keys())
        return jsonify({'success': True, 'benchmarks': benchmark_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# @app.route("/api/select-benchmark", methods=["POST"])
# def select_benchmark():
#     data = request.get_json()
#     benchmark_name = data.get("benchmark_name")
#     if not benchmark_name or benchmark_name not in BENCHMARKS:
#         return jsonify({"error": "Invalid benchmark name"}), 400
#     benchmark = BENCHMARKS[benchmark_name]
#     global_state["machine_data"] = benchmark.get("machine_data")
#     global_state["ptime_data"] = benchmark.get("ptime_data")
#     return jsonify({"message": f"Benchmark '{benchmark_name}' selected successfully."})

# set distance matrix 
# @app.route("/api/distance-matrix", methods=["POST"])
# def set_distance_matrix():
#     data = request.get_json()
#     distance_matrix = data.get("distance_matrix")
#     if distance_matrix is None:
#         return jsonify({"error": "No distance_matrix provided"}), 400
#     global_state["distance_matrix"] = distance_matrix
#     return jsonify({"message": "Distance matrix stored successfully."})

# Run the scheduling algorithm
@app.route("/api/run", methods=["POST"])
def run_scheduler():
    ''' Sets GA parameters and runs the JobShopScheduler '''
    req_data = request.get_json()

    benchmark_name = req_data.get("benchmark_name")
    if benchmark_name and benchmark_name in BENCHMARKS:
        machine_data = BENCHMARKS[benchmark_name]["machine_data"]
        ptime_data = BENCHMARKS[benchmark_name]["ptime_data"]
    else:
        machine_data = req_data.get("machine_data")
        if machine_data is None:
            machine_data = BENCHMARKS["pinedo"]["machine_data"]

        ptime_data = req_data.get("ptime_data")
        if ptime_data is None:
            ptime_data = BENCHMARKS["pinedo"]["ptime_data"]
        
    distance_matrix = np.array(req_data.get("distance_matrix"))
    m = req_data.get("m", 4)
    n = BENCHMARKS[benchmark_name]["n"]
    N = req_data.get("N", 200)
    T = req_data.get("T", 200)
    Pm = req_data.get("Pm", 0.5)
    Pc = req_data.get("Pc", 0.7)
    a = req_data.get("a", 2)
    stagnation_limit = req_data.get("stagnation_limit", 40)
    scheduler1 = JobShopScheduler(m, n, a, N, Pc, Pm, T, machine_data, ptime_data)    
    scheduler1.set_distance_matrix(distance_matrix)
    scheduler1.stagnation_limit = stagnation_limit
    
    best_chromosome = JobShopScheduler.GeneticAlgorithm(scheduler1)
    dict_chromosome = chromosome_to_dict(best_chromosome)
    
    image_url = request.host_url.rstrip('/') + '/static/result.png'
    return jsonify({
        "chromosome": dict_chromosome,
        "image_url": image_url
    })

if __name__ == "__main__":
    app.run(debug=True)
