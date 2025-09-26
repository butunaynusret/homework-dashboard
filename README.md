# Homework Fetcher

A Python script that fetches homework data from the Bogazici Sehir Koleji OBS API and generates a CSV report with homework details.

## Features

- 🚀 Makes authenticated API calls to fetch homework data
- 📊 Generates CSV reports with specific columns
- 📝 Fetches detailed descriptions for each homework assignment
- 💾 Compatible with Excel, Google Sheets, and any spreadsheet application
- 🔄 Automatically processes multiple homework items in batch

## Requirements

- Python 3.6 or higher
- `requests` library

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
python3 homework_fetcher.py
```

2. The script will:
   - Make an API call to fetch the homework list
   - For each homework item, make an additional API call to get detailed descriptions
   - Generate a CSV report saved as `homework_report.csv`
   - Display progress in your terminal

3. Open `homework_report.csv` in Excel, Google Sheets, or any text editor to view the data

## Output

The generated CSV report includes exactly these columns:
- **teaNameSurname**: Teacher's name
- **lesson**: Subject/course name  
- **startDate**: Assignment start date
- **endDate**: Assignment due date
- **description**: Detailed homework description

## API Calls

The script makes two types of API calls:
1. **getHomeworkList**: Fetches the list of all homework assignments
2. **getHomeworkDetail**: For each homework ID, fetches detailed information including descriptions

## HTML Report Generation

A separate script `csv_to_html.py` is included to generate beautiful HTML reports from your CSV data:

```bash
python3 csv_to_html.py
```

This will create `homework_report.html` with:
- 📊 Progress statistics and completion percentage
- 🎨 Beautiful responsive design with status-based styling
- ✅ Green badges for "Done" assignments
- 🔶 Orange badges for work in progress  
- ⚪ Gray badges for not started assignments
- 📱 Mobile-friendly responsive layout

## Workflow

1. **Fetch new homework:** `python3 homework_fetcher.py`
2. **Update status manually:** Edit the CSV file to mark assignments as "Done"  
3. **Generate HTML report:** `python3 csv_to_html.py`
4. **View in browser:** Open `homework_report.html`

## ☁️ Automated Vercel Deployment

For a fully automated solution with web interface and daily automation:

### 🚀 Features
- **Daily Auto-fetch**: Automatically checks for new homework at 8:00 AM
- **Web Interface**: Edit homework status from any device
- **One-Click Reports**: Generate HTML reports with a button click
- **GitHub Storage**: Persistent data storage in your repository
- **No Server Maintenance**: Fully serverless on Vercel

### 📱 Web Dashboard
- View all homework assignments
- Edit status (Done, In Progress, Pending)
- Generate beautiful HTML reports
- Automated daily homework fetching

### 🔧 Setup
See **[VERCEL_SETUP.md](VERCEL_SETUP.md)** for complete deployment instructions.

Quick setup:
1. Deploy to Vercel from your GitHub repository
2. Set environment variables (GitHub token, repo name, session ID)
3. Access your web dashboard at your Vercel URL

## Files

### Local Scripts
- `homework_fetcher.py` - Fetches homework data and updates CSV
- `csv_to_html.py` - Converts CSV to beautiful HTML report

### Web Application (Vercel)
- `index.html` - Web dashboard interface
- `api/fetch_homework.py` - API endpoint for automated homework fetching
- `api/generate_html.py` - API endpoint for HTML report generation
- `api/csv_data.py` - API endpoint for CSV data management
- `vercel.json` - Vercel deployment configuration with cron jobs

### Data Files
- `homework_report.csv` - Your data with manual status edits
- `homework_report.html` - Generated visual report

### Configuration
- `requirements.txt` - Python dependencies
- `VERCEL_SETUP.md` - Complete deployment guide

## Notes

- The homework fetcher includes all necessary headers and authentication cookies from the original curl requests
- Error handling is included for API failures and malformed responses
- The CSV output preserves your manual status edits between runs
- The HTML generator reads your current CSV data including all manual changes
- Progress is displayed in the terminal as each homework detail is fetched
