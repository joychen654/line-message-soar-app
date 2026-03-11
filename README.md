# Line_Message

Publisher: Joy Chen <br>
Connector Version: 1.0.0 <br>
Product Vendor: Line <br>
Product Name: Line Message <br>
Minimum Product Version: 7.0.0

Line Message

### Configuration variables

This table lists the configuration variables required to operate Line_Message. These variables are specified when configuring a Line Message asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**channel_access_token** | required | password | channel access token |

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate the Channel Access Token by calling GET /info. <br>
[push message](#action-push-message) - Sends a message to a user, group chat, or multi-person chat at any time. <br>
[multicast message](#action-multicast-message) - Send a message to multiple LINE users at once <br>
[broadcast message](#action-broadcast-message) - Send a message to all users who have added the bot as a friend. <br>
[get profile](#action-get-profile) - Get the profile of a LINE user by their user ID. <br>
[get message quota](#action-get-message-quota) - Get the monthly message quota limit and current usage count. <br>
[get message quota consumption](#action-get-message-quota-consumption) - Get the number of messages sent this month.

## action: 'test connectivity'

Validate the Channel Access Token by calling GET /info.

Type: **test** <br>
Read only: **True**

Basic test for app.

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'push message'

Sends a message to a user, group chat, or multi-person chat at any time.

Type: **generic** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**message** | required | Text content of the message to send | string | |
**to** | required | LINE user ID, group ID, or room ID to send the message to | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.message | string | | |
action_result.parameter.to | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'multicast message'

Send a message to multiple LINE users at once

Type: **generic** <br>
Read only: **False**

Send a message to multiple LINE users at once (up to 500 recipients). You can't send messages to group chats or multi-person chats

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**tos** | required | Comma-separated LINE user IDs to send the message to | string | |
**message** | required | Text content of the message to send | string | |
**notificationDisabled** | optional | Set to true to suppress push notifications for this message | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.tos | string | | |
action_result.parameter.message | string | | |
action_result.parameter.notificationDisabled | boolean | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'broadcast message'

Send a message to all users who have added the bot as a friend.

Type: **generic** <br>
Read only: **False**

Send a message to all users who have added the bot as a friend.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**message** | required | Text content of the message to broadcast to all friends | string | |
**notificationDisabled** | required | Set to true to suppress push notifications for this message | boolean | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.message | string | | |
action_result.parameter.notificationDisabled | boolean | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get profile'

Get the profile of a LINE user by their user ID.

Type: **generic** <br>
Read only: **False**

Note that the userId is retrieved from the webhook event rather than the LINE ID typically used for adding friends.
You can get the profile information of users who meet one of two conditions:

1. Users who have added your LINE Official Account as a friend
1. Users who haven't added your LINE Official Account as a friend but have sent a message to your LINE Official Account (except users who have blocked your LINE Official Account)

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**userId** | required | LINE user ID of the user whose profile to retrieve | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.parameter.userId | string | | |
action_result.data.\*.userId | string | | Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
action_result.data.\*.displayName | string | | John Doe |
action_result.data.\*.pictureUrl | string | | https://profile.line-scdn.net/ch/v2/p/uf9da5ee2b... |
action_result.data.\*.statusMessage | string | | Hello, LINE! |
action_result.data.\*.language | string | | zh-TW en ja |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get message quota'

Get the monthly message quota limit and current usage count.

Type: **generic** <br>
Read only: **False**

Get the monthly message quota limit and current usage count.

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.data.\*.type | string | | limited none |
action_result.data.\*.value | numeric | | 500 1000 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get message quota consumption'

Get the number of messages sent this month.

Type: **generic** <br>
Read only: **False**

Get the number of messages sent this month. You can get remaining quota by subtracting totalUsage from the value field in the Get Message Quota action.

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failure |
action_result.message | string | | |
action_result.data.\*.totalUsage | numeric | | 0 250 1000 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2026 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
