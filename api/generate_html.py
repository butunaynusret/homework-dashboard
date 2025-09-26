from flask import Flask, jsonify, request, send_file
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
HTML_FILE_PATH = "homework_report.html"

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
        'sha': sha if sha else None
    }
    
    response = requests.put(url, json=data, headers=headers)
    return response.status_code == 200

def generate_html_report(homework_data):
    """Generate beautiful HTML report from homework data"""
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_homework = len(homework_data)
    completed_homework = len([h for h in homework_data if h.get('status', '').strip().lower() == 'done'])
    pending_homework = total_homework - completed_homework
    
    completion_percentage = (completed_homework / total_homework * 100) if total_homework > 0 else 0
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homework Progress Report - Mesut Zahid Bütünay</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: white;
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.3em;
            opacity: 0.95;
            margin-bottom: 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .progress-bar {{
            background: rgba(255,255,255,0.3);
            height: 8px;
            border-radius: 4px;
            margin-top: 15px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: #48bb78;
            border-radius: 4px;
            width: {completion_percentage}%;
            transition: width 0.5s ease;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #2d3748;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #4facfe;
        }}
        
        .table-container {{
            overflow-x: auto;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9em;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: top;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        tr:hover {{
            background-color: #e3f2fd;
            transform: translateY(-1px);
            transition: all 0.3s ease;
        }}
        
        .status-done {{
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 4px rgba(72, 187, 120, 0.3);
        }}
        
        .status-empty {{
            background: #e2e8f0;
            color: #718096;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 500;
            font-size: 0.85em;
        }}
        
        .homework-id {{
            background: linear-gradient(135deg, #4299e1, #3182ce);
            color: white;
            padding: 6px 12px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9em;
            text-align: center;
            min-width: 50px;
        }}
        
        .teacher-name {{
            font-weight: 600;
            color: #2d3748;
        }}
        
        .lesson-name {{
            background: linear-gradient(135deg, #805ad5, #6b46c1);
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: 500;
            text-align: center;
        }}
        
        .date-cell {{
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #4a5568;
            white-space: nowrap;
        }}
        
        .description-cell {{
            max-width: 300px;
            line-height: 1.5;
            color: #2d3748;
        }}
        
        .footer {{
            background: #f7fafc;
            padding: 30px;
            text-align: center;
            color: #718096;
            border-top: 1px solid #e2e8f0;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 10px;
            }}
            
            .header {{
                padding: 30px 20px;
            }}
            
            .header h1 {{
                font-size: 2.2em;
            }}
            
            .content {{
                padding: 30px 20px;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
            }}
            
            .stat-number {{
                font-size: 2em;
            }}
            
            th, td {{
                padding: 12px 8px;
                font-size: 0.85em;
            }}
            
            .description-cell {{
                max-width: 200px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Homework Progress Report</h1>
            <p>Mesut Zahid Bütünay</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_homework}</div>
                    <div class="stat-label">Total Homework</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{completed_homework}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{pending_homework}</div>
                    <div class="stat-label">Pending</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{completion_percentage:.1f}%</div>
                    <div class="stat-label">Progress</div>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <h2 class="section-title">📋 Homework Assignments</h2>
            
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Status</th>
                            <th>Teacher</th>
                            <th>Subject</th>
                            <th>Start Date</th>
                            <th>Due Date</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>"""
    
    # Add homework rows
    for homework in homework_data:
        status = homework.get('status', '').strip()
        status_class = 'status-done' if status.lower() == 'done' else 'status-empty'
        status_text = status if status else 'Not Started'
        
        html_content += f"""
                        <tr>
                            <td><div class="homework-id">{homework.get('id', '')}</div></td>
                            <td><span class="{status_class}">{status_text}</span></td>
                            <td><div class="teacher-name">{homework.get('teaNameSurname', '')}</div></td>
                            <td><div class="lesson-name">{homework.get('lesson', '')}</div></td>
                            <td><div class="date-cell">{homework.get('startDate', '')}</div></td>
                            <td><div class="date-cell">{homework.get('endDate', '')}</div></td>
                            <td><div class="description-cell">{homework.get('description', '')}</div></td>
                        </tr>"""
    
    html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Report Generated:</strong> {current_time}</p>
            <p>📊 Total: {total_homework} assignments | ✅ Completed: {completed_homework} | ⏳ Pending: {pending_homework}</p>
            <p>🎯 Progress: {completion_percentage:.1f}%</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_content

@app.route('/api/generate_html', methods=['POST'])
def api_generate_html():
    """API endpoint to generate HTML report"""
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
        
        if not homework_data:
            return jsonify({"error": "No homework data found"}), 404
        
        # Sort by due date (descending)
        homework_data.sort(key=lambda x: x.get('endDate', ''), reverse=True)
        
        # Generate HTML
        html_content = generate_html_report(homework_data)
        
        # Get existing HTML SHA (if exists)
        _, html_sha = get_github_file(HTML_FILE_PATH)
        
        # Update HTML file in GitHub
        commit_message = f"Generate HTML report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if update_github_file(HTML_FILE_PATH, html_content, html_sha, commit_message):
            return jsonify({
                "success": True,
                "message": "HTML report generated successfully",
                "url": f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{HTML_FILE_PATH}"
            })
        else:
            return jsonify({"error": "Failed to update HTML file"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
