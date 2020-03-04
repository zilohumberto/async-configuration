import pickle
import json


class ActionService:

    @staticmethod
    def message_to_publish(**kwargs):
        return pickle.dumps(kwargs)

    @classmethod
    def load_message(cls, message):
        is_json = not (type(message) == bytes)
        if is_json:
            formatted_message = json.loads(message)
        else:
            try:
                formatted_message = pickle.loads(message)
            except pickle.UnpicklingError:
                formatted_message = json.loads(message.decode('utf-8'))
        return formatted_message

    @staticmethod
    def action_response(*args, **kwargs):
        if args:
            return dict(type="websocket.send", text=json.dumps(args))
        if kwargs:
            return dict(type="websocket.send", text=json.dumps(kwargs))

    @classmethod
    def received_action(cls, message):
        message_formatted = json.loads(message)
        if "params" not in message_formatted and not message_formatted["params"]:
            message_formatted["params"] = {}
        return message_formatted['action'], message_formatted['params']
