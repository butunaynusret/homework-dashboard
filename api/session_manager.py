import requests
import re
import os
from datetime import datetime, timedelta
import json

class SessionManager:
    def __init__(self):
        self.current_session = None
        self.session_expiry = None
        self.base_url = "https://bogazicisehirkolejiobs.com"
        
        # Try to get initial session from environment
        env_session = os.environ.get('PHPSESSID')
        if env_session:
            self.current_session = env_session
            # Set expiry to 1 hour from now as a default
            self.session_expiry = datetime.now() + timedelta(hours=1)

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
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Try different endpoints to get a session
            endpoints_to_try = [
                f"{self.base_url}/",
                f"{self.base_url}/login",
                f"{self.base_url}/index.php"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10, allow_redirects=True)
                    
                    # Check if we got a PHPSESSID in the response cookies
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
        
        # Check if current session exists and is not expired
        if (self.current_session and 
            self.session_expiry and 
            datetime.now() < self.session_expiry):
            return self.current_session
        
        # Session is expired or doesn't exist, get a fresh one
        print("🔄 Session expired or missing, getting fresh session...")
        return self.get_fresh_session()

    def make_api_request(self, url, headers=None, cookies=None, timeout=30, max_retries=2):
        """Make API request with automatic session refresh on failure"""
        
        if headers is None:
            headers = {}
        
        if cookies is None:
            cookies = {}
        
        # Base headers for school API
        base_headers = {
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
        
        # Merge with provided headers
        final_headers = {**base_headers, **headers}
        
        for attempt in range(max_retries + 1):
            try:
                # Get valid session
                session_id = self.get_valid_session()
                if not session_id:
                    return None
                
                # Set session cookie
                final_cookies = {**cookies, 'PHPSESSID': session_id}
                
                # Make the request
                response = requests.get(url, headers=final_headers, cookies=final_cookies, timeout=timeout)
                
                # Check for session-related errors
                if response.status_code == 401 or response.status_code == 403:
                    print(f"🔒 Session invalid (HTTP {response.status_code}), attempting refresh...")
                    self.current_session = None  # Force refresh
                    continue
                
                # Check response content for session errors
                try:
                    content = response.text.lower()
                    if any(error in content for error in ['session expired', 'login required', 'authentication failed', 'unauthorized']):
                        print("🔒 Session expired based on response content, attempting refresh...")
                        self.current_session = None  # Force refresh
                        continue
                except:
                    pass
                
                # Check if response is valid JSON (expected for API calls)
                try:
                    response.json()
                except json.JSONDecodeError:
                    if attempt < max_retries:
                        print("⚠️ Invalid JSON response, possibly session issue, attempting refresh...")
                        self.current_session = None  # Force refresh
                        continue
                    else:
                        print("❌ Invalid JSON response after retries")
                        return None
                
                # If we get here, the request was successful
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    print(f"⚠️ Request failed (attempt {attempt + 1}), retrying: {e}")
                    self.current_session = None  # Force refresh on network errors
                else:
                    print(f"❌ Request failed after {max_retries + 1} attempts: {e}")
                    return None
        
        return None

    def get_homework_list(self):
        """Get homework list with automatic session management"""
        url = "https://bogazicisehirkolejiobs.com/obsapi/homework/getHomeworkList?[object%20FormData]&_=1758909470368"
        response = self.make_api_request(url)
        
        if response:
            try:
                return response.json()
            except json.JSONDecodeError:
                return None
        return None

    def get_homework_detail(self, homework_id):
        """Get homework detail with automatic session management"""
        url = f"https://bogazicisehirkolejiobs.com/obsapi/homework/getHomeworkDetail?id={homework_id}&[object%20FormData]&_=1758909470369"
        response = self.make_api_request(url)
        
        if response:
            try:
                return response.json()
            except json.JSONDecodeError:
                return None
        return None

# Global session manager instance
session_manager = SessionManager()
