class Webhook:
    def __init__(self, data):
        self.hook = data["webhook"]
        self.channel_id: int = data["channel_id"]
