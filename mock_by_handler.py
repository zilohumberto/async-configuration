from gateways.cache_gateway import CacheGateway


async def send_camera(text):
    print(f"message received by camera {text}")


async def send_device(text):
    print(f"message received by device {text}")


def client():
    yield {"uid": "wsclient-1;u1", "cache": CacheGateway(), "send": send_camera, "logged": True}
    yield {"uid": "wsclient-1;u1", "cache": CacheGateway(), "send": send_camera, "logged": True}
    yield {"uid": "wsclient-3;u3", "cache": CacheGateway(), "send": send_camera, "logged": True}


def device():
    yield {"uid": "android", "cache": CacheGateway(), "send": send_device, "logged": True}
    yield {"uid": "ios", "cache": CacheGateway(), "send": send_device, "logged": True}
    yield {"uid": "camera", "cache": CacheGateway(), "send": send_device, "logged": True}
