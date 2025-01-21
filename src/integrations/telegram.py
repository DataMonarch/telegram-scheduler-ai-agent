from telethon import TelegramClient
from telethon.tl.types import User
from .telegram_config import load_config
import logging
from datetime import datetime
import os


async def get_last_five_users():
    config = load_config()["telegram"]
    client = TelegramClient(
        config["session_name"], config["api_id"], config["api_hash"]
    )

    chat_history = []
    recent_users = []
    async with client:
        await client.start(config["phone_number"])

        me = await client.get_me()
        logging.info(f"Logged in as {me.first_name} {me.last_name}")
        client_name = f"{me.first_name} {me.last_name}"

        async for dialog in client.iter_dialogs():
            if (
                isinstance(dialog.entity, User)
                and dialog.entity.username in ["rongo2", "john_doe2099"]
                and dialog.entity.id not in [u["id"] for u in recent_users]
            ):
                last_message = await client.get_messages(dialog.entity, limit=1)
                if dialog.entity.username is None or (last_message and last_message[0].from_id and last_message[0].from_id.user_id == (await client.get_me()).id):
                    continue

                recent_users.append(
                    {
                        "id": dialog.entity.id,
                        "name": dialog.name,
                        "username": getattr(dialog.entity, "username", None),
                        "date": dialog.date,
                    }
                )

        # Sort by most recent and get top 5
        recent_users.sort(key=lambda x: x["date"], reverse=True)
        recent_users = recent_users[:5]

        # Get last 3 messages for each user
        for user in recent_users:
            messages = await client.get_messages(user["id"], limit=3)

            history = {
                "dialog_name": user["name"],
                "username": user["username"],
                "messages": [],
            }

            for msg in reversed(messages):  # Oldest to newest
                sender = await msg.get_sender()
                if msg.text:  # Only include messages with text
                    history["messages"].append(
                        {
                            "sender": f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}".strip().replace(
                                "None", ""
                            ),
                            "text": msg.text,
                            "date": msg.date,
                        }
                    )

            chat_history.append(history)

    # Logging
    os.makedirs("logging", exist_ok=True)
    current_time = datetime.now().strftime("%H:%M")

    formatted_history = f"Retrieved dialogs at {current_time}\n"
    formatted_history += "=" * 50 + "\n\n"

    for i, chat in enumerate(chat_history, 1):
        formatted_history += (
            f"{i}. Dialog: {chat['dialog_name']} (@{chat['username']})\n"
        )
        for message in chat["messages"]:
            formatted_history += (
                f"   {message['date']} - @{message['sender']}: {message['text']}\n"
            )
        formatted_history += "-" * 50 + "\n\n"

    # Prepend to file
    try:
        with open(
            "logging/chat_history.log", "r+", encoding="utf-8", errors="replace"
        ) as f:
            content = f.read()
            f.seek(0)
            f.write(formatted_history + content)
    except FileNotFoundError:
        with open(
            "logging/chat_history.log", "w", encoding="utf-8", errors="replace"
        ) as f:
            f.write(formatted_history)
    client_name = client_name.replace("None", "")
    return chat_history, client_name
