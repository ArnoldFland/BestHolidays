import json
import os
import sys
import time
from datetime import datetime
from plyer import notification
from main import load_holiday_data, generate_reminder_tip
# 这个模块负责定时检查是否需要发送休息日提醒通知
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
def load_settings(filename="settings.json"):
    file_path = resource_path(filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
def write_log(message):
    log_path = resource_path("scheduler.log")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{now_str}] {message}\n")
def send_notification(message):
    notification.notify(
        title="休息日提醒",
        message=message,
        timeout=10
    )
already_reminded_days = set()
def should_trigger(now, remind_hour, remind_start_minute, remind_end_minute):
    return (
        now.hour == remind_hour
        and remind_start_minute <= now.minute <= remind_end_minute
    )
def run_scheduler():
    holidays, workdays = load_holiday_data()
    settings = load_settings()

    remind_hour = settings.get("remind_hour", 14)
    remind_start_minute = settings.get("remind_start_minute", 0)
    remind_end_minute = settings.get("remind_end_minute", 10)
    check_interval_seconds = settings.get("check_interval_seconds", 30)
    startup_message = (
        f"程序已启动，正在后台运行\n"
        f"提醒时间窗口：{remind_hour:02d}:{remind_start_minute:02d}"
        f" ~ {remind_hour:02d}:{remind_end_minute:02d}"
    )
    write_log("程序已启动")
    write_log(
        f"提醒时间窗口：{remind_hour:02d}:{remind_start_minute:02d}"
        f" ~ {remind_hour:02d}:{remind_end_minute:02d}"
    )
    write_log(f"检查间隔：{check_interval_seconds} 秒")
    time.sleep(2)
    send_notification(startup_message)
    write_log("已发送启动通知")
    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        if (
            should_trigger(now, remind_hour, remind_start_minute, remind_end_minute)
            and today_str not in already_reminded_days
        ):
            today = now.date()
            tip = generate_reminder_tip(today, holidays, workdays)
            write_log(f"检查提醒：{tip}")
            if "休息" in tip and "近期没有临近休息日" not in tip:
                send_notification(tip)
                write_log("已发送通知")
            already_reminded_days.add(today_str)
        time.sleep(check_interval_seconds)
if __name__ == "__main__":
    run_scheduler()