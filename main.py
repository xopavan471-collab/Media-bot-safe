import os
import re
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import yt_dlp

# Logging Configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Configuration Variables
BOT_TOKEN = "8283637087:AAH_q5peDqMMadZhU6zlja21JRq6wpkl-7E"  # Apna Telegram Bot Token yahan daalein
ADMIN_ID = 8562470788                # Apna numeric Telegram User ID yahan daalein

USER_FILE = "users.txt"

# Helper Functions for Managing Users
def get_users():
    if not os.path.exists(USER_FILE):
        return set()
    with open(USER_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def add_user(user_id):
    users = get_users()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")

# Custom Dynamic Progress Bar Generator
def make_progress_bar(percent):
    filled = int(percent // 10)
    empty = 10 - filled
    return "■" * filled + "□" * empty + f" {percent:.1f}%"

# Command: /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    bot_username = context.bot.username
    add_user(user_id)
    
    # Aapka Custom Welcome Text
    welcome_text = (
        f"𝐖ᴇʟᴄᴏᴍᴇ <b>{user_name}</b> 𝐌ᴇᴅɪᴀ 𝐔ᴘʟᴏᴀᴅᴇʀ 𝐁ᴏᴛ.\n\n"
        "𝐖ᴇ 𝐂ᴀɴ ʜᴇʟᴘ ᴛᴏ 𝐌ᴜʟᴛɪᴘʟᴇ ғᴀsᴛ 𝐏ʀᴏsᴇss ғᴇᴀᴛᴜʀᴇs 𝐀ʀᴇ 𝐀ᴠᴀɪʟᴀᴠʟᴇ  Dᴏᴡɴʟᴏᴀᴅ Mᴇᴅɪᴀ ғɪʀᴇ Wɪᴛʜ Fᴀsᴛ\n"
        "𝐉ᴜsᴛ 𝐒ᴇɴᴅ 𝐕ɪᴅᴇᴏ ʟɪɴᴋ, 𝐖ᴇ ᴅɪʀᴇᴄᴛ ᴜᴘʟᴏᴀᴅ ʏᴏᴜʀ ғɪʟᴇ, 𝐕ɪᴅᴇᴏ Sɪᴢᴇ\n"
        "𝐀ʟʟᴏᴡᴇᴅ 𝐃ᴏɴ'ᴛ sᴇɴᴅ 𝐁ɪɢ 𝐌ʙ sɪᴢᴇ 𝐀ɴᴅ sᴇɴᴅ ᴏɴʟʏ\n"
        "𝐓ᴀʀɢᴇᴛ 𝐖ᴇ ᴄᴀɴ ʜᴀɴᴅʟᴇ ғᴀsᴛ ᴇᴀsɪʟʏ\n"
        "𝐏ʟᴇᴀsᴇ 𝐆ɪᴠᴇ 𝐑ᴇᴏᴜᴇsᴛ ᴛᴏ sᴛᴀʀᴛ.\n\n"
        "𝐏ʟᴇᴀsᴇ 𝐒ʜᴀʀᴇ 𝐀ɴᴅ 𝐆ɪᴠᴇ 𝐒ᴜᴘᴘᴏʀᴛ."
    )
    
    # 4 Requested Buttons: Updates, Support, Share, Help
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}&text=Check%20out%20this%20awesome%20Media%20Downloader%20Bot!"
    
    keyboard = [
        [
            InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url="https://t.me/telegram"),
            InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url="https://t.me/telegram")
        ],
        [
            InlineKeyboardButton("𝐒ʜᴀʀᴇ", url=share_url),
            InlineKeyboardButton("𝐇ᴇʟᴘ", callback_data="help_info")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=reply_markup)

# Callback Handler for Inline Buttons
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "help_info":
        help_text = (
            "<b>💡 How To Use:</b>\n\n"
            "1. Copy video link from YouTube, Instagram, or Facebook.\n"
            "2. Send link here in this chat.\n"
            "3. Wait a few seconds for high-speed download & upload!\n\n"
            "<i>Note: Big files might fail due to server limits.</i>"
        )
        await query.edit_message_text(help_text, parse_mode="HTML")

# Command: /status (Admin Only)
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    users = get_users()
    await update.message.reply_text(f"📊 <b>Bot Status:</b>\n\nTotal Registered Users: <code>{len(users)}</code>", parse_mode="HTML")

# Command: /broadcast (Admin Only)
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Command Format: <code>/broadcast Message Text</code>", parse_mode="HTML")
        return
    
    msg_to_send = " ".join(context.args)
    users = get_users()
    sent_count = 0
    failed_count = 0
    
    status_msg = await update.message.reply_text("🚀 Broadcast starting...")
    
    for uid in users:
        try:
            await context.bot.send_message(chat_id=int(uid), text=msg_to_send)
            sent_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed_count += 1
            
    await status_msg.edit_text(
        f"✅ <b>Broadcast Completed!</b>\n\n"
        f"<b>Success:</b> {sent_count}\n"
        f"<b>Failed:</b> {failed_count}",
        parse_mode="HTML"
    )

# Media Downloader Handler
async def process_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("❌ Kripya valid HTTP/HTTPS video URL bhejein.")
        return

    status_msg = await update.message.reply_text("Processing link... 📥")
    loop = asyncio.get_running_loop()
    last_update_time = [0]

    # Progress Callback Function for yt-dlp
    def yt_progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = (downloaded / total) * 100
                import time
                current_time = time.time()
                if current_time - last_update_time[0] > 2.0:
                    last_update_time[0] = current_time
                    bar = make_progress_bar(percent)
                    text = f"Downloading... 📥\n{bar}"
                    asyncio.run_coroutine_threadsafe(
                        status_msg.edit_text(text), loop
                    )

    output_filename = f"video_{update.effective_user.id}.mp4"

    # Video type Check (Shorts / Reels vs Long Video)
is_short_video = "shorts" in url.lower() or "reel" in url.lower()

# Dynamic Format Selection
if is_short_video:
    # Short Videos (Reels / Shorts) -> Up to 1080p
    video_format = 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]/best'
else:
    # Long Videos -> Up to 360p
    video_format = 'bestvideo[ext=mp4][height<=360]+bestaudio[ext=m4a]/best[ext=mp4][height<=360]/best'

# Youtube & Bot Anti-Block Options
ydl_opts = {
    'format': video_format,
    'outtmpl': output_filename,
    'quiet': True,
    'no_warnings': True,
    'progress_hooks': [yt_progress_hook],
    'extractor_args': {
        'youtube': {
            'player_client': ['ios', 'android', 'web'],
            'player_skip': ['webpage', 'configs']
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
        'Accept-Language': 'en-US,en;q=0.9',
    },


    try:
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, download)
        await status_msg.edit_text("Uploading... 📤\n■■■■■■■■■■ 100%")

        with open(output_filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="✅ Video uploaded successfully!"
            )
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error processing URL: {e}")
        await status_msg.edit_text(f"❌ Download Failed!\nError: {str(e)[:100]}")
    
    finally:
        if os.path.exists(output_filename):
            try:
                os.remove(output_filename)
            except Exception:
                pass

# Main Runner
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_media))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

