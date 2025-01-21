from collections import defaultdict
from datetime import datetime, timedelta


def parse_time_to_minutes(time_str):
    dt = datetime.strptime(time_str.strip(), "%I:%M%p")
    return dt.hour * 60 + dt.minute


def parse_interval(interval_str):
    start_str, end_str = interval_str.split("-")
    return (parse_time_to_minutes(start_str), parse_time_to_minutes(end_str))


def format_minutes(mins):
    hour = (mins // 60) % 24
    minute = mins % 60
    am_pm = "am" if hour < 12 else "pm"
    disp_hour = hour if 1 <= hour <= 12 else (hour - 12 if hour > 12 else 12)
    if minute == 0:
        return f"{disp_hour}{am_pm}"
    else:
        return f"{disp_hour}:{minute:02d}{am_pm}"


def format_interval(start, end):
    return f"{format_minutes(start)}-{format_minutes(end)}"


def subtract_busy(working_interval, busy_intervals):
    free_intervals = []
    working_start, working_end = working_interval
    busy_sorted = sorted(busy_intervals, key=lambda x: x[0])

    current = working_start
    for b_start, b_end in busy_sorted:
        if b_start > current:
            free_intervals.append((current, b_start))
        if b_end > current:
            current = max(current, b_end)
    if current < working_end:
        free_intervals.append((current, working_end))
    return free_intervals


def interval_intersection(interval1, interval2):
    s = max(interval1[0], interval2[0], 480)
    e = min(interval1[1], interval2[1])
    if s < e:
        return (s, e)
    return None


def generate_meeting_slots(interval, duration=60):
    slots = []
    start, end = interval
    meeting_start = start
    while meeting_start + duration <= end:
        slots.append((meeting_start, meeting_start + duration))
        meeting_start += duration
    return slots


def find_meeting_slots(free_time_of_person1, busy_time_of_person2):
    working_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    working_interval = (8 * 60, 1440)

    for day in working_days:
        if day not in free_time_of_person1:
            free_time_of_person1[day] = []
        if day not in busy_time_of_person2:
            busy_time_of_person2[day] = []

    meeting_slots = defaultdict(list)

    for day in working_days:
        day_slots = []
        person1_intervals = []
        for interval_str in free_time_of_person1[day]:
            person1_intervals.append(parse_interval(interval_str))

        busy_intervals = [
            parse_interval(interval_str) for interval_str in busy_time_of_person2[day]
        ]

        person2_free_intervals = subtract_busy(working_interval, busy_intervals)

        for int1 in person1_intervals:
            for int2 in person2_free_intervals:
                intersect = interval_intersection(int1, int2)
                if intersect:
                    slots = generate_meeting_slots(intersect, duration=60)
                    for s in slots:
                        day_slots.append(format_interval(s[0], s[1]))
        meeting_slots[day] = day_slots

    # Get all slots with their days in a list
    all_slots = [(day, slot) for day in working_days for slot in meeting_slots[day]]

    if not all_slots:
        return None

    day, slot = all_slots[0]
    return f"{day}: {slot}"
