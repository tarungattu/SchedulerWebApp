"""Blueprint for benchmark-related routes."""
from flask import Blueprint, jsonify
from config import BENCHMARKS

benchmarks_bp = Blueprint('benchmarks', __name__)

@benchmarks_bp.route('/api/benchmarks', methods=['GET'])
def get_benchmarks():
    """Fetch available benchmarks from the benchmarks file."""
    try:
        benchmark_list = list(BENCHMARKS.keys())
        return jsonify({'success': True, 'benchmarks': benchmark_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

