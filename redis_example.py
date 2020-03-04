import asyncio
import aioredis
from settings import REDIS_HOST, REDIS_PORT
from gateways.cache_gateway import CacheGateway
channel_1 = 'one'
channel_2 = 'two'


async def sub():
    redis = await CacheGateway.get_poll()

    ch1, = await redis.subscribe(channel_1)

    async def reader(channel):
        async for message in channel.iter():
            print("Got message:", message)

    asyncio.get_running_loop().create_task(reader(ch1))
    await asyncio.sleep(100)


async def main():
    await asyncio.gather(
        sub(),
        loop=asyncio.get_running_loop()
    )

if __name__ == '__main__':
    asyncio.run(main())
