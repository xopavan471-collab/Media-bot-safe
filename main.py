import os
import asyncio
import logging
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = ("8283637087:AAGYwNrjrCd216-K_Z0h2PTn6TtisKnKm6A")
ADMIN_ID = 8562470788  # ⚠️ Yahan apni Telegram User ID daalein (numbers me)

USERS_FILE = "users.txt"

def add_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_all_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def get_total_users():
    return len(get_all_users())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Save user to system
    add_user(user_id)

    welcome_text = (
        f"𝐇ᴇʏ <b>{user_name}</b> 𝐖ᴇʟᴄᴏᴍᴇ ᴛᴏ 𝐃ᴏᴡɴʟᴏᴀᴅᴇʀ 𝐁ᴏᴛ.\n\n"
        f"𝐈 𝐀ᴍ 𝐔𝐑L 𝐕ɪᴅᴇᴏ 𝐃ᴏᴡɴʟᴏᴀᴅᴇʀ ᴡɪᴛʜ 𝐌ᴜʟᴛɪᴘʟᴇ ғᴀsᴛ ᴘʀᴏsᴇss ғᴇᴀᴛᴜʀᴇs 𝐀ʀᴇ 𝐀ᴠᴀɪʟᴀʙʟᴇ "
        f"ᴛᴏ 𝐃ᴏᴡɴʟᴏᴀᴅ \"𝐘ᴏᴜ ᴛᴜʙᴇ 𝐈ɴsᴛᴀɢʀᴀᴍ Fᴀᴄᴇʙᴏᴏᴋ\" 𝐕ɪᴅᴇᴏs 𝐀ɴᴅ ᴄᴀɴ 𝐀ʟᴡᴀʏs 𝐇ᴇʟᴘ ᴛʜɪs "
        f"𝐈F 𝐘ᴏᴜ 𝐑ᴇᴀᴅ𝐘 ᴛᴏ 𝐃ᴏᴡɴʟᴏᴀᴅ 𝐒ᴇɴᴅ Lɪɴᴋ, 𝐖ᴇ 𝐃ɪʀᴇᴄᴛ 𝐔ᴘʟᴏᴀᴅ ʏᴏᴜʀ 𝐕ɪᴅᴇᴏ, 𝐏ʟᴇᴀsᴇ 𝐆ɪᴠᴇ ᴍᴇ 𝐑ᴇᴏᴜᴇsᴛ ᴛᴏ sᴛᴀʀᴛ\n\n"
        f"𝐏ʟᴇᴀsᴇ 𝐒ʜᴀʀᴇ 𝐀ɴᴅ 𝐆ɪᴠᴇ 𝐒ᴜᴘᴘᴏʀᴛ."
    )

    keyboard = [
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/your_channel"),
            InlineKeyboardButton("💬 Support", url="https://t.me/your_group")
        ],
        [
            InlineKeyboardButton("ℹ️ Help / How to Use", callback_data="help_info")
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/your_username"),
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_start")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Yeh command sirf Admin ke liye hai.")
        return
    
    total = get_total_users()
    await update.message.reply_text(f"📊 <b>Bot Users Statistics:</b>\n\n👤 Total Users: <b>{total}</b>", parse_mode='HTML')

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Yeh command sirf Admin ke liye hai.")
        return

    reply = update.message.reply_to_message
    broadcast_text = " ".join(context.args)

    if not reply and not broadcast_text:
        await update.message.reply_text(
            "⚠️ <b>Kaise use karein:</b>\n\n"
            "1. <code>/broadcast Aapka message yahan</code>\n"
            "2. Ya kisi photo/video/message ko reply karke <code>/broadcast</code> likhein.",
            parse_mode='HTML'
        )
        return

    users = get_all_users()
    if not users:
        await update.message.reply_text("❌ Koi user database me nahi hai.")
        return

    status_msg = await update.message.reply_text(f"🚀 Broadcast shuru ho raha hai... (Total Users: {len(users)})")

    success = 0
    failed = 0

    for u_id in users:
        try:
            if reply:
                await reply.copy(chat_id=int(u_id))
            else:
                await context.bot.send_message(chat_id=int(u_id), text=broadcast_text, parse_mode='HTML')
            success += 1
            await asyncio.sleep(0.05)  # Telegram rate limit safety delay
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"✅ <b>Broadcast Completed!</b>\n\n"
        f"🟢 Successful: <b>{success}</b>\n"
        f"🔴 Failed / Blocked: <b>{failed}</b>\n"
        f"📊 Total Users: <b>{len(users)}</b>",
        parse_mode='HTML'
    )

