from workers import WorkerEntrypoint


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = request.url

        if url.endswith("/health"):
            return Response(
                '{"status":"ok","service":"SIF Mobile & Computer"}',
                headers={"Content-Type": "application/json"},
            )

        if url.endswith("/api/online-status"):
            return Response(
                '{"online":true,"database":"D1","status":"connected"}',
                headers={"Content-Type": "application/json"},
            )

        return Response(
            "SIF Mobile & Computer - Cloudflare Online",
            headers={"Content-Type": "text/plain"},
        )
