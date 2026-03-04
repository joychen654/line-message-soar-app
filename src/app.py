from typing import Union
from collections.abc import Iterator
from zoneinfo import ZoneInfo
import httpx
from soar_sdk.abstract import SOARClient
from soar_sdk.app import App
from soar_sdk.auth import StaticTokenAuth
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
_QUOTA_CONSUMPTION_EP     = "/message/quota/consumption"
_PROFILE_EP               = "/profile/{userId}"
_GROUP_MEMBER_PROFILE_EP  = "/group/{groupId}/member/{userId}"

logger = getLogger()

# ---------------------------------------------------------------------------
# Asset
# ---------------------------------------------------------------------------

class Asset(BaseAsset):
    channel_access_token: str = AssetField(
        required=True,
        sensitive=True,
        description="channel access token", 
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
        # default time out set to 5 on requests package level
        self._timeout = 5
        self._auth = StaticTokenAuth(asset.channel_access_token)

    def request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs: Any
    ) -> httpx.Response:
        """
        Args:
            method: HTTP method (e.g. "GET", "POST")
            endpoint: Relative path after /v2/bot (e.g. "/info", "/message/push")
            **kwargs: Additional arguments to pass to requests
        """

        url = self.base_url + endpoint
        logger.debug("-> %s %s", method, url)
        
        with httpx.Client(auth=self._auth, timeout=self._timeout) as client:
            response = getattr(client, method.lower())(
                url,
                **kwargs,
            )
        logger.debug("HTTP %s", response.status_code)

        return response
    
    @staticmethod
    def check_response(response: httpx.Response, action: str = "LINE API") -> None:
        """
            Raise a ActionFailure with detailed message on non-2xx response.
            200/204 are considered success; others are treated as errors.
        """
        if not response.is_success:
            msg = f"{action} failed [HTTP {response.status_code}]: {response.text}"
            logger.error(msg)
            raise ActionFailure(msg)


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

###  Test Connectivity
@app.test_connectivity()
def test_connectivity(soar: SOARClient, asset: Asset) -> None:
    """ Validate the Channel Access Token by calling GET /info. """
    logger.progress("Connecting to LINE Messaging API...")
    client = LineAPIClient(asset)
    r = client.request("GET", _INFO_EP)
    LineAPIClient.check_response(r, "Test Connectivity")
    logger.info("Test Connectivity Passed")

### Push Message
class PushMessageParams(Params):
    message: str = Param(
        description="Text content of the message to send",
        default="",
        required=True,
    )
    to: str = Param(
        description="LINE user ID, group ID, or room ID to send the message to", 
        default="",
        required=True,
    )

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
    r = client.request("POST", _PUSH_EP, json={
        "to": params.to,
        "messages": [{"type": "text", "text": params.message}],
    })
    LineAPIClient.check_response(r, "Push Message")

    return ActionOutput()

### Multicast Message
class MulticastMessageParams(Params):
    tos: str = Param(
        description="Comma-separated LINE user IDs to send the message to", 
        default="",
        required=True,
    )
    message: str = Param(
        description="Text content of the message to send", 
        default="", 
        required=True,
    )
    notificationDisabled: bool | None = Param(
        description="Set to true to suppress push notifications for this message",
        default=False,
    )

