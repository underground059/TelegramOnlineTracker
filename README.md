# TelegramOnlineTracker
logs entry and exit from online/логгирует вход и выход из онлайна
## Функционал
- Отслеживание статуса "онлайн"/"оффлайн" по номеру или юзернейму
- Логирование в файл `status_log.txt`
- Ручное создание отчётов с помощью команды `report`
- Уведомления в Telegram Bot

## Установка
1. Установите зависимости:
   pip install telethon colorama requests
2. Заполните config.py
3. Запустите tracker.py

## Внимание
   Скрипт использует сессию телеграм для первого запуска потребуется вход
   ----------------------------------------------------------------------
   Онлайн при работе скрипта не отображается
   ----------------------------------------------------------------------
   У юзера должно быть открыто время онлайн или должен быть телеграм премиум
   ----------------------------------------------------------------------
