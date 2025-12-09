# Configuration file - fill values here
SECRET_KEY = "change_this_secret"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # change this
DATABASE = "shop.db"

# Shop settings
CURRENCY = "₭"  # Laos Kip symbol
SHOP_CREDIT = 1000000  # initial shop credit in smallest currency unit (e.g., Kip)

# QR / Payment
QR_IMAGE_PATH = "static/qr_placeholder.png"  # put your QR image here
BANK_ACCOUNT_NAME = "ชื่อบัญชีของคุณ"
BANK_ACCOUNT_NUMBER = "000-000-0000"

# API placeholders (fill when you have real API keys)
GAME_API_ENDPOINT = ""
GAME_API_KEY = ""

# Notifications (optional) - provide tokens if you want notifications to work
LINE_NOTIFY_TOKEN = ""    # fill for Line Notify
TELEGRAM_BOT_TOKEN = ""   # fill for Telegram bot
TELEGRAM_CHAT_ID = ""     # chat id to send notifications
