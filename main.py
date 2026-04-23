import json
import os
import sys
from plyer import notification
from datetime import datetime, timedelta, date
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
def load_holiday_data(filename="holidays.json"):
    file_path = resource_path(filename)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    holidays = set(data.get("holidays", []))
    workdays = set(data.get("workdays", []))
    return holidays, workdays
def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()
def format_date(d: date) -> str:
    return d.strftime("%Y-%m-%d")
def weekday_name(d: date) -> str:
    names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return names[d.weekday()]
def is_rest_day(d: date, holidays: set[str], workdays: set[str]) -> bool:
    d_str = format_date(d)
    if d_str in holidays:
        return True
    if d_str in workdays:
        return False
    return d.weekday() >= 5
def day_type(d: date, holidays: set[str], workdays: set[str]) -> str:
    d_str = format_date(d)
    if d_str in holidays:
        return "法定节假日"
    if d_str in workdays:
        return "调休"
    if d.weekday() >= 5:
        return "周末"
    return "工作日"
def find_next_rest_day(start_day: date, holidays: set[str], workdays: set[str]) -> date:
    current = start_day
    while not is_rest_day(current, holidays, workdays):
        current += timedelta(days=1)
    return current
def find_rest_end(start_day: date, holidays: set[str], workdays: set[str]) -> date:
    current = start_day
    while True:
        next_day = current + timedelta(days=1)
        if is_rest_day(next_day, holidays, workdays):
            current = next_day
        else:
            return current
def generate_reminder_tip(today: date, holidays: set[str], workdays: set[str]) -> str:
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    # 情况1：明天开始休息
    if is_rest_day(tomorrow, holidays, workdays):
        end_day = find_rest_end(tomorrow, holidays, workdays)
        total_days = (end_day - tomorrow).days + 1
        return (
            f"提醒：明天开始休息\n"
            f"开始时间：{format_date(tomorrow)} {weekday_name(tomorrow)}\n"
            f"结束时间：{format_date(end_day)} {weekday_name(end_day)}\n"
            f"共 {total_days} 天"
        )
    # 情况2：今天是休息前最后一个工作日
    if (
        not is_rest_day(today, holidays, workdays)
        and not is_rest_day(tomorrow, holidays, workdays)
        and is_rest_day(day_after_tomorrow, holidays, workdays)
    ):
        end_day = find_rest_end(day_after_tomorrow, holidays, workdays)
        total_days = (end_day - day_after_tomorrow).days + 1
        return (
            f"提醒：今天是休息前最后一个工作日\n"
            f"休息将于：{format_date(day_after_tomorrow)} {weekday_name(day_after_tomorrow)} 开始\n"
            f"休息到：{format_date(end_day)} {weekday_name(end_day)}\n"
            f"共 {total_days} 天"
        )
    # 情况3：后天开始休息
    if is_rest_day(day_after_tomorrow, holidays, workdays):
        end_day = find_rest_end(day_after_tomorrow, holidays, workdays)
        total_days = (end_day - day_after_tomorrow).days + 1
        return (
            f"提醒：后天开始休息\n"
            f"开始时间：{format_date(day_after_tomorrow)} {weekday_name(day_after_tomorrow)}\n"
            f"结束时间：{format_date(end_day)} {weekday_name(end_day)}\n"
            f"共 {total_days} 天"
        )
    return "提醒：近期没有临近休息日"
def send_notification(tip: str):
    if "休息" in tip and "近期没有临近休息日" not in tip:
        notification.notify(
            title="休息日提醒",
            message=tip,
            timeout=10
        )
# 这个模块负责定时检查是否需要发送休息日提醒通知
def main():
    holidays, workdays = load_holiday_data()
    user_input = input("请输入日期（格式 YYYY-MM-DD，直接回车使用今天）: ").strip()
    if user_input:
        today = parse_date(user_input)
    else:
        today = datetime.today().date()
    print("\n==============================")
    print(f"今天是：{format_date(today)} {weekday_name(today)}")
    print(f"今天类型：{day_type(today, holidays, workdays)}")
    print("==============================")
    if is_rest_day(today, holidays, workdays):
        end_day = find_rest_end(today, holidays, workdays)
        remain_days = (end_day - today).days + 1
        print("今天已经是休息日了！")
        print(f"本次休息持续到：{format_date(end_day)} {weekday_name(end_day)}")
        print(f"从今天算起，还能休息 {remain_days} 天。")
    else:
        next_rest = find_next_rest_day(today, holidays, workdays)
        end_day = find_rest_end(next_rest, holidays, workdays)
        wait_days = (next_rest - today).days
        total_days = (end_day - next_rest).days + 1
        print(f"下一次休息开始于：{format_date(next_rest)} {weekday_name(next_rest)}")
        print(f"距离休息还有：{wait_days} 天")
        print(f"这次休息持续到：{format_date(end_day)} {weekday_name(end_day)}")
        print(f"本次休息总共：{total_days} 天")
        print(f"休息类型：{day_type(next_rest, holidays, workdays)}")
    print("\n------------------------------")
    tip = generate_reminder_tip(today, holidays, workdays)
    print(tip)
    send_notification(tip)
    print("------------------------------")
if __name__ == "__main__":
    main()