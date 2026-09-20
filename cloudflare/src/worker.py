from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from workers import asgi

app = FastAPI(title="SIF Mobile & Computer")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "SIF Mobile & Computer", "mode": "cloudflare-migration"}

@app.get("/api/online-status")
async def online_status(request: Request):
    return {"online": True, "database": "D1 migration pending"}

@app.get("/{path:path}")
async def frontend(path: str, request: Request):
    env = request.scope["env"]
    asset_url = f"https://assets.local/{path or 'index.html'}"
    resp = await env.ASSETS.fetch(asset_url)
    body = await resp.bytes()
    return Response(content=body, status=resp.status, headers=resp.headers)

Default = asgi.entrypoint(app)
