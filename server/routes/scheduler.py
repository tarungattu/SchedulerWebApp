"""Blueprint for scheduler/optimization routes."""
from flask import Blueprint, request, jsonify
import numpy as np
from algorithm.JobShopScheduler import JobShopScheduler
from config import BENCHMARKS
from utils.helpers import chromosome_to_dict

scheduler_bp = Blueprint('scheduler', __name__)

@scheduler_bp.route("/api/run", methods=["POST", "OPTIONS"])
def run_scheduler():
    """Run the genetic algorithm scheduler with provided parameters."""
    if request.method == 'OPTIONS':
        # Flask-CORS usually handles this automatically,
        # but you can explicitly return a 200 response if needed.
        return '', 200
    
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

