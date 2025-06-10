from flask import Blueprint, render_template, request, jsonify
from app.utils.git_analyzer import analyze_repository
from app.utils.competency import calculate_competency
from app.utils.visualizer import generate_visualizations
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    github_url = data.get('github_url')
    
    if not github_url:
        return jsonify({'error': 'No GitHub URL provided'}), 400
    
    try:
        # Step 1: Extract data from repository
        repo_data = analyze_repository(github_url)
        
        # Step 2: Calculate competency scores
        competency_data = calculate_competency(repo_data)
        
        # Step 3: Generate visualizations
        visualizations = generate_visualizations(competency_data)
        
        return jsonify({
            'status': 'success',
            'visualizations': visualizations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 