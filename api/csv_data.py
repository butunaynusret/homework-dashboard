from flask import Flask, jsonify, request
import csv
import io
import base64
from datetime import datetime
import os
import requests

app = Flask(__name__)

# GitHub configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO')
CSV_FILE_PATH = "homework_report.csv"

def get_github_file(file_path):
    """Get file content from GitHub repository"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        file_content = base64.b64decode(content['content']).decode('utf-8')
        return file_content, content['sha']
    return None, None

def update_github_file(file_path, content, sha, commit_message):
    """Update file content in GitHub repository"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    data = {
        'message': commit_message,
        'content': encoded_content,
        'sha': sha
    }
    
    response = requests.put(url, json=data, headers=headers)
    return response.status_code == 200

@app.route('/api/get_csv', methods=['GET'])
def api_get_csv():
    """API endpoint to get CSV data"""
    try:
        # Get CSV content from GitHub
        csv_content, _ = get_github_file(CSV_FILE_PATH)
        if csv_content is None:
            return jsonify({"error": "CSV file not found"}), 404
        
        # Parse CSV data
        homework_data = []
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        for row in csv_reader:
            homework_data.append(row)
        
        # Sort by due date (descending)
        homework_data.sort(key=lambda x: x.get('endDate', ''), reverse=True)
        
        return jsonify({
            "success": True,
            "data": homework_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update_csv', methods=['POST'])
def api_update_csv():
    """API endpoint to update CSV data"""
    try:
        # Get the updated data from request
        data = request.json
        homework_data = data.get('data', [])
        
        if not homework_data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get current CSV SHA
        _, sha = get_github_file(CSV_FILE_PATH)
        if sha is None:
            return jsonify({"error": "CSV file not found"}), 404
        
        # Generate new CSV content
        output = io.StringIO()
        fieldnames = ['id', 'status', 'teaNameSurname', 'lesson', 'startDate', 'endDate', 'description']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        # Sort by due date (descending) before writing
        homework_data.sort(key=lambda x: x.get('endDate', ''), reverse=True)
        writer.writerows(homework_data)
        
        new_csv_content = output.getvalue()
        
        # Update GitHub file
        commit_message = f"Update homework status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if update_github_file(CSV_FILE_PATH, new_csv_content, sha, commit_message):
            return jsonify({
                "success": True,
                "message": "CSV data updated successfully"
            })
        else:
            return jsonify({"error": "Failed to update GitHub file"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
