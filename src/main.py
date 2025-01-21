from src.integrations.telegram import get_last_five_users
from src.integrations.telegram_desktop import launch_telegram
import asyncio


async def main():
    # Get history
    chat_history, client_name = await get_last_five_users()

    # Launch desktop client
    await launch_telegram(chat_history, client_name)


if __name__ == "__main__":
    asyncio.run(main())
