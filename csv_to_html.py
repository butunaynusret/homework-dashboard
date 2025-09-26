#!/usr/bin/env python3
"""
CSV to HTML Converter
Converts the homework CSV report to a beautiful HTML page with status styling
"""

import csv
from datetime import datetime
import sys
import os

def read_csv_data(csv_file_path):
    """Read CSV data and return list of dictionaries"""
    
    homework_data = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                homework_data.append(row)
        
        print(f"📊 Successfully read {len(homework_data)} homework records from CSV")
        return homework_data
        
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_file_path}")
        return None
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return None

def generate_html_report(homework_data):
    """Generate beautiful HTML report from homework data"""
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_homework = len(homework_data)
    completed_homework = len([h for h in homework_data if h.get('status', '').strip().lower() == 'done'])
    pending_homework = total_homework - completed_homework
    
    # Calculate completion percentage
    completion_percentage = (completed_homework / total_homework * 100) if total_homework > 0 else 0
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homework Progress Report - Bogazici Sehir Koleji</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        
        .header::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
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
            display: flex;
            align-items: center;
            gap: 10px;
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
        
        .status-pending {{
            background: linear-gradient(135deg, #ed8936, #dd6b20);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 4px rgba(237, 137, 54, 0.3);
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
        
        .footer p {{
            margin-bottom: 10px;
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        
        .legend-done {{ background: #48bb78; }}
        .legend-pending {{ background: #ed8936; }}
        .legend-empty {{ background: #e2e8f0; }}
        
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
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-dot legend-done"></div>
                    <span>Completed</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot legend-pending"></div>
                    <span>In Progress</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot legend-empty"></div>
                    <span>Not Started</span>
                </div>
            </div>
            
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
        status_class = 'status-done' if status.lower() == 'done' else ('status-pending' if status else 'status-empty')
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
            <p>🎯 Keep up the great work! You're {completion_percentage:.1f}% through your homework!</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_content

def sort_and_rewrite_csv(csv_file_path):
    """Sort the existing CSV file by due date and rewrite it"""
    
    try:
        # Read all data
        homework_data = []
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                homework_data.append(row)
        
        # Sort by due date (descending - most recent due dates first)
        homework_data.sort(key=lambda x: x.get('endDate', ''), reverse=True)
        
        # Rewrite the CSV file with sorted data
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            if homework_data:
                fieldnames = homework_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(homework_data)
        
        print("🔄 Sorted and updated CSV file by due date")
        return True
        
    except Exception as e:
        print(f"⚠️ Warning: Could not sort CSV file: {e}")
        return False

def main():
    """Main function to convert CSV to HTML"""
    print("🚀 Starting CSV to HTML conversion...")
    
    # Define file paths
    csv_file_path = "/Users/nusretbutunay/Desktop/personal/homework_report.csv"
    html_file_path = "/Users/nusretbutunay/Desktop/personal/homework_report.html"
    
    # Check if CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        print("💡 Please run homework_fetcher.py first to generate the CSV file")
        return 1
    
    # Sort the CSV file by due date first
    sort_and_rewrite_csv(csv_file_path)
    
    # Read CSV data
    homework_data = read_csv_data(csv_file_path)
    
    if homework_data is None:
        print("❌ Failed to read CSV data")
        return 1
    
    if not homework_data:
        print("📭 No homework data found in CSV")
        return 0
    
    # Generate HTML report
    print("🎨 Generating beautiful HTML report...")
    html_content = generate_html_report(homework_data)
    
    # Save HTML file
    try:
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report generated successfully!")
        print(f"📄 Saved to: {html_file_path}")
        print(f"🌐 Open the file in your browser to view your homework progress!")
        
        # Show summary stats
        total = len(homework_data)
        completed = len([h for h in homework_data if h.get('status', '').strip().lower() == 'done'])
        pending = total - completed
        percentage = (completed / total * 100) if total > 0 else 0
        
        print(f"\n📊 Summary:")
        print(f"   📚 Total Homework: {total}")
        print(f"   ✅ Completed: {completed}")
        print(f"   ⏳ Pending: {pending}")
        print(f"   🎯 Progress: {percentage:.1f}%")
        
    except Exception as e:
        print(f"❌ Error saving HTML file: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
