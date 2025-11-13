"""Blueprint for distance matrix generation routes."""
from flask import Blueprint, request, jsonify

distance_matrix_bp = Blueprint('distance_matrix', __name__)

@distance_matrix_bp.route('/api/generate-distance-matrix', methods=['POST', 'OPTIONS'])
def generate_distance_matrix():
    """Generate distance matrix from machine and dock positions using Manhattan distance."""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        req_data = request.get_json()
        
        machines = req_data.get('machines', [])
        loading_dock = req_data.get('loadingDock')
        unloading_dock = req_data.get('unloadingDock')
        grid_size = req_data.get('gridSize', 40)
        
        # Validation
        if not machines or len(machines) == 0:
            return jsonify({'success': False, 'error': 'Need at least 1 machine'}), 400
        
        if not loading_dock:
            return jsonify({'success': False, 'error': 'Loading dock is required'}), 400
        
        if not unloading_dock:
            return jsonify({'success': False, 'error': 'Unloading dock is required'}), 400
        
        # Combine entities: machines first, then loading dock, then unloading dock
        entities = []
        for machine in machines:
            entities.append({
                'x': machine.get('x', 0),
                'y': machine.get('y', 0)
            })
        entities.append({
            'x': loading_dock.get('x', 0),
            'y': loading_dock.get('y', 0)
        })
        entities.append({
            'x': unloading_dock.get('x', 0),
            'y': unloading_dock.get('y', 0)
        })
        
        # Generate distance matrix using Manhattan distance
        n = len(entities)
        matrix = []
        
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(0)
                else:
                    entity1 = entities[i]
                    entity2 = entities[j]
                    # Manhattan distance: |x1/gridSize - x2/gridSize| + |y1/gridSize - y2/gridSize|
                    distance = abs(entity1['x'] / grid_size - entity2['x'] / grid_size) + \
                              abs(entity1['y'] / grid_size - entity2['y'] / grid_size)
                    row.append(int(distance))
            matrix.append(row)
        
        return jsonify({
            'success': True,
            'matrix': matrix,
            'size': n
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

