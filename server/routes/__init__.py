"""Route blueprints registration."""
from .benchmarks import benchmarks_bp
from .distance_matrix import distance_matrix_bp
from .scheduler import scheduler_bp

def register_blueprints(app):
    """
    Register all route blueprints with the Flask application.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(benchmarks_bp)
    app.register_blueprint(distance_matrix_bp)
    app.register_blueprint(scheduler_bp)

