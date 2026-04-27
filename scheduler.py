import json
import os
import sys
import threading
from datetime import datetime
from PIL import Image
from plyer import notification
from pystray import Icon, Menu, MenuItem
from main import load_holiday_data, generate_reminder_tip
# 这个模块负责定时检查是否需要发送休息日提醒通知
def resource_path(relative_path):
    """
    获取资源文件路径。
    - 普通 Python 运行时：从 scheduler.py 所在目录读取
    - PyInstaller 打包后：从临时资源目录 sys._MEIPASS 读取
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
def load_settings(filename="settings.json"):
    """
    读取设置文件。
    """
    file_path = resource_path(filename)

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
def write_log(message):
    """
    写入日志。
    注意：打包后 scheduler.log 会写在程序运行目录或资源路径附近。
    """
    log_path = resource_path("scheduler.log")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{now_str}] {message}\n")
def send_notification(message):
    """
    发送系统通知。
    """
    notification.notify(
        title="休息日提醒",
        message=message,
        timeout=10
    )
already_reminded_days = set()
stop_event = threading.Event()
# 用于控制后台循环停止
stop_event = threading.Event()
def should_trigger(now, remind_hour, remind_start_minute, remind_end_minute):
    """
    判断当前时间是否处于提醒时间窗口内。
    """
    return (
        now.hour == remind_hour
        and remind_start_minute <= now.minute <= remind_end_minute
    )
def create_tray_image():
    """
    读取托盘图标。
    你的图标文件名是 holiday.ico，需要和 scheduler.py 放在同一层。
    打包时也要通过 --add-data 或 spec 文件带进去。
    """
    icon_path = resource_path("holiday.ico")
    return Image.open(icon_path)
def on_exit(icon, item):
    """
    点击托盘菜单中的“退出”时触发。
    """
    write_log("用户通过托盘菜单退出程序")
    # 通知后台调度循环停止
    stop_event.set()
    # 停止托盘图标
    icon.stop()
def run_tray():
    """
    启动系统托盘图标。
    """
    menu = Menu(
        MenuItem("退出", on_exit)
    )
    icon = Icon(
        "BestHolidays",
        create_tray_image(),
        "休息日提醒",
        menu
    )
    icon.run()
def run_scheduler():
    """
    后台定时提醒主循环。
    """
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
    # 启动后等待 2 秒再发送通知。
    # 用 stop_event.wait 替代 time.sleep，方便退出。
    stop_event.wait(2)
    if not stop_event.is_set():
        send_notification(startup_message)
        write_log("已发送启动通知")
    while not stop_event.is_set():
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
        # 等待下一次检查。
        # 如果此时点击“退出”，会立刻结束等待。
        stop_event.wait(check_interval_seconds)
    write_log("调度循环已停止")
if __name__ == "__main__":
    # 调度器放到后台线程里跑
    scheduler_thread = threading.Thread(
        target=run_scheduler,
        daemon=True
    )
    scheduler_thread.start()
    # 托盘图标在主线程运行
    run_tray()
    # 托盘退出后，确保后台线程也结束
    stop_event.set()
    scheduler_thread.join(timeout=5)
    write_log("程序已退出")