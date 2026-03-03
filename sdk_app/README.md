# LINE Message

This is a SOAR Connector in order to connect to LINE(https://www.line.me/en/)
Created based on https://developers.line.biz/en/reference/messaging-api/

## Prerequisite
- You should follow this documentation (https://developers.line.biz/en/docs/messaging-api/getting-started/) to get your LINE environment prepared.
- You can send a certain number of messages each month for free and it differs from countries. Details can be found on https://developers.line.biz/en/docs/messaging-api/pricing/

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **Channel Access Token** | Access Token | Yes | Long-lived token from LINE Developers Console |


## Supported Actions
### test connectivity
### send push message
### multicast message
### broadcast message
### get profile