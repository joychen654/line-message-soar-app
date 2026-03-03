LINE_BASE_ENDPOINT = "https://api.line.me/v2/bot"

# POST Endpoints
LINE_INFO_URL = f"{LINE_BASE_ENDPOINT}/info"
LINE_PUSH_URL = f"{LINE_BASE_ENDPOINT}/message/push"
LINE_MULTICAST_URL = f"{LINE_BASE_ENDPOINT}/message/multicast"
LINE_BROADCAST_URL = f"{LINE_BASE_ENDPOINT}/message/broadcast"

# GET Endpoints
LINE_GET_PROFILE_URL = f"{LINE_BASE_ENDPOINT}/profile/{{userId}}"
LINE_MESSAGING_QUOTA_URL = f"{LINE_BASE_ENDPOINT}/message/quota"