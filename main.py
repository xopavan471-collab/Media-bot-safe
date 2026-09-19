import os
import json
import time
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram Bot Token yahan daalein
BOT_TOKEN = "8283637087:AAGYwNrjrCd216-K_Z0h2PTn6TtisKnKm6A"
def save_user(user_id):
    file = "users.json"
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)
    with open(file, "r") as f:
        users = json.load(f)
    if user_id not in users:
        users.append(user_id)
        with open(file, "w") as f:
            json.dump(users, f)
        return True
    return False

def humanbytes(size):
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    dic_power_ten = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + dic_power_ten[n] + 'B'

def time_formatter(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + \
        ((str(hours) + "ʜ, ") if hours else "") + \
        ((str(minutes) + "ᴍ, ") if minutes else "") + \
        ((str(seconds) + "ꜱ") if seconds else "")
    return tmp if tmp else "𝟶 ꜱ"

def make_progress_bar(percentage):
    completed = int(percentage / 6.25)  # Total 16 dibbi (▣ / ▢)
    return "▣" * completed + "▢" * (16 - completed)
async def total_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_ID = 8562470788  # pehle isko apni ID se badal dega
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text(f"Aap admin nahi ho! Aapki ID hai: {user_id}\nIsko code me ADMIN_ID me daal do.")
        return

    try:
        with open("users.json", "r") as f:
            users = json.load(f)
        await update.message.reply_text(f"📊 Total Users: {len(users)}")
    except:
        await update.message.reply_text("Abhi tak koi user nahi hai!")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name.upper() if update.effective_user else "USER"
    user_id = update.effective_user.id
    save_user(user_id)
    
    caption_text = (
        f"𝐇ᴇʟʟᴏ {user_name} 𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ 𝐔𝐑𝐋 𝐔ᴘʟᴏᴀᴅᴇʀ 𝐁ᴏᴛ.\n\n"
        "𝐈 𝐀ᴍ 𝐔𝐑𝐋 𝐔ᴘʟᴏᴀᴅᴇʀ 𝐀ᴅᴠᴀɴᴄᴇ 𝐁ᴏᴛ. 𝐖ᴇ 𝐂ᴀɴ 𝐇ᴇʟᴘ 𝐀ɴᴅ 𝐌ᴜʟᴛɪᴘʟᴇ 𝐅ᴀsᴛ 𝐏ʀᴏsᴇss "
        "𝐅ᴇᴀᴛᴜʀᴇs 𝐀ʀᴇ 𝐀ᴠᴀɪʟᴀʙʟᴇ 𝐓ᴏ 𝐃ᴏᴡɴʟᴏᴀᴅ \"𝐘ᴏᴜ 𝐓ᴜʙᴇ 𝐈ɴsᴛᴀɢʀᴀᴍ 𝐅ᴀᴄᴇʙᴏᴏᴋ 𝐕ɪᴅᴇᴏ. "
        "𝐍ᴏ 𝐋ɪᴍɪᴛ 𝐔ɴʟɪᴍɪᴛᴇᴅ 𝐉ᴜsᴛ 𝐒ᴇɴᴅ 𝐌ᴇ 𝐘ᴏᴜʀ 𝐋ɪɴᴋ, 𝐖ᴇ 𝐃ɪʀᴇᴄᴛ 𝐔ᴘʟᴏᴀᴅ 𝐘ᴏᴜʀ 𝐕ɪᴅᴇᴏ, "
        "𝐅ɪʀsᴛ 𝐆ɪᴠᴇ 𝐌ᴇ 𝐑ᴇᴏᴜᴇsᴛ 𝐓ᴏ 𝐒ᴛᴀʀᴛ.\n\n"
        "𝐏ʟᴇᴀsᴇ 𝐒ʜᴀʀᴇ 𝐀ɴᴅ 𝐆ɪᴠᴇ 𝐒ᴜᴘᴘᴏʀᴛ."
    )
    
    keyboard = [
        [InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url="https://t.me/zexon_Bot_updates")],
        [
            InlineKeyboardButton("𝐒ʜᴀʀᴇ", url="https://t.me/URL_Save_Bot"),
            InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url="https://whatsapp.com/channel/0029VbClgKEEVccGKahXmw3X")
        ],
        [InlineKeyboardButton("𝐇ᴇʟᴘ", url="https://t.me/zexon_x")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=caption_text, 
        parse_mode='HTML', 
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        return

    status_msg = await update.message.reply_text("𝐏ʀᴏsᴇssɪɴɢ...⚡️")
    last_update = [0]
    loop = asyncio.get_running_loop()

    # --- DOWNLOADING PROGRESS HOOK ---
    def yt_dlp_hook(d):
        if d['status'] == 'downloading':
            now = time.time()
            if now - last_update[0] < 2:
                return
            last_update[0] = now

            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            speed = d.get('speed', 0) or 0
            eta = d.get('eta', 0) or 0

            if total > 0:
                percentage = (downloaded / total) * 100
                bar = make_progress_bar(percentage)
                text = (
                    "𝐒ᴛᴀᴛᴜs 𝐃ᴏᴡɴʟᴏᴀᴅɪɴɢ:\n\n"
                    f"{bar}\n\n"
                    f"  𝐒ɪᴢᴇ : {humanbytes(downloaded)} | {humanbytes(total)}\n"
                    f"  𝐃ᴏɴᴇ : {round(percentage, 2)}%\n"
                    f"  𝐒ᴘᴇᴇᴅ : {humanbytes(speed)}/s\n"
                    f"  𝐄ᴛᴀ : {time_formatter(eta)}"
                )
                asyncio.run_coroutine_threadsafe(
                    status_msg.edit_text(text, parse_mode='HTML'), loop
                )

    if "youtube.com" in url or "youtu.be" in url:
        if "shorts" in url:
            format_opt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
        else:
            format_opt = "bestvideo[height<=360]+bestaudio/best[height<=360]/best"
    else:
        format_opt = "bestvideo+bestaudio/best"

        ydl_opts = {
        'format': format_opt,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web', 'ios']
            },
            'instagram': {
                'api_version': 'v1'
            }
        },
        'noplaylist': True
    }

    try:
        def download_file():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp4'):
                    filename = os.path.splitext(filename)[0] + '.mp4'
                return filename

        filename = await loop.run_in_executor(None, download_file)
        file_size = os.path.getsize(filename)

        # --- UPLOADING SIMULATED ANIMATED DIBBI BAR ---
        async def update_upload_status():
            for pct in range(10, 100, 20):
                bar = make_progress_bar(pct)
                text = (
                    "𝐒ᴛᴀᴛᴜs 𝐔ᴘʟᴏᴀᴅɪɴɢ:\n\n"
                    f"{bar}\n\n"
                    f"  𝐒ɪᴢᴇ : {humanbytes(file_size * pct / 100)} | {humanbytes(file_size)}\n"
                    f"  𝐃ᴏɴᴇ : {pct}%\n"
                    f"  𝐄ᴛᴀ : 𝟶 ꜱ"
                )
                try:
                    await status_msg.edit_text(text, parse_mode='HTML')
                except Exception:
                    pass
                await asyncio.sleep(1.4)

        upload_task = asyncio.create_task(update_upload_status())

        with open(filename, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="ᴅᴏᴡɴʟᴏᴀᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ✨",
                write_timeout=600,
                read_timeout=600
            )

        upload_task.cancel()
        await status_msg.delete()

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await status_msg.edit_text(f"Failed to process video.\nError: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", total_users))
    app.add_handler(CommandHandler("status", total_users))
    app.add_handler(CommandHandler("user", total_users))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("Bot is running perfectly...")
    app.run_polling()

if __name__ == '__main__':
    main()
