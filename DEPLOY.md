# AI Investor Platform - Deployment Guide

## Deploy to Render (Free Tier)

### Prerequisites
- GitHub account
- Git installed

### Step 1: Push to GitHub

```bash
cd /root/.openclaw/workspace/ai-investor
git init
git add .
git commit -m "Add auth layer"
```

Create a new repository on GitHub and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-investor.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub and select the repository
4. Configure:

| Setting | Value |
|---------|-------|
| Name | ai-investor |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python3 app.py` |

5. Add Environment Variables:

| Key | Value |
|-----|-------|
| `AUTH_USERNAME` | (choose a username) |
| `AUTH_PASSWORD` | (choose a strong password) |

6. Click "Create Web Service"

### Step 3: Access Your App

Once deployed, visit:
```
https://ai-investor-xxxx.onrender.com
```

You'll be prompted for Basic Auth — use the credentials you set.

### Security Notes

- **Change the default password!** Default is `change-me-in-production`
- Credentials are set in Render dashboard under "Environment Variables"
- No financial advice is given — platform shows signals only
- User assumes all risk

---

## Local Development

```bash
# Set credentials
export AUTH_USERNAME=admin
export AUTH_PASSWORD=your-secret-password

# Run locally
cd ai-investor
pip install -r requirements.txt
python3 app.py
```

Visit http://localhost:5000