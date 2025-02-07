import aiohttp


async def send_slack_message(message: str, channel: str, webhook_url: str):
    try:
        payload = {"text": message, "channel": "#" + channel}
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    print(f"Failed to send Slack message. Status: {response.status}")
                else:
                    print(f"Slack message sent successfully to {channel}")
    except Exception as e:
        print(f"Error sending Slack message: {str(e)}")


async def send_error_to_slack(error_message: str):
    from config import settings

    await send_slack_message(
        f"[{settings.ENV}] Error: {error_message}",
        settings.SLACK_ERROR_CHANNEL,
        settings.SLACK_WEBHOOK_URL_ERROR,
    )


async def send_info_to_slack(info_message: str):
    from config import settings

    await send_slack_message(
        f"[{settings.ENV}] Info: {info_message}",
        settings.SLACK_INFO_CHANNEL,
        settings.SLACK_WEBHOOK_URL_INFO,
    )
