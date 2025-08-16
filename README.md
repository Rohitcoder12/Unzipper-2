# Telegram Unzipper Bot

A powerful and efficient Telegram bot designed to handle large ZIP archives. The bot can download, analyze, unzip, and send back the contents of ZIP files up to 2 GB.

## ✨ Features

-   **Large File Support:** Can download ZIP archives up to 2 GB, the maximum allowed by the Telegram Bot API.
-   **Pre-Extraction Analysis:** Before unzipping, the bot quickly analyzes the archive to count the number of files and videos, informing the user of what's inside.
-   **Interactive Status Updates:** Keeps the user informed with real-time status messages (e.g., "Downloading...", "Analyzing...", "Sending files...").
-   **File Upload:** Sends extracted files back to the user one by one.
    -   *Note: Respects Telegram's 50 MB bot upload limit and will notify the user if a file is too large to send.*
-   **Automatic Cleanup:** Deletes the downloaded ZIP and extracted files after the job is complete to conserve server disk space.
-   **Admin Log Channel:** Forwards the original ZIP file and a final summary report to a private channel for easy monitoring and record-keeping.

## 📋 Prerequisites

Before you begin, you will need:

1.  A Telegram Account.
2.  A Linux VPS (Virtual Private Server). **Ubuntu 22.04** is recommended.
3.  A **Bot Token** from `@BotFather` on Telegram.
4.  A private Telegram channel to use for logging, and its **Channel ID**.

## 🚀 Deployment Instructions

Follow these steps to deploy the bot on your new VPS.

### 1. Connect to Your VPS

Connect to your server using SSH. Open PowerShell (on Windows) or Terminal (on Mac/Linux) and run:

```bash
ssh root@YOUR_SERVER_IP
```

-   Replace `YOUR_SERVER_IP` with the IP address provided by your hosting provider (e.g., Hostinger).
-   You will be prompted for your server's password.

### 2. Initial Server Setup

Run the following commands to update your server and install the necessary software.

```bash
# Update package lists and upgrade existing packages
sudo apt update && sudo apt upgrade -y

# Install Python, pip (Python's package manager), and screen
sudo apt install python3 python3-pip screen -y
```

### 3. Install Python Libraries

Install the required Python library for the bot.

```bash
pip install --upgrade python-telegram-bot
```

### 4. Create the Bot File

Create a directory for the bot, move into it, and then create the `bot.py` file using the `nano` text editor.

```bash
# Create a folder for the bot
mkdir unzipper-bot
cd unzipper-bot

# Create and open the Python file for editing
nano bot.py
```

### 5. Add and Configure the Code

1.  **Copy the entire content** of the `bot.py` script provided above.
2.  **Paste it** into the `nano` editor window (in PowerShell, a right-click will paste the content).
3.  **Configure your credentials:** Use the arrow keys to scroll to the top of the file and replace the placeholder values for `BOT_TOKEN` and `LOG_CHANNEL_ID` with your own.
4.  **Save and Exit:**
    -   Press `Ctrl + O`, then press `Enter` to save the file.
    -   Press `Ctrl + X` to exit the editor.

### 6. Run the Bot 24/7

We will use `screen` to ensure the bot keeps running even after you disconnect from the server.

1.  **Start a new `screen` session:**
    ```bash
    screen -S unzipper-bot
    ```

2.  **Run the bot script inside the screen session:**
    ```bash
    python3 bot.py
    ```
    You should see the message: `Bot started! Send it a ZIP file.`

3.  **Detach from the session:** Press **`Ctrl + A`**, then press **`D`**.

Your bot is now running live on the server, 24/7! You can safely close your PowerShell window.

## ⚙️ Managing the Bot

-   **To check on the bot's logs:** Connect to your VPS via SSH and re-attach to the screen session:
    ```bash
    screen -r unzipper-bot
    ```
-   **To stop the bot:** Re-attach to the session and press `Ctrl + C`.
-   **To restart the bot:** After stopping it, just run `python3 bot.py` again inside the same screen session.
