from fastapi import FastAPI, Request
from fastapi.responses import Response
from workers import asgi

app = FastAPI(title="SIF Mobile & Computer")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "SIF Mobile & Computer",
        "mode": "cloudflare-migration",
    }


@app.get("/api/online-status")
async def online_status(request: Request):
    return {
        "online": True,
        "database": "D1",
        "status": "connected",
    }


@app.get("/{path:path}")
async def frontend(path: str, request: Request):
    env = request.scope["env"]

    path = path or "index.html"

    asset_url = f"https://assets.local/{path}"
    response = await env.ASSETS.fetch(asset_url)

    body = await response.bytes()

    return Response(
        content=body,
        status=response.status,
        headers=dict(response.headers),
    )


Default = asgi.entrypoint(app)
