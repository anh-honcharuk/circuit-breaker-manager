import json

from app.core.redis import redis_client


class HealthCache:
    TTL = 10

    async def get(self, service_id: int) -> dict | None:
        data = await redis_client.get(
            f"health:{service_id}"
        )

        if data is None:
            return None

        return json.loads(data)

    async def set(
        self,
        service_id: int,
        data: dict,
    ) -> None:
        await redis_client.set(
            f"health:{service_id}",
            json.dumps(data),
            ex=self.TTL,
        )

    async def delete(
        self,
        service_id: int,
    ) -> None:
        await redis_client.delete(
            f"health:{service_id}"
        )