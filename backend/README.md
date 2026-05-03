# DeskTube

A YouTube video downloader — clean frontend on GitHub Pages, yt-dlp backend on Render (free tier).

---

## Project Structure

```
desktube/
├── backend/        ← Deploy to Render
│   ├── app.py
│   ├── requirements.txt
│   ├── Procfile
│   └── render.yaml
└── frontend/       ← Deploy to GitHub Pages
    └── index.html
```

---

## Step 1 — Deploy the backend to Render (free)

1. Create a free account at [render.com](https://render.com) — no credit card needed
2. Push the `backend/` folder to a GitHub repo (can be a separate repo or a subfolder)
3. In Render dashboard → **New → Web Service**
4. Connect your GitHub repo
5. Set these settings:
   - **Runtime**: Python
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app:app`
6. Add this environment variable in Render:
   - Key: `PYTHON_VERSION` / Value: `3.11.0`
7. Click **Deploy**

> ⚠️ Render free tier spins down after 15 minutes of inactivity. First request after sleep takes ~30 seconds to wake up. This is normal.

After deploying, copy your Render URL — it looks like:
`https://desktube-api.onrender.com`

---

## Step 2 — Connect the frontend to your backend

Open `frontend/index.html` and find this line near the bottom:

```js
const API_BASE = 'https://your-desktube-api.onrender.com';
```

Replace it with your actual Render URL.

---

## Step 3 — Deploy the frontend to GitHub Pages

1. Push `frontend/index.html` to a GitHub repo (can be the same repo)
2. Go to repo **Settings → Pages**
3. Source: **Deploy from a branch** → `main` → `/frontend` (or root if index.html is at root)
4. GitHub will give you a URL like `https://yourusername.github.io/desktube`

---

## Step 4 — Connect your custom domain

### On GitHub Pages:
- Go to repo **Settings → Pages → Custom domain**
- Enter your domain e.g. `desktube.yourdomain.com`

### On your domain registrar (DNS):
Add a CNAME record:
```
Type:  CNAME
Name:  desktube   (or @ for root domain)
Value: yourusername.github.io
```

GitHub Pages will auto-provision an SSL certificate within a few minutes.

---

## ffmpeg note

ffmpeg is required for merging video+audio streams and mp3 conversion.
Render's free tier includes ffmpeg — no extra setup needed.

---

## Keep yt-dlp updated

YouTube changes frequently. If downloads stop working, update yt-dlp:

In your backend `requirements.txt`, change:
```
yt-dlp==2024.11.18
```
to:
```
yt-dlp  (no pin, always latest)
```

Then redeploy on Render.
