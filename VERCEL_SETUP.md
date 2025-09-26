# Vercel Deployment Setup Guide

This guide will help you deploy your homework automation system to Vercel with automated daily fetching and a web interface for manual status updates.

## 🚀 Architecture Overview

- **GitHub Repository**: Stores your CSV and HTML files persistently
- **Vercel App**: Hosts the web interface and API endpoints  
- **Cron Jobs**: Automatically fetch homework daily at 8:00 AM
- **Web Interface**: Edit homework status and generate HTML reports manually

## 📋 Prerequisites

1. GitHub account with your homework repository
2. Vercel account (free tier is sufficient)
3. GitHub Personal Access Token with repository permissions

## 🔧 Setup Steps

### Step 1: Prepare GitHub Repository

1. **Push your code to GitHub** (you've likely already done this)
2. **Create a GitHub Personal Access Token**:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate new token (classic)
   - Select scopes: `repo` (Full control of private repositories)
   - Copy the token - you'll need it later

### Step 2: Deploy to Vercel

1. **Connect Repository**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Environment Variables**:
   - In Vercel project settings, go to "Environment Variables"
   - Add these required variables:
     ```
     GITHUB_TOKEN = your_github_personal_access_token
     GITHUB_REPO = your_username/your_repo_name
     ```
   - **Recommended**: Add your school login credentials for automatic authentication:
     ```
     SCHOOL_USERNAME = your_school_username
     SCHOOL_PASSWORD = your_school_password
     ```
   - **Optional**: Add a manual session ID as fallback:
     ```
     PHPSESSID = your_valid_session_id_from_browser
     ```
   - **Note**: With login credentials, the system will automatically authenticate and get fresh sessions!

3. **Deploy**:
   - Vercel will automatically deploy your app
   - The deployment will include:
     - Web interface at your Vercel URL
     - API endpoints at `/api/*`
     - Cron job that runs daily at 8:00 AM

### Step 3: Authentication Configuration

**Option A: Automatic Login (Recommended)**

1. **Get Your School Credentials**:
   - Use the same username and password you use to log into the school system
   - Usually your student ID number and password

2. **Add to Vercel Environment Variables**:
   ```
   SCHOOL_USERNAME = your_student_id_or_username
   SCHOOL_PASSWORD = your_school_password
   ```

3. **Benefits**:
   - Fully automated - no manual session management
   - System automatically logs in and gets fresh sessions
   - Much more reliable than manual session IDs

**Option B: Manual Session ID (Fallback)**

1. **Login to School System**:
   - Go to https://bogazicisehirkolejiobs.com
   - Log in with your credentials
   - Navigate to the homework section

2. **Get Session ID from Browser**:
   - Open Developer Tools (F12 or right-click → Inspect)
   - Go to "Application" or "Storage" tab
   - Find "Cookies" for bogazicisehirkolejiobs.com
   - Copy the `PHPSESSID` value

3. **Add to Vercel**:
   - Add/update the `PHPSESSID` environment variable

### Step 4: Automatic Session Management

The system includes intelligent 3-tier session management:

**Priority Order:**
1. **Environment PHPSESSID** - Uses if provided and valid ✅
2. **Automatic Login** - Authenticates with credentials and gets fresh session 🔐
3. **Fallback Methods** - Tries to get sessions from public pages 🔄

**Smart Features:**
- **Login Authentication**: Uses your credentials to get authenticated sessions
- **Session Validation**: Tests all sessions before using them
- **Automatic Retry**: Failed requests retry with fresh sessions
- **Longer Session Life**: Authenticated sessions last 4 hours vs 2 hours for manual ones
- **Multiple Fallbacks**: Never fails if any method works

## 🌐 Usage

### Automated Daily Fetching
- Runs automatically every day at 8:00 AM
- Checks for new homework assignments
- Adds new items to your CSV file in GitHub
- Preserves your existing status updates

### Manual Operations
1. **Access Web Interface**: Visit your Vercel app URL
2. **Fetch Homework**: Click "Fetch Homework" to manually check for new assignments
3. **Edit Status**: Click "Edit Status" to view and update homework completion status
4. **Generate Report**: Click "Generate Report" to create and publish HTML report

## 📁 File Structure in Repository

```
your-repo/
├── index.html              # Web interface
├── api/
│   ├── fetch_homework.py    # Daily homework fetching
│   ├── generate_html.py     # HTML report generation
│   └── csv_data.py          # CSV data management
├── homework_report.csv      # Your homework data (auto-updated)
├── homework_report.html     # Generated reports (auto-updated)
├── vercel.json             # Vercel configuration
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

## 🔄 Workflow

### Daily Automated Process:
1. **8:00 AM**: Vercel cron job runs
2. **API Call**: Fetches new homework from school system
3. **CSV Update**: Adds new assignments to GitHub repository
4. **Preservation**: Keeps your existing status updates intact

### Manual Process:
1. **Visit Dashboard**: Open your Vercel app URL
2. **Edit Status**: Mark assignments as "Done", "In Progress", etc.
3. **Generate Report**: Create beautiful HTML report
4. **View/Share**: Access the generated report from GitHub

## 🛠️ Troubleshooting

### Cron Job Not Working
- Check Vercel function logs in dashboard
- Verify environment variables are set correctly
- Ensure GitHub token has proper permissions

### Session Issues
- Session management is now automatic
- Check function logs if homework fetching fails
- System will automatically retry with fresh sessions

### GitHub API Errors
- Check GitHub token permissions
- Verify repository name format: `username/repo-name`
- Ensure token has `repo` scope

### CSV Not Updating
- Check if GitHub repository is accessible
- Verify file permissions in repository
- Check API endpoint logs in Vercel

## 🔒 Security Notes

- Keep your GitHub token secure and never share it
- Use environment variables for all sensitive data
- Consider using GitHub fine-grained tokens for better security
- Regularly rotate your access tokens

## 📊 Monitoring

- **Vercel Dashboard**: Monitor function executions and logs
- **GitHub Repository**: See commit history for automated updates
- **Web Interface**: Check status messages for operation results

## 🎯 Benefits

- **Fully Automated**: No need to manually run scripts
- **Persistent Storage**: Data stored safely in GitHub
- **Web Interface**: Easy status management from any device
- **Professional Reports**: Beautiful HTML reports generated on demand
- **Version Control**: All changes tracked in Git history

Your homework management system is now fully automated and accessible from anywhere! 🎉
