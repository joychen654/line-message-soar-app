from typing import Union
from collections.abc import Iterator
from zoneinfo import ZoneInfo
from soar_sdk.abstract import SOARClient
from soar_sdk.app import App
from soar_sdk.params import Param, Params, OnPollParams, OnESPollParams
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.asset import BaseAsset, AssetField
from soar_sdk.logging import getLogger
from soar_sdk.models.container import Container
from soar_sdk.models.artifact import Artifact
from soar_sdk.models.finding import Finding
from soar_sdk.models.attachment_input import AttachmentInput

logger = getLogger()


class Asset(BaseAsset):
    channel_access_token: str = AssetField(
        description="channel access token", alias="channel access token"
    )
    timeout: float | None = AssetField(
        description="timeout, default 10", default=10.0, value_list=[]
    )


app = App(
    name="phLine_Message",
    app_type="devops",
    logo="linemessage.png",
    logo_dark="linemessage_dark.png",
    product_vendor="Line",
    product_name="Line Message",
    publisher="Joy Chen",
    appid="f5c0cc2c-fcc3-452a-a6e9-8facb4f9951c",
    fips_compliant=False,
    asset_cls=Asset,
)


@app.test_connectivity()
def test_connectivity(soar: SOARClient, asset: Asset) -> None:
    raise NotImplementedError()


class PushMessageParams(Params):
    input: str = Param(
        description="String message that is going to push to", default=""
    )
    to: str = Param(description="Receiver", default="")


@app.action(
    description="Sends a message to a user, group chat, or multi-person chat at any time.  #",
    action_type="generic",
    read_only=False,
)
def push_message(
    params: PushMessageParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    raise NotImplementedError()


class MulticastMessageParams(Params):
    to: str = Param(
        description="User IDs separate by comma (,)", default="", cef_types=["userID"]
    )
    messages: str = Param(
        description="Message to send.", default="", cef_types=["line message object"]
    )
    notificationdisabled: bool | None = Param(
        description="Default: false", default=False
    )


@app.action(
    description="Send the same message to multiple user IDs",
    action_type="generic",
    read_only=False,
    verbose="Send the same message to multiple user IDs. You can't send messages to group chats or multi-person chats",
)
def multicast_message(
    params: MulticastMessageParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    raise NotImplementedError()


class BroadcastMessageParams(Params):
    messages: str = Param(description="Message to send", default="")
    notificationdisabled: bool | None = Param(
        description="Default: false", default=False
    )


@app.action(
    description="Broadcast all the Bot's subscriber",
    action_type="generic",
    read_only=False,
    verbose="Broadcast all the Bot's subscriber",
)
def broadcast_message(
    params: BroadcastMessageParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    raise NotImplementedError()


class GetProfileParams(Params):
    userid: str = Param(
        description="User ID that is returned in a webhook event object. Do not use the LINE ID found on LINE.",
        default="",
    )


@app.action(
    description="Get the profile information of users",
    action_type="generic",
    read_only=False,
    verbose="You can get the profile information of users who meet one of two conditions:\n1. Users who have added your LINE Official Account as a friend\n2. Users who haven't added your LINE Official Account as a friend but have sent a message to your LINE Official Account (except users who have blocked your LINE Official Account)",
)
def get_profile(
    params: GetProfileParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    raise NotImplementedError()


if __name__ == "__main__":
    app.cli()
