#!/usr/bin/env python3
"""
Homework Fetcher Script
Fetches homework data from Bogazici Sehir Koleji API and generates a CSV report
"""

import requests
import json
import csv
from datetime import datetime, timedelta
import sys
import os
import re

class SessionManager:
    def __init__(self):
        self.current_session = None
        self.session_expiry = None
        self.base_url = "https://bogazicisehirkolejiobs.com"

    def login_and_get_session(self):
        """Login using credentials and get authenticated session"""
        try:
            username = os.environ.get('SCHOOL_USERNAME')
            password = os.environ.get('SCHOOL_PASSWORD')
            
            if not username or not password:
                print("⚠️ No login credentials found in environment variables")
                print("💡 Set SCHOOL_USERNAME and SCHOOL_PASSWORD environment variables")
                return None
            
            print(f"🔐 Attempting login for user: {username}")
            
            # First get a basic session from the main page
            session = requests.Session()
            
            # Get initial session
            init_response = session.get(f"{self.base_url}/", timeout=10)
            
            # Prepare login data
            login_url = f"{self.base_url}/require/class/login.php"
            
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9,tr;q=0.8',
                'origin': self.base_url,
                'priority': 'u=1, i',
                'referer': f"{self.base_url}/",
                'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest'
            }
            
            # Prepare multipart form data
            form_data = {
                'request': 'login',
                'loginAs': 'standard',
                'isRegister': '0',
                'password': password,
                'username': username,
                'newUser': '0'
            }
            
            # Make login request
            response = session.post(login_url, headers=headers, data=form_data, timeout=10)
            
            if response.status_code == 200:
                # Check if login was successful
                try:
                    login_result = response.json()
                    if login_result.get('success') == True or login_result.get('status') == 'success':
                        print("✅ Login successful!")
                        
                        # Get the session ID from the session cookies
                        if 'PHPSESSID' in session.cookies:
                            session_id = session.cookies['PHPSESSID']
                            print(f"🔑 Got authenticated session ID: {session_id[:10]}...")
                            
                            # Verify the session works for homework API
                            if self.test_session_validity(session_id):
                                print("✅ Authenticated session is valid for homework API!")
                                self.current_session = session_id
                                self.session_expiry = datetime.now() + timedelta(hours=4)  # Longer expiry for authenticated sessions
                                return session_id
                            else:
                                print("⚠️ Authenticated session not valid for homework API")
                        else:
                            print("⚠️ No session ID found after login")
                    else:
                        print(f"❌ Login failed: {login_result}")
                        return None
                        
                except json.JSONDecodeError:
                    print("⚠️ Invalid JSON response from login API")
                    print(f"Response: {response.text}")
                    return None
            else:
                print(f"❌ Login request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return None

    def get_fresh_session(self):
        """Get a fresh session ID, trying login first, then fallback methods"""
        try:
            # First, try to use any existing environment session ID
            env_session = os.environ.get('PHPSESSID')
            if env_session:
                print(f"🔑 Trying environment session ID: {env_session[:10]}...")
                if self.test_session_validity(env_session):
                    print(f"✅ Environment session ID is valid!")
                    self.current_session = env_session
                    self.session_expiry = datetime.now() + timedelta(hours=2)
                    return env_session
                else:
                    print("⚠️ Environment session ID is invalid")
            
            # Try to login and get authenticated session
            session_id = self.login_and_get_session()
            if session_id:
                return session_id
            
            print("🔄 Login method failed, trying fallback methods...")
            
            # Fallback: try to get session from public pages
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
                'Connection': 'keep-alive',
            }
            
            endpoints_to_try = [
                f"{self.base_url}/",
                f"{self.base_url}/login",
                f"{self.base_url}/index.php"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10, allow_redirects=True)
                    if 'PHPSESSID' in response.cookies:
                        session_id = response.cookies['PHPSESSID']
                        print(f"🔍 Got session ID from {endpoint}: {session_id[:10]}...")
                        
                        # Test if this session actually works for the homework API
                        if self.test_session_validity(session_id):
                            print(f"✅ Valid session ID obtained!")
                            self.current_session = session_id
                            self.session_expiry = datetime.now() + timedelta(hours=2)
                            return session_id
                        else:
                            print(f"⚠️ Session ID from {endpoint} is not valid for homework API")
                            
                except Exception as e:
                    print(f"⚠️ Failed to get session from {endpoint}: {e}")
                    continue
            
            print("❌ Could not obtain valid session ID using any method")
            print("💡 Solutions:")
            print("   1. Set SCHOOL_USERNAME and SCHOOL_PASSWORD environment variables for automatic login")
            print("   2. Set PHPSESSID environment variable with a valid session from your browser")
            return None
            
        except Exception as e:
            print(f"❌ Error getting fresh session: {e}")
            return None
    
    def test_session_validity(self, session_id):
        """Test if a session ID is valid by making a test API call"""
        try:
            test_url = "https://bogazicisehirkolejiobs.com/obsapi/homework/getHomeworkList?[object%20FormData]&_=1758909470368"
            
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
            
            cookies = {'PHPSESSID': session_id}
            response = requests.get(test_url, headers=headers, cookies=cookies, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Check if the response indicates login is required
                    if isinstance(data, dict):
                        if data.get('success') == False and 'login' in str(data.get('error', '')).lower():
                            return False
                        if 'data' in data or 'success' in data:
                            return True
                    elif isinstance(data, list):
                        return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error testing session validity: {e}")
            return False

    def get_valid_session(self):
        """Get a valid session ID, refreshing if necessary"""
        if (self.current_session and 
            self.session_expiry and 
            datetime.now() < self.session_expiry):
            return self.current_session
        
        print("🔄 Getting fresh session...")
        return self.get_fresh_session()

    def make_api_request(self, url, max_retries=2):
        """Make API request with automatic session refresh on failure"""
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
        
        for attempt in range(max_retries + 1):
            try:
                session_id = self.get_valid_session()
                if not session_id:
                    return None
                
                cookies = {'PHPSESSID': session_id}
                response = requests.get(url, headers=headers, cookies=cookies, timeout=30)
                
                if response.status_code in [401, 403]:
                    print(f"🔒 Session invalid (HTTP {response.status_code}), attempting refresh...")
                    self.current_session = None
                    continue
                
                try:
                    response.json()  # Validate JSON
                    response.raise_for_status()
                    return response
                except json.JSONDecodeError:
                    if attempt < max_retries:
                        print("⚠️ Invalid JSON response, attempting refresh...")
                        self.current_session = None
                        continue
                    else:
                        return None
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    print(f"⚠️ Request failed (attempt {attempt + 1}), retrying: {e}")
                    self.current_session = None
                else:
                    print(f"❌ Request failed after {max_retries + 1} attempts: {e}")
                    return None
        
        return None

# Global session manager
session_manager = SessionManager()

def fetch_homework_data():
    """Make API call to fetch homework data using session manager"""
    url = "https://bogazicisehirkolejiobs.com/obsapi/homework/getHomeworkList?[object%20FormData]&_=1758909470368"
    
    response = session_manager.make_api_request(url)
    if response:
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Warning: Response is not valid JSON. Raw response:")
            print(response.text)
            return {"raw_response": response.text}
    return None

def fetch_homework_detail(homework_id):
    """Make API call to fetch homework detail data for a specific ID using session manager"""
    url = f"https://bogazicisehirkolejiobs.com/obsapi/homework/getHomeworkDetail?id={homework_id}&[object%20FormData]&_=1758909470369"
    
    response = session_manager.make_api_request(url)
    if response:
        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"Warning: Detail response for ID {homework_id} is not valid JSON")
            return None
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
