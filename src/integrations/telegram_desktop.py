import pyautogui
import cv2
import pytesseract
from PIL import ImageGrab
import subprocess
from clicknium import clicknium as cc, locator
from src.utils.image_utils import find_best_match, process_screenshot_text
from src.utils.text_utils import format_chat_history, parse_schedule
from src.services.llm_interaction import send_request_to_llm
from src.integrations.calendar import (
    authenticate_google_calendar,
    get_next_week_events,
    build_events_by_weekday,
)

from src.services.scheduler import (
    find_meeting_slots,
)


import os
import logging
import re
import time

with open("prompts/classify/prompt.txt", "r", encoding="utf8") as f:
    input_prompt_classify = f.read()
with open("prompts/classify/system_prompt.txt", "r", encoding="utf8") as f:
    system_prompt_classify = f.read()

with open("prompts/extract_time/prompt.txt", "r", encoding="utf8") as f:
    input_prompt_extract = f.read()
with open("prompts/extract_time/system_prompt.txt", "r", encoding="utf8") as f:
    system_prompt_extract = f.read()

with open("prompts/send_response/prompt.txt", "r", encoding="utf8") as f:
    input_prompt_send = f.read()
with open("prompts/send_response/system_prompt.txt", "r", encoding="utf8") as f:
    system_prompt_send = f.read()

with open("prompts/decline/prompt.txt", "r", encoding="utf8") as f:
    input_prompt_decline = f.read()
with open("prompts/decline/system_prompt.txt", "r", encoding="utf8") as f:
    system_prompt_decline = f.read()

with open("prompts/done/prompt.txt", "r", encoding="utf8") as f:
    input_prompt_done = f.read()
with open("prompts/done/system_prompt.txt", "r", encoding="utf8") as f:
    system_prompt_done = f.read()

log_dir = "logging"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, "telegram_desktop.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


