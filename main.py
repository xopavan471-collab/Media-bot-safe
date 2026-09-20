
import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ADMIN CONFIGURATION (Apni Telegram ID yahan dalein)
ADMIN_ID = 8562470788  # Replace with your Telegram User ID

# Simple file-based user storage
USERS_FILE = "users.txt"

def add_user(user_id):
    users = get_users()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# Progress Bar Generator
def make_progress_bar(percent):
    done = int(percent // 10)
    return "■" * done + "□" * (10 - done)

# Progress Hook for yt-dlp
def make_progress_hook(loop, bot, chat_id, message_id):
    last_text = {"text": ""}

    def progress_hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed', 0) or 0
            eta = d.get('eta', 0) or 0

            percent = (downloaded / total_bytes * 100) if total_bytes > 0 else 0
            speed_mb = speed / (1024 * 1024)
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total_bytes / (1024 * 1024)

            text = (
                f"Status Downloading...📥**\n"
                f"{make_progress_bar(percent)} {percent:.1f}%\n"
                f"Speed: {speed_mb:.2f} MB/s\n"
                f"Size: {downloaded_mb:.1f} MB / {total_mb:.1f} MB\n"
                f"ETA: {eta}s"
            )

            if text != last_text["text"]:
                last_text["text"] = text
                asyncio.run_coroutine_threadsafe(
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown'),
                    loop
                )

    return progress_hook

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    
    welcome_text = (
        "<b>𝐇ᴇʏ 𝐖ᴇʟᴄᴏᴍᴇ ᴛᴏ 𝐃ᴏᴡɴʟᴏᴀᴅᴇʀ 𝐁ᴏᴛ.</b>\n\n"
        "𝐈 𝐀ᴍ 𝐔𝐑L 𝐕ɪᴅᴇᴏ 𝐃ᴏᴡɴʟᴏᴀᴅᴇʀ ᴡɪᴛʜ 𝐌ᴜʟᴛɪᴘʟᴇ ғᴀsᴛ ᴘʀᴏsᴇss ғᴇᴀᴛᴜʀᴇs 𝐀ʀᴇ 𝐀ᴠᴀɪʟᴀʙʟᴇ ᴛᴏ 𝐃ᴏᴡɴʟᴏᴀᴅ "𝐘ᴏᴜ ᴛᴜʙᴇ 𝐈ɴsᴛᴀɢʀᴀᴍ Fᴀᴄᴇʙᴏᴏᴋ" 𝐕ɪᴅᴇᴏs 𝐀ɴᴅ ᴄᴀɴ 𝐀ʟᴡᴀʏs 𝐇ᴇʟᴘ ᴛʜɪs 𝐈F 𝐘ᴏᴜ 𝐑ᴇᴀᴅ𝐘 ᴛᴏ 𝐃ᴏᴡɴʟᴏᴀᴅ 𝐒ᴇɴᴅ Lɪɴᴋ, 𝐖ᴇ 𝐃ɪʀᴇᴄᴛ 𝐔ᴘʟᴏᴀᴅ ʏᴏᴜʀ 𝐕ɪᴅᴇᴏ, 𝐏ʟᴇᴀsᴇ 𝐆ɪᴠᴇ ᴍᴇ 𝐑ᴇᴏᴜᴇsᴛ ᴛᴏ sᴛᴀʀᴛ"
        "𝐏ʟᴇᴀsᴇ 𝐒ʜᴀʀᴇ 𝐀ɴᴅ 𝐆ɪᴠᴇ 𝐒ᴜᴘᴘᴏʀᴛ."
    )
    
    keyboard = [
        [
            InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url="https://t.me/your_channel"),
            InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url="https://t.me/your_support")
        ],
        [
            InlineKeyboardButton("𝐒ʜᴀʀᴇ", callback_data="help"),
            InlineKeyboardButton("𝐃ᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/your_dev")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

# Admin Status Command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = get_users()
    await update.message.reply_text(f"📊 **Total Bot Users:** {len(users)}")

# Admin Broadcast Command (/broadcast Your message here)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    msg = update.message.text.replace("/broadcast", "").strip()
    if not msg:
        await update.message.reply_text("❌ Usage: `/broadcast Your Message Here`", parse_mode='Markdown')
        return

    users = get_users()
    success, failed = 0, 0
    await update.message.reply_text("📢 Starting Broadcast...")

    for u_id in users:
        try:
            await context.bot.send_message(chat_id=int(u_id), text=msg)
            success += 1
        except Exception:
            failed += 1

    await update.message.reply_text(f"Broadcast Complete!\nSuccess: {success}\nFailed: {failed}")

# Video Downloader Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    
    url = update.message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return

    # Step 1: Processing Status
    status_msg = await update.message.reply_text("**𝐏ʀᴏsᴇssɪɴɢ...⚡️**", parse_mode='Markdown')

    loop = asyncio.get_running_loop()
    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)

    # Format selection rules:
    # Shorts -> 1080p limit
    # Long YouTube -> 360p limit
    # Others -> Best direct mp4 format
    if "youtube.com/shorts/" in url or "youtu.be/" in url and "shorts" in url:
        fmt = "b[ext=mp4][height<=1080]/best[ext=mp4][height<=1080]/best"
    elif "youtube.com" in url or "youtu.be" in url:
        fmt = "b[ext=mp4][height<=360]/best[ext=mp4][height<=360]/best"
    else:
        fmt = "b[ext=mp4]/best[ext=mp4]/best"

    ydl_opts = {
        'format': fmt,
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [make_progress_hook(loop, context.bot, status_msg.chat_id, status_msg.message_id)],
    }

    try:
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)

        # Download Video
        file_path = await loop.run_in_executor(None, download)

        # Step 2: Upload Status
        await status_msg.edit_text("**ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ᴜᴘʟᴏᴀᴅɪɴɢ...⚡️**", parse_mode='Markdown')

        # Upload Video to Chat
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="**ᴅᴏᴡɴʟᴏᴀᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ✨**", parse_mode='Markdown')

        # Cleanup
        await status_msg.delete()
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("❌ **Process fail ho gaya! Link check karein ya thodi der baad try karein.**", parse_mode='Markdown')

# Main Runner
if __name__ == '__main__':
    # Add your Telegram Bot Token Here
    BOT_TOKEN = "8283637087:AAGYwNrjrCd216-K_Z0h2PTn6TtisKnKm6A"
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
