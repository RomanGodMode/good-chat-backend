from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

external_groups = []


def subscribe_for_dialog(dialog_id: int, channel_name: str):
    group_name = f'dialog-{dialog_id}'
    async_to_sync(get_channel_layer().group_add)(group_name, channel_name)
    external_groups.append(group_name)