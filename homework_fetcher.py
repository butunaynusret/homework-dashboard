#!/usr/bin/env python3
"""
Homework Fetcher Script
Fetches homework data from Bogazici Sehir Koleji API and generates a CSV report
"""

import requests
import json
import csv
from datetime import datetime
import sys

def fetch_homework_data():
    """Make API call to fetch homework data"""
    
    url = "https://bogazicisehirkolejiobs.com/obsapi/homework/getHomeworkList?[object%20FormData]&_=1758909470368"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,tr;q=0.8',
        'priority': 'u=1, i',
        'referer': 'https://bogazicisehirkolejiobs.com/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    cookies = {
        'PHPSESSID': 'kfvqm9f7b4mck7iejuu7u6a4e2'
    }
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=30)
        response.raise_for_status()
        
        # Try to parse as JSON
        try:
            data = response.json()
            return data
        except json.JSONDecodeError:
            print("Warning: Response is not valid JSON. Raw response:")
            print(response.text)
            return {"raw_response": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None

def fetch_homework_detail(homework_id):
    """Make API call to fetch homework detail data for a specific ID"""
    
    url = f"https://bogazicisehirkolejiobs.com/obsapi/homework/getHomeworkDetail?id={homework_id}&[object%20FormData]&_=1758909470369"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,tr;q=0.8',
        'priority': 'u=1, i',
        'referer': 'https://bogazicisehirkolejiobs.com/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    cookies = {
        'PHPSESSID': 'kfvqm9f7b4mck7iejuu7u6a4e2'
    }
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=30)
        response.raise_for_status()
        
        # Try to parse as JSON
        try:
            data = response.json()
            return data
        except json.JSONDecodeError:
            print(f"Warning: Detail response for ID {homework_id} is not valid JSON")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making detail API request for ID {homework_id}: {e}")
        return None

def read_existing_csv(csv_file_path):
    """Read existing CSV file and return set of existing homework IDs"""
    existing_ids = set()
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'id' in row and row['id']:
                    existing_ids.add(str(row['id']))
        
        print(f"📋 Found {len(existing_ids)} existing homework records in CSV")
        return existing_ids
        
    except FileNotFoundError:
        print("📝 No existing CSV file found - will create new one")
        return set()
    except Exception as e:
        print(f"⚠️ Error reading existing CSV: {e}")
        return set()

def append_new_records_to_csv(csv_file_path, new_homework_data):
    """Append new homework records to existing CSV file"""
    
    # Define the columns in the correct order (matching user's CSV structure)
    columns = ['id', 'status', 'teaNameSurname', 'lesson', 'startDate', 'endDate', 'description']
    
    # Check if file exists and has headers
    file_exists = False
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line:
                file_exists = True
    except FileNotFoundError:
        pass
    
    # If file doesn't exist, create it with headers
    if not file_exists:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
        print("📝 Created new CSV file with headers")
        
    # Ensure file ends with proper newline before appending
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if content exists and doesn't end with newline
        if content and not content.endswith('\n'):
            with open(csv_file_path, 'a', encoding='utf-8') as f:
                f.write('\n')
    except Exception as e:
        print(f"⚠️ Warning: Could not check/fix file ending: {e}")
    
    # Append new records
    new_records_added = 0
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        for item in new_homework_data:
            row = []
            for column in columns:
                if column == 'status':
                    # Leave status empty for user to fill manually
                    row.append('')
                elif column == 'description':
                    # Description comes from the detail API call
                    row.append(item.get('description', ''))
                else:
                    # Other columns come from the main homework data
                    row.append(item.get(column, ''))
            
            writer.writerow(row)
            new_records_added += 1
    
    return new_records_added

def main():
    """Main function to run the homework fetcher"""
    print("🚀 Starting homework data fetch...")
    
    # Define output file path
    output_file = "/Users/nusretbutunay/Desktop/personal/homework_report.csv"
    
    # Read existing CSV to see what homework IDs we already have
    existing_ids = read_existing_csv(output_file)
    
    # Fetch homework list from API
    homework_list_data = fetch_homework_data()
    
    if homework_list_data is None:
        print("❌ Failed to fetch homework list")
        return 1
    
    # Extract homework items from the response
    homework_items = []
    if isinstance(homework_list_data, dict):
        if 'data' in homework_list_data:
            homework_items = homework_list_data['data']
        elif 'homework' in homework_list_data or 'homeworks' in homework_list_data:
            homework_items = homework_list_data.get('homework', homework_list_data.get('homeworks', []))
        else:
            print("⚠️ Unexpected data format from homework list API")
            print(json.dumps(homework_list_data, indent=2, ensure_ascii=False))
            return 1
    elif isinstance(homework_list_data, list):
        homework_items = homework_list_data
    else:
        print("⚠️ Unexpected data format from homework list API")
        return 1
    
    if not homework_items:
        print("📭 No homework items found from API")
        return 0
    
    # Filter out homework items that already exist in CSV
    new_homework_items = []
    for item in homework_items:
        homework_id = str(item.get('id', ''))
        if homework_id and homework_id not in existing_ids:
            new_homework_items.append(item)
    
    print(f"📚 Found {len(homework_items)} total homework items from API")
    print(f"🆕 Found {len(new_homework_items)} new homework items to process")
    
    if not new_homework_items:
        print("✅ No new homework items to add - CSV is up to date!")
        return 0
    
    # Fetch details for NEW homework items only
    new_homework_data_with_details = []
    for i, item in enumerate(new_homework_items):
        homework_id = item.get('id')
        if homework_id:
            print(f"📖 Fetching details for new homework {homework_id} ({i+1}/{len(new_homework_items)})")
            detail_data = fetch_homework_detail(homework_id)
            
            # Combine main data with detail data
            combined_item = item.copy()  # Start with the main homework item
            
            if detail_data and isinstance(detail_data, dict):
                # Extract description from detail data
                if 'data' in detail_data and isinstance(detail_data['data'], dict):
                    description = detail_data['data'].get('description', '')
                elif 'description' in detail_data:
                    description = detail_data['description']
                else:
                    description = ''
                
                combined_item['description'] = description
            else:
                combined_item['description'] = ''
            
            new_homework_data_with_details.append(combined_item)
        else:
            print(f"⚠️ Homework item missing ID: {item}")
            # Still add it but without description
            item_copy = item.copy()
            item_copy['description'] = ''
            new_homework_data_with_details.append(item_copy)
    
    # Sort new records by due date (descending - most recent due dates first)
    print("🔄 Sorting new records by due date...")
    new_homework_data_with_details.sort(key=lambda x: x.get('endDate', ''), reverse=True)
    
    # Append new records to existing CSV
    print("📄 Appending new records to CSV...")
    try:
        new_records_added = append_new_records_to_csv(output_file, new_homework_data_with_details)
        
        print(f"✅ Successfully updated CSV file: {output_file}")
        print(f"📊 Added {new_records_added} new homework entries")
        print("💾 Your existing data and status values have been preserved!")
        
        if new_records_added > 0:
            print("📝 New records have empty status - you can fill them in manually")
        
    except Exception as e:
        print(f"❌ Error updating CSV file: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
