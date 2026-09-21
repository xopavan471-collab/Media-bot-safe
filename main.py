import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
BOT_TOKEN = ("BOT_TOKEN", "8283637087:AAH_q5peDqMMadZhU6zlja21JRq6wpkl-7E")
ADMIN_ID = 8562470788  # <--- Apna Telegram Numeric User ID Yahan Daalein

USERS_FILE = "users.json"

# Helper Functions for User Management
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.add(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(list(users), f)

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)

    welcome_text = (
        "𝑾𝑬𝑳𝑪𝑶𝑴𝑬 𝑴𝑹 ⪩ 𝒁𝑬 any 𝑴𝑬𝑫𝑰𝑨 𝑴𝑬𝑫𝑰𝑨 𝑼𝑑𝑳𝑶𝑨𝑫𝑬𝑹 𝑩𝑶𝑻.\n\n"
        "𝑾𝑬 𝑪𝑨𝑵 𝑯𝑬𝑳𝑑 𝑻𝑶 𝑴𝑼𝑳𝑻𝑰𝑷𝑳𝑬 𝑭𝑨𝑺𝑻 𝑷𝑹𝑶𝑺𝑬𝑺𝑺 𝑭𝑬𝑨𝑻𝑼𝑑𝑬𝑺 𝑨𝑹𝑬 𝑨𝑽𝑨𝑰𝑳𝑨𝑽𝑳𝑬 "
        "𝑫𝑶𝑑𝑵𝑳𝑶𝑨𝑫 𝑴𝑬𝑫𝑰𝑨 𝑭𝑰𝑹𝑬 𝑑𝑰𝑻𝑯 𝑭𝑨𝑺𝑻 𝑱𝑼𝑺𝑻 𝑺𝑬𝑵𝑫 𝑽𝑰𝑫𝑬𝑶 𝑳𝑰𝑵𝑲, "
        "𝑾𝑬 𝑫𝑰𝑑𝑬𝑪𝑻 𝑼𝑑𝑳𝑶𝑨𝑫 𝒀𝑶𝑑𝑹 𝑭𝑰𝑳𝑬, 𝑽𝑰𝑫𝑬𝑶 𝑺𝑰𝒁𝑬 𝑨𝑳𝑳𝑶𝑑𝑬𝑫 𝑫𝑶𝑵'𝑻 𝑺𝑬𝑵𝑫 "
        "𝑩𝑰𝑮 𝑴𝑴𝑩 𝑺𝑰𝒁𝑬 𝑨𝑵𝑫 𝑺𝑬𝑵𝑫 𝑶𝑵𝑳𝒀 𝑻𝑨𝑑𝑮𝑬𝑻 𝑾𝑬 𝑪𝑨𝑵 𝑯𝑨𝑵𝑫𝑳𝑬 𝑭𝑨𝑺𝑻 𝑬𝑨𝑺𝑰𝑳𝒀 "
        "𝑷𝑳𝑬𝑨𝑺𝑬 𝑮𝑰𝑽𝑬 𝑹𝑬𝑸𝑼𝑬𝑺𝑻 𝑻𝑶 𝑺𝑻𝑨𝑑𝑻.\n\n"
        "𝑷𝑳𝑬𝑨𝑺𝑬 𝑺𝑯𝑨𝑑𝑬 𝑨𝑵𝑫 𝑮𝑰𝑽𝑬 𝑺𝑼𝑑𝑑𝑶𝑑𝑻."
    )

    keyboard = [
        [
            InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url="https://t.me/your_updates_channel"),
            InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url="https://t.me/your_support_group")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    users = load_users()
    await update.message.reply_text(f"📊 **Bot Status:**\nTotal Registered Users: `{len(users)}`", parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Kishi message ko reply karke `/broadcast` likhein.")
        return

    target_msg = update.message.reply_to_message
    users = load_users()
    
    success = 0
    failed = 0

    await update.message.reply_text(f"📢 Broadcast shuru ho gaya hai `{len(users)}` users ko...")

    for u_id in users:
        try:
            await target_msg.copy(chat_id=u_id)
            success += 1
        except Exception:
            failed += 1

    await update.message.reply_text(f"✅ **Broadcast Done!**\nSuccess: `{success}`\nFailed/Blocked: `{failed}`", parse_mode="Markdown")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)

    url = update.message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return

    status_msg = await update.message.reply_text("Progress Downloading ...📥\n■■■□□□□□□□ 36%")

    is_short = "shorts" in url.lower() or "reel" in url.lower() or "tiktok" in url.lower()

    if is_short:
        format_str = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
    else:
        format_str = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best'

    ydl_opts = {
        'format': format_str,
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("Please wait Uploading...⚡")
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video)

        if os.path.exists(filename):
            os.remove(filename)

        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        await status_msg.edit_text(f" Failed ❌ {str(e)}")

def main():
    if BOT_TOKEN == "8283637087:AAH_q5peDqMMadZhU6zlja21JRq6wpkl-7E" or not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is missing!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("Bot is running successfully with Admin features...")
    app.run_polling()

if __name__ == '__main__':
    main()