async def notify_restart(app):
    try:
        await app.bot.send_message(chat_id=ADMIN_ID, text="🤖 <b>Bot has been Restarted / Deployed successfully!</b>", parse_mode='HTML')
    except Exception as e:
        logging.error(f"Could not send restart alert to admin: {e}")

def generate_progress_bar(percent):
    filled_length = int(10 * percent // 100)
    bar = '▣' * filled_length + '▢' * (10 - filled_length)
    return bar

def format_bytes(bytes_val):
    if not bytes_val:
        return "0.0 MB"
    mb = bytes_val / (1024 * 1024)
    return f"{mb:.1f} MB"

def make_progress_hook(loop, bot, chat_id, message_id):
    last_text = {"text": ""}

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed', 0) or 0
            eta = d.get('eta', 0) or 0

            percent = int(downloaded / total * 100) if total > 0 else 0
            bar = generate_progress_bar(percent)

            speed_str = f"{speed / (1024 * 1024):.1f} MB/s" if speed else "0.0 MB/s"
            size_str = f"{format_bytes(downloaded)} / {format_bytes(total)}"
            eta_str = f"{eta}s" if eta else "0s"

            text = (
                f"𝐒ᴛᴀᴛᴜs 𝐃ᴏᴡɴʟᴏᴀᴅ :\n"
                f"{bar} {percent} %\n"
                f"ꜱᴘᴇᴇᴅ : {speed_str}\n"
                f"ꜱɪᴢᴇ : {size_str}\n"
                f"ᴇᴛᴀ : {eta_str}"
            )

            if text != last_text["text"]:
                last_text["text"] = text
                asyncio.run_coroutine_threadsafe(
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text),
                    loop
                )
    return progress_hook

def download_video(url, download_path, loop, bot, chat_id, message_id):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [make_progress_hook(loop, bot, chat_id, message_id)],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)

    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("Kripya ek valid video URL (YouTube, Instagram, or Facebook) bhejein.")
        return

    init_text = (
        "𝐒ᴛᴀᴛᴜs 𝐃ᴏᴡɴʟᴏᴀᴅ :\n"
        "▢▢▢▢▢▢▢▢▢▢ 0 %\n"
        "ꜱᴘᴇᴇᴅ : 0.0 MB/s\n"
        "ꜱɪᴢᴇ : 0.0 MB / 0.0 MB\n"
        "ᴇᴛᴀ : 0s"
    )
    status_msg = await update.message.reply_text(init_text)

    download_dir = "downloads"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    try:
        loop = asyncio.get_running_loop()
        file_path = await loop.run_in_executor(
            None, 
            download_video, 
            url, 
            download_dir, 
            loop, 
            context.bot, 
            update.effective_chat.id, 
            status_msg.message_id
        )

        last_upload_text = {"text": ""}
        async def upload_progress(current, total):
            percent = int((current / total) * 100) if total > 0 else 0
            bar = generate_progress_bar(percent)
            size_str = f"{format_bytes(current)} / {format_bytes(total)}"
            
            text = (
                f"𝐒ᴛᴀᴛᴜs 𝐔ᴘʟᴏᴀᴅ :\n"
                f"{bar} {percent} %\n"
                f"ꜱɪᴢᴇ : {size_str}"
            )
            
            if text != last_upload_text["text"]:
                last_upload_text["text"] = text
                try:
                    await status_msg.edit_text(text)
                except Exception:
                    pass

        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="✅ Done! Downloaded successfully.",
                write_timeout=300,
                read_timeout=300,
                progress=upload_progress
            )

        await status_msg.delete()

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        logging.error(f"Error handling video download: {e}")
        await status_msg.edit_text("❌ Process fail ho gaya! Link check karein ya thodi der baad try karein.")

async def post_init(app):
    await notify_restart(app)

def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable set nahi hai.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
