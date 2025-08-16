import os
import shutil
import zipfile
import logging
import time
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
# Replace with your actual Bot Token from BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
# Replace with your channel's ID (e.g., -1001234567890)
LOG_CHANNEL_ID = -100xxxxxxxxxx

# --- SCRIPT SETTINGS ---
DOWNLOAD_DIR = "downloads"
EXTRACT_DIR = "extracted"
VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Helper Functions ---
def cleanup(path):
    """Safely remove a file or directory."""
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            logger.info(f"Cleaned up directory: {path}")
        else:
            os.remove(path)
            logger.info(f"Cleaned up file: {path}")

# --- Bot Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\nSend me a ZIP file. I will analyze it, unzip it, and send the contents back to you.",
    )

# --- Core Logic: Handling the ZIP File ---
async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the entire process of downloading, analyzing, and unzipping a file."""
    chat_id = update.message.chat_id
    user = update.effective_user
    document = update.message.document

    # 1. Forward the original file to the log channel for record-keeping
    if LOG_CHANNEL_ID:
        try:
            await context.bot.forward_message(chat_id=LOG_CHANNEL_ID, from_chat_id=chat_id, message_id=update.message.message_id)
        except Exception as e:
            logger.error(f"Could not forward file to log channel: {e}")

    status_message = await update.message.reply_text("✅ File received. Starting download...")
    
    # Create unique directories for this job to handle multiple users simultaneously
    timestamp = str(int(time.time()))
    unique_download_dir = os.path.join(DOWNLOAD_DIR, timestamp)
    unique_extract_dir = os.path.join(EXTRACT_DIR, timestamp)
    os.makedirs(unique_download_dir, exist_ok=True)
    os.makedirs(unique_extract_dir, exist_ok=True)
    
    zip_path = os.path.join(unique_download_dir, document.file_name)

    # 2. Download the file from Telegram
    try:
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(zip_path)
        logger.info(f"File downloaded to: {zip_path}")
    except Exception as e:
        logger.error(f"Failed to download file: {e}")
        await status_message.edit_text("❌ An error occurred during download.")
        cleanup(unique_download_dir)
        cleanup(unique_extract_dir)
        return

    # 3. Analyze the ZIP file before extracting
    await status_message.edit_text("📥 Download complete! Analyzing archive...")
    video_count = 0
    total_files = 0
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            total_files = len(file_list)
            for filename in file_list:
                if any(filename.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                    video_count += 1
    except Exception as e:
        await status_message.edit_text("❌ Error: The file is not a valid ZIP archive or it is corrupted.")
        cleanup(unique_download_dir)
        cleanup(unique_extract_dir)
        return
        
    # 4. Send the custom reply based on the analysis
    base_name = os.path.splitext(document.file_name)[0]
    
    if video_count > 0:
        reply_text = f"✅ **{base_name}** ({video_count} videos)\n\nNow extracting and sending the files..."
    else:
        reply_text = f"✅ **{base_name}** ({total_files} files)\n\nNow extracting and sending the files..."
    
    await status_message.edit_text(reply_text, parse_mode='Markdown')

    # 5. Extract the ZIP archive
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(unique_extract_dir)
    except Exception as e:
        logger.error(f"Failed to unzip: {e}")
        await status_message.edit_text(f"❌ An error occurred during unzipping.")
        cleanup(unique_download_dir)
        cleanup(unique_extract_dir)
        return

    # 6. Send the extracted files back to the user
    sent_file_count = 0
    for root, _, files in os.walk(unique_extract_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                # Telegram bots can only upload files up to 50 MB
                if os.path.getsize(file_path) > 50 * 1024 * 1024:
                    await context.bot.send_message(chat_id, f"⚠️ Skipping '{filename}' because it is larger than 50MB.")
                    continue
                
                await context.bot.send_document(chat_id=chat_id, document=open(file_path, 'rb'))
                sent_file_count += 1
                await asyncio.sleep(1) # Small delay to avoid hitting Telegram's rate limits
            except Exception as e:
                logger.error(f"Failed to send file {filename}: {e}")
                await context.bot.send_message(chat_id, f"❌ Could not send file: {filename}")
    
    final_message = f"✅ All done! Sent {sent_file_count} files from **{base_name}**."
    await status_message.edit_text(final_message, parse_mode='Markdown')

    # 7. Send a final summary to the log channel
    if LOG_CHANNEL_ID:
        try:
            log_summary = (
                f"✅ **Job Complete**\n\n"
                f"**File:** `{document.file_name}`\n"
                f"**User:** {user.first_name} (`{user.id}`)\n"
                f"**Total Files in Zip:** {total_files}\n"
                f"**Sent to User:** {sent_file_count} files"
            )
            await context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=log_summary, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Could not send summary to log channel: {e}")

    # 8. Clean up the downloaded and extracted files to save space
    cleanup(unique_download_dir)
    cleanup(unique_extract_dir)


def main() -> None:
    """Starts the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ZIP, handle_zip))
    
    logger.info("Bot started! Send it a ZIP file.")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == '__main__':
    # Create necessary directories on startup if they don't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    main()