async def launch_telegram(chat_history, client_name):
    # try:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_dir = os.path.join("screenshots", "session_" + str(timestamp))
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    screen_recorder_index = 0

    pyautogui.press("win")
    time.sleep(1)
    pyautogui.write("Telegram")
    time.sleep(2)
    logging.info(f"\n\n\n\n========= Launching Telegram =========")

    custom_screen_shot_path = os.path.join(
        screenshot_dir, "screen_" + str(screen_recorder_index) + ".png"
    )
    screen_recorder_index += 1
    pyautogui.screenshot(custom_screen_shot_path)

    telegram_icon = find_best_match(
        custom_screen_shot_path, "icons/telegram_icon.png", threshold=0.7
    )

    if telegram_icon:
        pyautogui.click(telegram_icon)
        logging.info("Telegram icon found and clicked")
    else:
        logging.warning("Telegram icon not found")

    custom_screen_shot_path = os.path.join(
        screenshot_dir, "screen_" + str(screen_recorder_index) + ".png"
    )
    screen_recorder_index += 1
    pyautogui.press("win")

    for chat in chat_history:
        username = chat["username"]
        name = chat["dialog_name"] if chat["dialog_name"] else ""
        name = name[:13]

        pyautogui.screenshot(
            custom_screen_shot_path, region=(0, 0, pyautogui.size()[0], 200)
        )
        telegram_search = find_best_match(
            custom_screen_shot_path, "icons/search_icon.png", threshold=0.8
        )

        if telegram_search:
            pyautogui.click(telegram_search)
            logging.info("Telegram search icon found and clicked")
        else:
            logging.warning(
                "Telegram search icon not found, using fallback coordinates"
            )
            pyautogui.click((182, 101))
            pyautogui.hotkey("ctrl", "a")
            pyautogui.press("delete")
        time.sleep(5)
        custom_screen_shot_path = os.path.join(
            screenshot_dir, "screen_" + str(screen_recorder_index) + ".png"
        )
        screen_recorder_index += 1
        pyautogui.screenshot(custom_screen_shot_path)
        pyautogui.write(username)
        time.sleep(2)
        logging.info(f"Searching for username: {username}, name: {name}")

        screenshot = pyautogui.screenshot(region=(0, 0, 600, pyautogui.size()[1]))
        custom_screen_shot_path = os.path.join(
            screenshot_dir, "screen_" + str(screen_recorder_index) + ".png"
        )
        screen_recorder_index += 1
        screenshot.save(custom_screen_shot_path)
        logging.info(
            f"Taking screenshot for username search results. Screenshot saved to {custom_screen_shot_path}"
        )

        x, y = process_screenshot_text(screenshot, name)
        logging.info(f"Found name '{name}' at coordinates x={x}, y={y}")
        pyautogui.click(x, y)
        custom_screen_shot_path = os.path.join(
            screenshot_dir, "screen_" + str(screen_recorder_index) + ".png"
        )
        screen_recorder_index += 1
        pyautogui.screenshot(custom_screen_shot_path)
        history_of_user = format_chat_history(chat)

        logging.info(f"Chat history for user:\n{history_of_user}")
        input_prompt_classify_full = (
            input_prompt_classify + "\nConversation:\n" + history_of_user
        )

        response_classify = send_request_to_llm(
            input_prompt_classify_full, system_prompt_classify
        )
        schedule_meeting = 1 if response_classify == "1" else 0

        logging.info(f"\n\n--------- CLASSIFYING ---------")
        logging.info(f"System prompt for classification:\n{system_prompt_classify}")
        logging.info(f"Input prompt for classification:\n{input_prompt_classify_full}")
        logging.info(
            f"Classification LLM output:\n{response_classify}\nschedule_meeting:{schedule_meeting}"
        )

        input_prompt_done_full = (
            input_prompt_done + "\nConversation:\n" + history_of_user
        )
        input_prompt_done_full = input_prompt_done_full.replace(
            "your_tag", client_name.strip()
        )
        response_done = send_request_to_llm(
            input_prompt_done_full, system_prompt_done, temp=0.5
        )

        want_scheduling = 0
        if schedule_meeting:
            logging.info(f"\n\n--------- IS CONVERSATION OVER? ---------")
            logging.info(f"System prompt for done:\n{system_prompt_done}")
            logging.info(f"Input prompt for done:\n{input_prompt_done_full}")
            logging.info(f"Need reponse LLM output:\n{response_done}")
            boolean_match = re.search(r"Boolean:(\d)|Boolean: (\d)", response_done)
            response_done = (
                boolean_match.group(1) or boolean_match.group(2)
                if boolean_match
                else "0"
            )
            logging.info(f"Boolean match from response_done: {response_done}")
            want_scheduling = 1 if response_done == "0" else 0

        else:
            logging.info(f"The conversation is not about the scheduling a meeting")
            logging.info(f"====== Interaction with the interlocutor is over ======")
            continue

        if want_scheduling:
            logging.info(f"There is a need to schedule a meeting")
            logging.info(f"\n\n--------- EXTRACTING TIME ---------")
            input_prompt_extract_full = input_prompt_extract + "\n" + history_of_user
            input_prompt_extract_full = input_prompt_extract_full.replace(
                "his_tag", name
            )
            response_extract = send_request_to_llm(
                input_prompt_extract_full, system_prompt_extract, temp=1
            )
            logging.info(f"System prompt for time extraction:\n{system_prompt_extract}")
            logging.info(
                f"Input prompt for time extraction:\n{input_prompt_extract_full}"
            )

            logging.info(f"Extraction response: {response_extract}")

            free_time_of_person1 = parse_schedule(response_extract)

            log_str = "\n".join(
                [f"{day}: {times}" for day, times in free_time_of_person1.items()]
            )

            logging.info(f"Free time slots for person1:\n{log_str}")

            logging.info(f"\n\n--------- CHECKING GOOGLE CALENDAR ---------")
            service = authenticate_google_calendar()
            next_week_events = get_next_week_events(service)
            logging.info("Your next week events from Google Calendar:")
            busy_time_of_person2 = build_events_by_weekday(next_week_events)

            log_str = "\n".join(
                [f"{day}: {times}" for day, times in busy_time_of_person2.items()]
            )
            logging.info(f"Your busy time slots:\n{log_str}")

            free_meeting_slot = find_meeting_slots(
                free_time_of_person1, busy_time_of_person2
            )
            logging.info(f"Available meeting slot:\n{free_meeting_slot}")
            if free_meeting_slot is not None:
                logging.info(
                    f"\n\n--------- CHOOSING SPECIFIC TIME AND SENDING A RESPONSE ---------"
                )

                input_prompt_send_full = (
                    input_prompt_send
                    + " "
                    + free_meeting_slot.split("-")[0]
                    + ".\nConversation history:\n"
                    + history_of_user
                )
                logging.info(
                    f"System prompt for response generation:\n{system_prompt_send}"
                )
                logging.info(
                    f"Input prompt for response generation:\n{input_prompt_send_full}"
                )
                setting_meeting = send_request_to_llm(
                    input_prompt_send_full,
                    system_prompt_send,
                    temp=0.7,
                    model="llama3.2:3b",
                )
                setting_meeting = setting_meeting.replace("[Your Name]", "")
                logging.info(f"LLM generated response:\n{setting_meeting}")
                pyautogui.write(setting_meeting)

                custom_screen_shot_path = os.path.join(
                    screenshot_dir, "screen_" + str(screen_recorder_index) + ".png"
                )
                screen_recorder_index += 1
                pyautogui.screenshot(custom_screen_shot_path)

                pyautogui.press("enter")

                custom_screen_shot_path = os.path.join(
                    screenshot_dir, "screen_" + str(screen_recorder_index) + ".png"
                )
                screen_recorder_index += 1
                pyautogui.screenshot(custom_screen_shot_path)

                logging.info(f"The meeting is scheduled")
                logging.info(f"====== Interaction with the interlocutor is over ======")
            else:
                logging.info(f"\n\n--------- ASKING FOR ANOTHER TIME ---------")
                logging.info("No available meeting slots")
                input_prompt_decline_full = (
                    input_prompt_decline
                    + ".\nConversation history:\n"
                    + history_of_user
                )
                logging.info(
                    f"System prompt for response gleneration:\n{system_prompt_decline}"
                )
                logging.info(
                    f"Input prompt for response generation:\n{input_prompt_decline_full}"
                )
                decline_response = send_request_to_llm(
                    input_prompt_decline_full,
                    system_prompt_decline,
                    temp=0.7,
                    model="llama3.2:3b",
                )
                logging.info(f"LLM generated response:\n{decline_response}")
                pyautogui.write(decline_response.replace("[Your Name]", ""))

                custom_screen_shot_path = os.path.join(
                    screenshot_dir, "screen_" + str(screen_recorder_index) + ".png"
                )
                screen_recorder_index += 1
                pyautogui.screenshot(custom_screen_shot_path)

                pyautogui.press("enter")

                custom_screen_shot_path = os.path.join(
                    screenshot_dir, "screen_" + str(screen_recorder_index) + ".png"
                )
                screen_recorder_index += 1
                pyautogui.screenshot(custom_screen_shot_path)

                logging.info(
                    f"The meeting is not scheduled, the interlocutor is asked to suggest another time"
                )
                logging.info(f"====== Interaction with the interlocutor is over ======")
        else:
            logging.info(f"No need to schedule a meeting")
            logging.info(f"====== Interaction with the interlocutor is over ======")

    if len(chat_history) == 0:
        logging.info(f"No chats requiring attention is found")
        screen_width, screen_height = pyautogui.size()
        pyautogui.click(screen_width // 2, screen_height // 2)
        logging.info("Clicked center of screen")
    pyautogui.hotkey("alt", "f4")
    logging.info("============ Closed Telegram window ============")

    # except Exception as e:
    #     print(f"Error: {e}")
