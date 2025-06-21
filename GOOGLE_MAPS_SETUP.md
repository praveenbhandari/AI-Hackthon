# Google Maps API Setup Guide

This guide will help you set up Google Maps API integration for the Safe Route Finder.

## 🗺️ Prerequisites

1. **Google Account**: You need a Google account
2. **Google Cloud Project**: You'll create a new project or use an existing one
3. **Billing Enabled**: Google Maps API requires billing to be enabled (you get $200 free credit monthly)

## 📋 Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "Safe Route Finder")
4. Click "Create"

### 2. Enable Billing

1. In the Google Cloud Console, go to "Billing"
2. Click "Link a billing account"
3. Create a new billing account or link an existing one
4. **Note**: You get $200 free credit monthly, which is more than enough for testing

### 3. Enable Required APIs

1. Go to "APIs & Services" → "Library"
2. Search for and enable these APIs:
   - **Directions API** (required for routing)
   - **Maps JavaScript API** (optional, for enhanced maps)

### 4. Create API Key

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Copy the generated API key

### 5. Restrict API Key (Recommended)

1. Click on your API key to edit it
2. Under "Application restrictions", select "HTTP referrers"
3. Add your domain (e.g., `localhost:5000/*` for development)
4. Under "API restrictions", select "Restrict key"
5. Select only the APIs you enabled (Directions API)
6. Click "Save"

### 6. Set Environment Variable

#### On macOS/Linux:
```bash
export GOOGLE_MAPS_API_KEY='your_api_key_here'
```

#### On Windows:
```cmd
set GOOGLE_MAPS_API_KEY=your_api_key_here
```

#### For permanent setup, add to your shell profile:
```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile
echo 'export GOOGLE_MAPS_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

## 🚀 Testing the Setup

1. **Start the application**:
   ```bash
   python web_interface.py
   ```

2. **Open the web interface** at `http://localhost:5000`

3. **Check Google Maps availability**:
   - The checkbox should be enabled
   - No warning message should appear

4. **Test Google Maps routing**:
   - Check the "Use Google Maps Directions" checkbox
   - Enter coordinates and find a route
   - You should see real Google Maps directions with safety overlay

## 💰 Cost Information

- **Free Tier**: $200 monthly credit
- **Directions API**: ~$5 per 1000 requests
- **Typical Usage**: 1 route = 1 request
- **Monthly Cost**: Usually $0-5 for personal use

## 🔧 Troubleshooting

### "API key not found" error
- Make sure you set the environment variable correctly
- Restart your terminal/command prompt after setting the variable
- Check that the variable name is exactly `GOOGLE_MAPS_API_KEY`

### "API not enabled" error
- Go to Google Cloud Console → APIs & Services → Library
- Make sure "Directions API" is enabled
- Wait a few minutes for changes to take effect

### "Billing not enabled" error
- Go to Google Cloud Console → Billing
- Link a billing account to your project
- Even with billing enabled, you get $200 free credit

### "Quota exceeded" error
- Check your usage in Google Cloud Console → APIs & Services → Dashboard
- You may need to wait for quota reset or upgrade your plan

## 🔒 Security Best Practices

1. **Restrict API Key**: Always restrict your API key to specific domains/IPs
2. **Monitor Usage**: Check your usage regularly in Google Cloud Console
3. **Rotate Keys**: Consider rotating API keys periodically
4. **Server-Side Only**: Never expose API keys in client-side code

## 📱 Alternative: No API Key

If you don't want to set up Google Maps API:
- The application will work with custom routing only
- You'll still get safety analysis and route visualization
- The "Use Google Maps Directions" checkbox will be disabled

## 🆘 Support

If you encounter issues:
1. Check the Google Cloud Console for error messages
2. Verify your API key is correct
3. Ensure billing is enabled
4. Check that the Directions API is enabled
5. Wait a few minutes for changes to take effect 