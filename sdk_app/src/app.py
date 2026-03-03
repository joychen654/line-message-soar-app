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
from soar_sdk.exceptions import ActionFailure

import requests
from typing import Any

## Constants
_INFO_EP                  = "/info"
_PUSH_EP                  = "/message/push"
_MULTICAST_EP             = "/message/multicast"
_BROADCAST_EP             = "/message/broadcast"
_REPLY_EP                 = "/message/reply"
_QUOTA_EP                 = "/message/quota"
_PROFILE_EP               = "/profile/{userId}"
_GROUP_MEMBER_PROFILE_EP  = "/group/{groupId}/member/{userId}"

logger = getLogger()

class Asset(BaseAsset):
    channel_access_token: str = AssetField(
        required=True,
        sensitive=True,
        description="channel access token", 
        alias="channel access token",
    )
    # key_header: str = AssetField(
    #     default="Authorization",
    #     value_list=["Authorization", "X-API-Key"],
    #     description="Header for API key authentication",
    # )

app = App(
    name="Line_Message",
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

# ---------------------------------------------------------------------------
# LineAPIClient - general purpose client for calling LINE Messaging API
# ---------------------------------------------------------------------------

class LineAPIClient:
    """
    Usage:
        client = LineAPIClient(asset)
        r = client.get("/info")
        r = client.post("/message/push", {"to": uid, "messages": [...]})
    """

    def __init__(self, asset: Asset) -> None:
        self.base_url = "https://api.line.me/v2/bot"
        self._token = asset.channel_access_token
        # default time out set to 5 on requests package level
        self._timeout = 5
        self._base_headers: dict[str, str] = {
            "Authorization": f"Bearer {asset.channel_access_token}"
        }

    def request(
        self, 
        method: str, 
        endpoint: str, 
        *, 
        content_type: bool = True,
        extra_headers: dict[str, str] | None = None, 
        **kwargs: Any
    ) -> requests.Response:
        """
        Args:
            method: HTTP method (e.g. "GET", "POST")
            endpoint: Relative path after /v2/bot (e.g. "/info", "/message/push")
            content_type: Whether to set Content-Type: application/json (default: True)
            extra_headers: Additional headers to include (can override Authorization)
            **kwargs: Additional arguments to pass to requests
        """

        url = self.base_url + endpoint
        headers: dict[str, str] = {
            **self._base_headers,
            **({"Content-Type": "application/json"} if content_type else {}),
            **(extra_headers or {}),
        }

        logger.debug("-> %s %s", method, url)
        
        response = getattr(requests, method.lower())(
            url,
            headers=headers,
            timeout=self._timeout,
            **kwargs,
        )
        logger.debug("HTTP %s", response.status_code)

        return response
    
    @staticmethod
    def check_response(response: requests.Response, action: str = "LINE API") -> None:
        """
            Raise a ActionFailure with detailed message on non-2xx response.
            200/204 are considered success; others are treated as errors.
        """
        if not response.ok:
            logger.error(
                "%s failed [HTTP %s]: %s",
                action, response.status_code, response.text,
            )
            raise ActionFailure(
                f"{action} failed "
                f"[HTTP {response.status_code}]: {response.text}"
            )


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

# test connectivity
@app.test_connectivity()
def test_connectivity(soar: SOARClient, asset: Asset) -> None:
    """ Validate the Channel Access Token by calling GET /info. """
    logger.progress("Connecting to LINE Messaging API...")
    client = LineAPIClient(asset)
    r = client.request("GET", "/info", content_type=False)
    LineAPIClient.check_response(r, "Test Connectivity")
    logger.progress("Test Connectivity Passed")

# push message
class PushMessageParams(Params):
    input: str = Param(
        description="Text content of the message to send",
        default="",
        required=True,
    )
    to: str = Param(
        description="LINE user ID, group ID, or room ID to send the message to", 
        default="",
        required=True,
    )

# ------ below action haven't modified yet ------
@app.action(
    description="Sends a message to a user, group chat, or multi-person chat at any time.",
    action_type="generic",
    read_only=False,
)
def push_message(
    params: PushMessageParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    logger.progress("Sending push message...")
    client = LineAPIClient(asset)
    r = client.request("POST", "/message/push", json={
        "to": params.to,
        "messages": [{"type": "text", "text": params.input}],
    })
    LineAPIClient.check_response(r, "Push Message")

    return ActionOutput()


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
