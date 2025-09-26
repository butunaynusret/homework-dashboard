from flask import Flask, jsonify, request
import requests
import json
import csv
import io
import base64
from datetime import datetime
import os
from session_manager import session_manager

app = Flask(__name__)

# GitHub configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO')  # format: "username/repo-name"
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

def fetch_homework_data():
    """Make API call to fetch homework data using session manager"""
    return session_manager.get_homework_list()

def fetch_homework_detail(homework_id):
    """Make API call to fetch homework detail data for a specific ID using session manager"""
    return session_manager.get_homework_detail(homework_id)

@app.route('/api/fetch_homework', methods=['POST'])
def api_fetch_homework():
    """API endpoint to fetch and update homework data"""
    try:
        # Get existing CSV content
        csv_content, sha = get_github_file(CSV_FILE_PATH)
        if csv_content is None:
            # Create new CSV if doesn't exist
            csv_content = "id,status,teaNameSurname,lesson,startDate,endDate,description\n"
            sha = None
        
        # Parse existing CSV
        existing_ids = set()
        existing_rows = []
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        fieldnames = csv_reader.fieldnames or ['id', 'status', 'teaNameSurname', 'lesson', 'startDate', 'endDate', 'description']
        
        for row in csv_reader:
            existing_rows.append(row)
            if row.get('id'):
                existing_ids.add(str(row['id']))
        
        # Fetch new homework data
        homework_list_data = fetch_homework_data()
        if not homework_list_data:
            return jsonify({"error": "Failed to fetch homework data"}), 500
        
        # Extract homework items
        homework_items = []
        if isinstance(homework_list_data, dict) and 'data' in homework_list_data:
            homework_items = homework_list_data['data']
        elif isinstance(homework_list_data, list):
            homework_items = homework_list_data
        
        # Find new homework items
        new_items = []
        for item in homework_items:
            homework_id = str(item.get('id', ''))
            if homework_id and homework_id not in existing_ids:
                # Fetch details
                detail_data = fetch_homework_detail(homework_id)
                description = ''
                if detail_data and isinstance(detail_data, dict):
                    if 'data' in detail_data and isinstance(detail_data['data'], dict):
                        description = detail_data['data'].get('description', '')
                    elif 'description' in detail_data:
                        description = detail_data['description']
                
                item['description'] = description
                new_items.append(item)
        
        # Sort new items by due date (descending)
        new_items.sort(key=lambda x: x.get('endDate', ''), reverse=True)
        
        # Combine existing and new data
        all_rows = existing_rows.copy()
        for item in new_items:
            row = {
                'id': item.get('id', ''),
                'status': '',  # Empty for manual filling
                'teaNameSurname': item.get('teaNameSurname', ''),
                'lesson': item.get('lesson', ''),
                'startDate': item.get('startDate', ''),
                'endDate': item.get('endDate', ''),
                'description': item.get('description', '')
            }
            all_rows.append(row)
        
        # Sort all rows by due date (descending)
        all_rows.sort(key=lambda x: x.get('endDate', ''), reverse=True)
        
        # Generate new CSV content
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
        new_csv_content = output.getvalue()
        
        # Update GitHub file
        commit_message = f"Auto-update homework data - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if update_github_file(CSV_FILE_PATH, new_csv_content, sha, commit_message):
            return jsonify({
                "success": True,
                "message": f"Added {len(new_items)} new homework items",
                "new_items": len(new_items),
                "total_items": len(all_rows)
            })
        else:
            return jsonify({"error": "Failed to update GitHub file"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
