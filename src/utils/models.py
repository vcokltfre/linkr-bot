class Webhook:
    def __init__(self, data):
        self.hook = data["webhook"]
        self.channel_id: int = data["channel_id"]


class DiscordChannel:
    def __init__(self, data):
        self.id: int = data["id"]
        self.guild_id: int = data["guild_id"]
        self.adder: int = data["adder"]
        self.linkr_channel: str = data["linkr_channel"]


class LinkrChannel:
    def __init__(self, data):
        self.name: str = data["channel_name"]
        self.owner_id: str = data["owner_id"]
        self.data: str = data["extra_data"]
