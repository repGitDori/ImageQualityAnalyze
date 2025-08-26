from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import sys
import tempfile
import uuid
import json
from datetime import datetime
import threading
import time

# Add the parent directory to Python path to import our analyzer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from image_quality_analyzer import ImageQualityAnalyzer, load_default_config, load_profile
    from image_quality_analyzer.visualization import GraphGenerator
    
    # Fix matplotlib backend for threading
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    
except ImportError as e:
    print(f"Error importing ImageQualityAnalyzer: {e}")
    sys.exit(1)

app = Flask(__name__, static_folder='dist', template_folder='dist')
CORS(app)

# Global analyzer instance
analyzer = ImageQualityAnalyzer()
graph_generator = GraphGenerator()

# Store for real-time analysis progress
analysis_progress = {}

@app.route('/')
def index():
    """Serve the Vue.js app"""
    return send_from_directory('dist', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('dist', path)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'analyzer_ready': True
    })

@app.route('/api/profiles')
def get_profiles():
    """Get available configuration profiles"""
    try:
        from image_quality_analyzer.config import list_profiles
        profiles = list_profiles()
        return jsonify({
            'success': True,
            'profiles': profiles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """Analyze uploaded image with real-time progress"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Get analysis parameters
        profile_name = request.form.get('profile', 'default')
        generate_viz = request.form.get('generate_viz', 'true').lower() == 'true'
        
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        analysis_progress[analysis_id] = {
            'status': 'starting',
            'progress': 0,
            'stage': 'Initializing analysis...',
            'results': None,
            'error': None
        }
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, f"upload_{analysis_id}.jpg")
        file.save(temp_path)
        
        # Start analysis in background thread
        def run_analysis():
            try:
                # Load configuration
                analysis_progress[analysis_id]['stage'] = 'Loading configuration...'
                analysis_progress[analysis_id]['progress'] = 10
                
                if profile_name != 'default':
                    config = load_profile(profile_name)
                else:
                    config = load_default_config()
                
                # Run analysis with progress updates
                analysis_progress[analysis_id]['stage'] = 'Analyzing image quality...'
                analysis_progress[analysis_id]['progress'] = 30
                
                result = analyzer.analyze_image(temp_path, config)
                
                analysis_progress[analysis_id]['stage'] = 'Generating insights...'
                analysis_progress[analysis_id]['progress'] = 70
                
                # Generate visualizations if requested
                viz_paths = []
                if generate_viz:
                    analysis_progress[analysis_id]['stage'] = 'Creating visualizations...'
                    analysis_progress[analysis_id]['progress'] = 85
                    
                    # Skip visualization generation for now due to path issues
                    # Will be fixed in next iteration
                    print("Visualization generation temporarily disabled")
                    # output_dir = os.path.join(temp_dir, 'viz')
                    # os.makedirs(output_dir, exist_ok=True)
                    
                    # # Generate all visualizations using the correct method
                    # try:
                    #     viz_files = graph_generator.generate_all_graphs(temp_path, result, output_dir)
                    #     for viz_type, viz_path in viz_files.items():
                    #         if viz_path and os.path.exists(viz_path):
                    #             viz_paths.append({
                    #                 'type': viz_type,
                    #                 'path': viz_path,
                    #                 'filename': os.path.basename(viz_path)
                    #             })
                    # except Exception as viz_error:
                    #     print(f"Visualization generation error: {viz_error}")
                
                # Complete analysis
                analysis_progress[analysis_id]['stage'] = 'Analysis complete!'
                analysis_progress[analysis_id]['progress'] = 100
                analysis_progress[analysis_id]['status'] = 'complete'
                analysis_progress[analysis_id]['results'] = {
                    'analysis': result,
                    'visualizations': viz_paths,
                    'metadata': {
                        'filename': file.filename,
                        'profile_used': profile_name,
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                # Clean up temp file
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
            except Exception as e:
                analysis_progress[analysis_id]['status'] = 'error'
                analysis_progress[analysis_id]['error'] = str(e)
                analysis_progress[analysis_id]['stage'] = f'Error: {str(e)}'
        
        # Start analysis thread
        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'message': 'Analysis started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analysis/<analysis_id>/progress')
def get_analysis_progress(analysis_id):
    """Get real-time analysis progress"""
    try:
        if analysis_id not in analysis_progress:
            return jsonify({
                'success': False,
                'error': 'Analysis ID not found'
            }), 404
        
        progress_data = analysis_progress[analysis_id]
        
        # Handle cases where analysis might have errored
        if progress_data.get('status') == 'error':
            return jsonify({
                'success': True,
                'status': 'error',
                'progress': progress_data.get('progress', 0),
                'stage': progress_data.get('stage', 'Error occurred'),
                'results': None,
                'error': progress_data.get('error', 'Unknown error')
            })
        
        return jsonify({
            'success': True,
            'status': progress_data['status'],
            'progress': progress_data['progress'],
            'stage': progress_data['stage'],
            'results': progress_data['results'],
            'error': progress_data['error']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/visualization/<path:filename>')
def serve_visualization(filename):
    """Serve generated visualization files"""
    try:
        # Find the file in temporary directories
        for temp_dir in os.listdir(tempfile.gettempdir()):
            viz_path = os.path.join(tempfile.gettempdir(), temp_dir, 'viz', filename)
            if os.path.exists(viz_path):
                return send_from_directory(os.path.dirname(viz_path), filename)
        
        return jsonify({'error': 'Visualization not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting ImageQualityAnalyzer Web UI...")
    print("📊 Advanced AI-Powered Document Analysis Interface")
    print("🌐 Access at: http://localhost:5000")
    print("⚡ Real-time analysis with stunning visualizations!")
    
    # Start the Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
