from asyncio import gather, get_running_loop, run
from handlers.device_handler import DeviceHandler
from handlers.client_handler import ClientHandler
import mock_by_handler


def pickup_handler(parameter):
    handlers = {
        'client': ClientHandler,
        'device': DeviceHandler,
    }
    kwargs_handler = {
        'client': mock_by_handler.client(),
        'device': mock_by_handler.device(),
    }
    kwargs = next(kwargs_handler.get(parameter))
    return handlers.get(parameter)(
        **kwargs
    )


async def main():
    instances = []
    for user in ['client', 'device', 'client', 'device', 'device']:
        instances.append(pickup_handler(user).producer())
    await gather(
        *instances,
        loop=get_running_loop()
    )


if __name__ == '__main__':
    run(main())
