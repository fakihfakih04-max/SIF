from workers import WorkerEntrypoint, Response


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = request.url

        if url.endswith("/health"):
            return Response.json({
                "status": "ok",
                "service": "SIF Mobile & Computer"
            })

        if url.endswith("/api/online-status"):
            return Response.json({
                "online": True,
                "database": "D1",
                "status": "connected"
            })

        return await self.env.ASSETS.fetch(request)
