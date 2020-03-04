import logging
from abc import ABC
from asyncio import sleep, get_running_loop
from datetime import datetime
from settings import DATETIME_FORMAT, TIME_SLEEP_PRODUCER, TIME_SLEEP_CONSUMER
from services.action_service import ActionService


class Handler(ABC):
    uid = None
    token = None
    cache = None
    send = None
    channels = None
    subscriptions = []
    logged = None
    task_end = False

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        # self.subscribe_cache_gateway()

    async def subscribe_cache_gateway(self):
        self.channels = [self.uid]
        if self.type == 'client':
            ws_client_uid = self.uid.split(";")[0]
            self.channels.append(ws_client_uid)

        cache_poll = await self.cache.get_poll()

        for channel in self.channels:
            subscription, = await cache_poll.subscribe(channel)
            get_running_loop().create_task(self.reader(subscription))

        print(f"{self.uid} Socket subscribed to the following channels: {self.channels}")

    async def consumer(self, receive):
        """
        Receives messages from the client and process them properly.
        """
        while True:
            try:
                print(f"{self.uid} Socket subscribed to the following channels: {self.channels}")
                message = await receive()
            except Exception as e:
                print(f'{self.uid} consumer unknown error: {e}')
                raise Exception()
            if message.get("type") == "websocket.disconnect":
                print(f"{datetime.now()} closing connection")
                raise Exception()  # notify to close the redis connection
            if message.get("type") == "websocket.connect":
                continue

            action, params = ActionService.received_action(message['text'])
            print(
                f"[{self.uid}] [{self.type}] [{message.get('type')}] "
                f"consumer retrieve message: {action} - {params}"
            )
            await self.on_message(action=action, params=params)
            await sleep(TIME_SLEEP_CONSUMER)

    async def producer(self):
        await self.subscribe_cache_gateway()
        while True:
            if self.task_end:
                break
            await sleep(TIME_SLEEP_PRODUCER)

    async def reader(self, channel):
        async for message in channel.iter():
            try:
                message = message.decode('utf-8')
            except Exception as e:
                print(e)
                raise Exception()

            formatted_message = ActionService.load_message(message)
            print(
                f"[{self.uid}] [{self.type}] "
                f"producer retrieve message from channel {self.uid}: {formatted_message}"
            )
            if 'action' in formatted_message and hasattr(self, formatted_message['action']):
                await self.on_message(**formatted_message)
            else:
                message_to_send = ActionService.action_response(**formatted_message)
                await self.send(message_to_send)

    async def on_message(self, action, params=dict(), **kwargs):
        try:
            await self.received_action(action, params)
        except Exception as e:
            print(f"{self} Client {self.uid} tried to execute non existing action: {action}: {e}")
            response = ActionService.action_response(
                action="{action}_error".format(action=action),
                params="Non existent action", detail=str(e)
            )
            await self.send(response)

    async def received_action(self, action, params):
        action_func = getattr(self, action)
        await action_func(params)

    async def ping(self, params):
        if "to" in params:
            to = params["to"]
            response_cs = ActionService.action_response(
                action='pong_cs',
                params={'from': "ControlServer", "creation_date": datetime.now().strftime(DATETIME_FORMAT)}
            )
            await self.send(response_cs)
            self.cache.publish_message(to, response_cs['text'])
        else:
            response = ActionService.action_response(action='pong_cs', params=self.get_from)
            await self.send(response)

    async def pong(self, params):
        if "to" in params:
            to = params["to"]
            response = ActionService.action_response(action='pong', params=self.get_from)
            self.cache.publish_message(to, response)
        else:
            response = ActionService.action_response(action='pong_error', params={'message': "not a valid response"})
            await self.send(response)

    @property
    def type(self):
        return self.__class__.__name__.lower().replace("handler", '')

    @staticmethod
    def get_disassociate_response():
        """
            Este caso se va a provocar cuando la camera conectado pierda conexion
            pasos:
                LOGIN_START - ok
                Transmision establecida de datos - ok
                Por algun motivo se pierde conexion - FAIL
                todos los attr de self pierden valor - None
                La camara constantemente sigue mandando el live-status / wifi networks - Fail
                La conexion se pierde
                Se le notifica a la camera con un nuevo comando "disassociated"
                La logica pasa a camera (verificar el token y volver al paso LOGIN_START)
        """
        return ActionService.action_response(
            action="disassociated_camera",
            params="DISASSOCIATED_CAMERA",
            detail=str(f"connection lost, please check token with server.")
        )

    @property
    def get_from(self):
        return {"from": self.uid, "creation_date": datetime.now().strftime(DATETIME_FORMAT)}

    async def unsubscribe(self, params):
        for subscription in self.subscriptions:
            subscription.punsubscribe()
            subscription.unsubscribe()
            subscription.close()
        self.channels = []
        self.subscriptions = []
        self.task_end = True
        if self.cache:
            self.cache.close()
