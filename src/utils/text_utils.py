import re
from collections import defaultdict


def add_mins(t):
    pattern = r"(\b\d{1,2})(?:\:(\d{2}))?([ap]m\b)"

    def fix_time(match):
        hour = match.group(1)  # e.g. "9" or "10"
        minutes = match.group(2)  # e.g. "30" or None if missing
        ampm = match.group(3)  # "am" or "pm"

        # If minutes are missing, use "00"; otherwise keep them
        if minutes:
            return f"{hour}:{minutes}{ampm}"
        else:
            return f"{hour}:00{ampm}"

    return re.sub(pattern, fix_time, t)


def parse_schedule(schedule_str):
    pair_pattern = r'"([^"]+)"\s*:\s*\[([^\]]*)\]'
    time_pattern = r'"([^"]+)"'

    def convert_time_format(time_str):
        # Split the time range into start and end times
        start_time, end_time = time_str.split("-")

        def format_single_time(t):
            # Remove any spaces
            t = t.strip()

            # Extract hours, minutes and period
            match = re.match(r"(\d+):(\d+)(am|pm)", t.lower())
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                period = match.group(3)

                # Handle cases where hours > 12 in pm format
                if period == "pm" and hours > 12:
                    hours -= 12

                # Convert to 12-hour format
                if hours == 0:
                    hours = 12
                elif hours > 12:
                    hours -= 12

                return f"{hours}:{minutes:02d}{period}"
            return t

        return f"{format_single_time(start_time)}-{format_single_time(end_time)}"

    schedule = defaultdict(list)

    # Find all key-value pairs
    for day, times_str in re.findall(pair_pattern, schedule_str):
        # Find all time ranges in the captured list string
        print(f">>> Times: {times_str}")

        times_str = times_str.replace(" pm", "pm").replace(" am", "am")
        if "-" in times_str:
            start_time, end_time = times_str.split("-")
            if ":" not in start_time:
                ds_loc = start_time.find("m")
                if len(start_time[:ds_loc]) > 2:
                    start_time = (
                        start_time[: ds_loc - 3] + ":" + start_time[ds_loc - 3 : ds_loc]
                    )

            if ":" not in end_time:
                ds_loc = end_time.find("m")
                if len(end_time[:ds_loc]) > 2:
                    end_time = (
                        end_time[: ds_loc - 3] + ":" + end_time[ds_loc - 3 : ds_loc]
                    )
            times_str = start_time + "-" + end_time

        print(f"Time before: {times_str}")
        times_str = add_mins(times_str)
        print(f"Time after: {times_str}")
        times = re.findall(time_pattern, times_str)
        # Convert each time range to proper 12-hour format
        converted_times = [convert_time_format(t) for t in times]
        schedule[day].extend(converted_times)

    return schedule


def format_chat_history(chat_history):
    formatted_text = ""
    for chat in chat_history["messages"]:
        formatted_text += f"{chat['sender']}:\n"
        formatted_text += f"{chat['text']}\n"
    return formatted_text.strip()
