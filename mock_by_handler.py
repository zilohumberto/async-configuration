from gateways.cache_gateway import CacheGateway


async def send_camera(text):
    print(f"message received by camera {text}")


async def send_device(text):
    print(f"message received by device {text}")


def client():
    yield {"uid": "wsclient-1;u1", "send": send_camera, "logged": True}
    yield {"uid": "wsclient-1;u1", "send": send_camera, "logged": True}
    yield {"uid": "wsclient-3;u3", "send": send_camera, "logged": True}


def device():
    yield {"uid": "android", "send": send_device, "logged": True}
    yield {"uid": "ios", "send": send_device, "logged": True}
    yield {"uid": "camera", "send": send_device, "logged": True}