@app.action(
    description="Send a message to multiple LINE users at once",
    action_type="generic",
    read_only=False,
    verbose="Send a message to multiple LINE users at once (up to 500 recipients). You can't send messages to group chats or multi-person chats",
)
def multicast_message(
    params: MulticastMessageParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    logger.progress("Sending multicast message...")
    
    recipients = [uid.strip() for uid in params.tos.split(",") if uid.strip()]
    if len(recipients) > 500:
        raise ActionFailure(f"Too many recipients ({len(recipients)}). LINE API maximum is 500.")
    if len(recipients) > 400:
        logger.warning("Recipient count is %d, approaching the LINE API limit of 500.", len(recipients))

    client = LineAPIClient(asset)
    r = client.request("POST", _MULTICAST_EP, json={
        "to": recipients,
        "messages": [{"type": "text", "text": params.message}],
        "notificationDisabled": params.notificationDisabled,
    })
    LineAPIClient.check_response(r, "Multicast Message")
    logger.info("Multicast message sent successfully to %d recipients", len(recipients))

    return ActionOutput()

### Broadcast Message
class BroadcastMessageParams(Params):
    message: str = Param(
        description="Text content of the message to broadcast to all friends",
        default="",
        required=True,
    )
    notificationDisabled: bool = Param(
        description="Set to true to suppress push notifications for this message",
        default=False,
    )

@app.action(
    description="Send a message to all users who have added the bot as a friend.",
    action_type="generic",
    read_only=False,
    verbose="Send a message to all users who have added the bot as a friend.",
)
def broadcast_message(
    params: BroadcastMessageParams, soar: SOARClient, asset: Asset
) -> ActionOutput:
    logger.progress("Broadcasting message...")

    client = LineAPIClient(asset)
    r = client.request("POST", _BROADCAST_EP, json={
        "messages": [{"type": "text", "text": params.message}],
        "notificationDisabled": params.notificationDisabled,
    })
    LineAPIClient.check_response(r, "Broadcast Message")
    logger.info("Broadcast message sent successfully")

    return ActionOutput()

### Get Profile
class GetProfileParams(Params):
    userId: str = Param(
        description="LINE user ID of the user whose profile to retrieve",
        default="",
        required=True,
    )

### Get Profile Output
class UserProfileOutput(ActionOutput):
    userId: str = OutputField(example_values=["Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"])
    displayName: str = OutputField(example_values=["John Doe"])
    pictureUrl: str = OutputField(example_values=["https://profile.line-scdn.net/ch/v2/p/uf9da5ee2b..."])
    statusMessage: str = OutputField(example_values=["Hello, LINE!"])
    language: str = OutputField(example_values=["zh-TW", "en", "ja"])

@app.action(
    description="Get the profile of a LINE user by their user ID.",
    action_type="generic",
    read_only=False,
    verbose="Note that the userId is retrieved from the webhook event rather than the LINE ID typically used for adding friends.\n" \
        "You can get the profile information of users who meet one of two conditions:\n"\
        "1. Users who have added your LINE Official Account as a friend\n" \
        "2. Users who haven't added your LINE Official Account as a friend but have sent a message to your LINE Official Account "
        "(except users who have blocked your LINE Official Account)",
)
def get_profile(
    params: GetProfileParams, soar: SOARClient, asset: Asset
) -> UserProfileOutput:
    logger.debug("Retrieving profile for userId=%s", params.userId)
    client = LineAPIClient(asset)
    r = client.request("GET", _PROFILE_EP.format(userId=params.userId))
    LineAPIClient.check_response(r, "Get Profile")
    data = r.json()

    return UserProfileOutput(**{k: v for k, v in data.items() if k in UserProfileOutput.model_fields})

### get message quota
class QuotaOutput(ActionOutput):
    type: str = OutputField(example_values=["limited", "none"])
    value: int = OutputField(example_values=[500, 1000]) 

@app.action(
    description="Get the monthly message quota limit and current usage count.", 
    verbose="Get the monthly message quota limit and current usage count.",
    read_only=False,
)
def get_message_quota(
    params: Params, soar: SOARClient, asset: Asset
) -> QuotaOutput:
    logger.info("Retrieving message quota...")

    client = LineAPIClient(asset)
    r = client.request("GET", _QUOTA_EP)
    LineAPIClient.check_response(r, "Get Message Quota")
    data = r.json()
    return QuotaOutput(**{k: v for k, v in data.items() if k in QuotaOutput.model_fields})

### get message quota consumption
class QuotaConsumptionOutput(ActionOutput):
    # You can get remaining quota by subtracting totalUsage from the value field in QuotaOutput
    totalUsage: int = OutputField(example_values=[0, 250, 1000])

@app.action(
    description="Get the number of messages sent this month.", 
    verbose="Get the number of messages sent this month. You can get remaining quota by subtracting totalUsage from the value field in the Get Message Quota action.",
    read_only=False,
)
def get_message_quota_consumption(params: Params, soar: SOARClient, asset: Asset) -> QuotaConsumptionOutput:
    logger.info("Retrieving message quota consumption...")

    client = LineAPIClient(asset)
    r = client.request("GET", _QUOTA_CONSUMPTION_EP)
    LineAPIClient.check_response(r, "Get message quota consumption")
    data = r.json()

    return QuotaConsumptionOutput(**{k: v for k, v in data.items() if k in QuotaConsumptionOutput.model_fields})


if __name__ == "__main__":
    app.cli()
