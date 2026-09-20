# SIF Mobile & Computer — Online Web Deployment

This project is prepared for a Render Web Service.

## Important data note
The app currently uses SQLite. For online production, the included Render configuration places the SQLite database on a persistent disk at `/var/data/sif_mobile.db` so data survives service restarts/deploys. This requires a Render plan that supports persistent disks.

## Deploy
1. Put this project in a GitHub repository.
2. In Render, create a **Web Service** from that repository.
3. Render can read `render.yaml`, or enter:
   - Build: `pip install -r backend/requirements.txt`
   - Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Health check: `/health`
4. Add the persistent disk at `/var/data` if it was not created from the Blueprint.
5. Open the generated `onrender.com` URL.

## First login
Username: `admin`
Password: `admin`

Change the admin password after the first login when password management is added.

## Local version
`START_SIF.bat` remains unchanged for Windows/offline use.
