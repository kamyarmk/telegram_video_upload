# Telegram Video Upload Bot

A Telegram bot that allows users to upload videos after providing their details. The bot supports multiple languages and enables admins to review the submitted videos.

## 🚀 Features

- Users select their language at the start.
- Collects user information (name, age, country, instrument played).
- Accepts and forwards video submissions to admins.
- Uses inline buttons for interaction.
- Supports right-to-left (RTL) text formatting for Persian.

## 🛠️ Setup & Installation

### 1️⃣ Prerequisites

Ensure you have:

- Python 3.13.2+ installed
- A Telegram Bot Token (created via [BotFather](https://t.me/BotFather))
- An admin Telegram chat ID (for receiving submissions)

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/kamyarmk/telegram_video_upload.git
cd telegram-video-bot
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables

Create a `.env` file and add your credentials:

```ini
BOT_TOKEN=your_telegram_bot_token
ADMIN_CHAT_ID=your_admin_chat_id
```

### 5️⃣ Run the Bot

```bash
python bot.py
```

## 🚀 Deploying on Railway

1. Install the [Railway CLI](https://docs.railway.app/cli/install)
2. Initialize the project:
   ```bash
   railway init
   ```
3. Deploy:
   ```bash
   railway up
   ```

## 🔧 Bot Commands

| Command   | Description                 |
| --------- | --------------------------- |
| `/start`  | Starts the bot interaction  |
| `/cancel` | Cancels the current process |

## 🤖 Built With

- `python-telegram-bot` (async version)
- Railway for hosting

## 📜 License

This project is licensed under the MIT License.

## ✨ Contributing

Feel free to open issues or submit pull requests!

