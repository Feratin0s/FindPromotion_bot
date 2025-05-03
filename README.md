# FindPromotion_bot
🤖 Smart Promotion Finder Bot for Telegram  This Telegram bot helps you find the best deals and promotions in Telegram groups automatically! Instead of manually searching through countless messages, the bot scans promotion channels for keywords you define and notifies you only when a relevant offer appears

---

## Cloning repository

```bash
git clone https://github.com/Feratin0s/FindPromotion_bot.git
```

---

## Starting bot

If you prefer not to use Docker, you can also run the bot directly with Python:

```bash
python main.py 
```

or 

- **On Linux/macOS**:
```bash
python3 main.py
```
---

## 🔧 Prerequisites

Before getting started, ensure you have the following installed:

- **Docker**: To build and run the bot container.
- **Docker Compose**: To manage the bot container easily.
- **Telethon**: To run the bot.

---

### 1. Configure `keywords.json`

First, copy the example file `keywords-example.json` and rename it to `keywords.json`. Then, replace `USER_ID` for your actual Telegram User ID and any desired keywords for the bot to search for.

```bash
cp keywords-example.json keywords.json
```
--> To find your Telegram User ID, message @userinfobot on Telegram.

### 2. Configure `secrets.json`

Next, copy the example file secrets-example.json and rename it to secrets.json. Fill in your bot's credentials (bot_token, api_hash, api_id, and bot_user) obtained from registering your bot on Telegram.

```bash
cp secrets-example.json secrets.json
```

### 3. Create a docker image

To create a Docker image for the project, run the following command inside the folder:

```bash
docker build -t findpromo-app . 
```

### 4. First Run (Interactive Terminal for Telegram Code)

Run the following command to start the bot in interactive mode, just to get the Telegram code and have an interactive terminal:

```bash
docker run -it --rm -v $(pwd):/app findpromo-app
```

### 5. Run the Bot Permanently

To run the bot in the background permanently, use Docker Compose. Run the following command:

```bash
docker-compose up -d
```

If you need to recreate the bot container or update the Git repository, you may want to remove unused Docker images. You can do so with the following command:

```bash
docker image prune -a
```

And recreate the docker image and docker-compose container.

---

