import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import UserStatusOnline, UserStatusOffline
import config
from colorama import init, Fore, Style
import os
import sys
import requests

init()

client = TelegramClient('session', config.API_ID, config.API_HASH)

HEADER = f"{Fore.CYAN}╔════════════════════════════════════╗{Style.RESET_ALL}"
FOOTER = f"{Fore.CYAN}╚════════════════════════════════════╝{Style.RESET_ALL}"
DIVIDER = f"{Fore.BLUE}║{Style.RESET_ALL} {'-' * 34} {Fore.BLUE}║{Style.RESET_ALL}"

LOG_FILE = "status_log.txt"
REPORT_FILE = "manual_report_{}.txt"

TELEGRAM_API_URL = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"

def log_to_file(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def create_manual_report():
    today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = REPORT_FILE.format(today)
    
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        with open(LOG_FILE, "r", encoding="utf-8") as log_f:
            content = log_f.read()
        with open(report_filename, "w", encoding="utf-8") as report_f:
            report_f.write(f"Ручной отчёт за {today}\n")
            report_f.write("=" * 40 + "\n")
            report_f.write(content)
        open(LOG_FILE, "w").close()
        print(f"{Fore.YELLOW}Создан отчёт: {report_filename}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Лог пуст или не существует. Нечего сохранять.{Style.RESET_ALL}")

def send_telegram_message(message):
    payload = {
        "chat_id": config.CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(TELEGRAM_API_URL, json=payload)
    if response.status_code != 200:
        print(f"{Fore.RED}Ошибка отправки в Telegram: {response.text}{Style.RESET_ALL}")

async def handle_input():
    loop = asyncio.get_event_loop()
    while True:
        command = await loop.run_in_executor(None, sys.stdin.readline)
        command = command.strip().lower()
        if command == "report":
            create_manual_report()
        elif command == "exit":
            print(f"{Fore.CYAN}Завершение работы...{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.YELLOW}Неизвестная команда. Введите 'report' для отчёта или 'exit' для выхода.{Style.RESET_ALL}")

async def track_user(target):
    await client.start()

    print(HEADER)
    print(f"{Fore.BLUE}║{Style.RESET_ALL}    Авторизация прошла успешно    {Fore.BLUE}║{Style.RESET_ALL}")
    print(DIVIDER)
    log_to_file("Авторизация прошла успешно")
    send_telegram_message("🔔 *Авторизация прошла успешно*")

    try:
        entity = await client.get_entity(target)
        if not entity:
            error_msg = "Ошибка: Пользователь не найден"
            print(f"{Fore.BLUE}║{Style.RESET_ALL}  {error_msg}  {Fore.BLUE}║{Style.RESET_ALL}")
            print(FOOTER)
            log_to_file(error_msg)
            send_telegram_message(f"❌ *{error_msg}*")
            return
    except ValueError as e:
        error_msg = f"Ошибка: {e}"
        print(f"{Fore.BLUE}║{Style.RESET_ALL}  {error_msg}  {Fore.BLUE}║{Style.RESET_ALL}")
        print(FOOTER)
        log_to_file(error_msg)
        send_telegram_message(f"❌ *{error_msg}*")
        return

    username = entity.first_name or entity.username
    print(f"{Fore.BLUE}║{Style.RESET_ALL}  Отслеживаю: {Fore.YELLOW}{username:^20}{Style.RESET_ALL}  {Fore.BLUE}║{Style.RESET_ALL}")
    print(FOOTER)
    log_to_file(f"Отслеживаю: {username}")
    send_telegram_message(f"👀 *Отслеживаю: {username}*")
    print(f"{Fore.CYAN}Для создания отчёта введите 'report'. Для выхода — 'exit'.{Style.RESET_ALL}")

    last_status = None
    online_start_time = None

    while True:
        user = await client.get_entity(entity.id)
        current_status = user.status
        now = datetime.now()

        if current_status != last_status:
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            print(HEADER)
            if isinstance(current_status, UserStatusOnline):
                online_start_time = now
                status_msg = f"Статус: {Fore.GREEN}ОНЛАЙН{Style.RESET_ALL} ★"
                print(f"{Fore.BLUE}║{Style.RESET_ALL}  {now_str}  {Fore.BLUE}║{Style.RESET_ALL}")
                print(f"{Fore.BLUE}║{Style.RESET_ALL}  {status_msg}  {Fore.BLUE}║{Style.RESET_ALL}")
                log_to_file("Статус: ОНЛАЙН")
                send_telegram_message(f"✅ *{username} онлайн* ({now_str})")
            elif isinstance(current_status, UserStatusOffline) and online_start_time:
                online_duration = now - online_start_time
                minutes = int(online_duration.total_seconds() // 60)
                seconds = int(online_duration.total_seconds() % 60)
                status_msg = f"Статус: {Fore.RED}ОФФЛАЙН{Style.RESET_ALL} ✘"
                time_msg = f"{Fore.GREEN}Время онлайн: {minutes} мин {seconds} сек{Style.RESET_ALL}"
                print(f"{Fore.BLUE}║{Style.RESET_ALL}  {now_str}  {Fore.BLUE}║{Style.RESET_ALL}")
                print(f"{Fore.BLUE}║{Style.RESET_ALL}  {status_msg}  {Fore.BLUE}║{Style.RESET_ALL}")
                print(f"{Fore.BLUE}║{Style.RESET_ALL}  {time_msg}  {Fore.BLUE}║{Style.RESET_ALL}")
                log_to_file(f"Статус: ОФФЛАЙН (Время онлайн: {minutes} мин {seconds} сек)")
                send_telegram_message(f"❌ *{username} оффлайн* ({now_str})\n🕓 Время онлайн: {minutes} мин {seconds} сек")
                online_start_time = None
            elif isinstance(current_status, UserStatusOffline):
                status_msg = f"Статус: {Fore.RED}ОФФЛАЙН{Style.RESET_ALL} ✘"
                print(f"{Fore.BLUE}║{Style.RESET_ALL}  {now_str}  {Fore.BLUE}║{Style.RESET_ALL}")
                print(f"{Fore.BLUE}║{Style.RESET_ALL}  {status_msg}  {Fore.BLUE}║{Style.RESET_ALL}")
                log_to_file("Статус: ОФФЛАЙН")
                send_telegram_message(f"❌ *{username} оффлайн* ({now_str})")
            else:
                status_msg = "Статус: Неизвестен ⚠"
                print(f"{Fore.BLUE}║{Style.RESET_ALL}  {now_str}  {Fore.BLUE}║{Style.RESET_ALL}")
                print(f"{Fore.BLUE}║{Style.RESET_ALL}  {status_msg}  {Fore.BLUE}║{Style.RESET_ALL}")
                log_to_file("Статус: Неизвестен")
                send_telegram_message(f"⚠ *{username}: Статус неизвестен* ({now_str})")
            print(FOOTER)
            last_status = current_status

        await asyncio.sleep(5)

async def main():
    print(f"{Fore.CYAN}Запуск Telegram Status Tracker...{Style.RESET_ALL}")
    target = input(f"{Fore.YELLOW}Введите номер телефона (например, +79991234567) или юзернейм (например, @username): {Style.RESET_ALL}")
    await asyncio.gather(track_user(target), handle_input())

if __name__ == "__main__":
    if os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
    asyncio.run(main())