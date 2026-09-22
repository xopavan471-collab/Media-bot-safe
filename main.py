import os
import yt_dlp
import re
import math
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# --- CONFIGURATION ---
BOT_TOKEN = "8283637087:AAFr_dQKWh9XQW1KRw5U4JHI2CD3xrsjGBk"  # Bot Token
ADMIN_ID = 8562470788                         # Telegram User ID (Numeric)

MEDIAFIRE_MAX_SIZE = 400 * 1024 * 1024       # MediaFire limit: 400 MB
SOCIAL_MAX_SIZE = 200 * 1024 * 1024          # YT, IG, FB limit: 200 MB

USERS_FILE = "users.json"
executor = ThreadPoolExecutor(max_workers=4)

# --- USER STORAGE HELPER ---
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_users(users_set):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(list(users_set), f)
    except Exception as e:
        print(f"Error saving users: {e}")

users_set = load_users()

def add_user(user_id):
    if user_id not in users_set:
        users_set.add(user_id)
        save_users(users_set)

def human_readable_size(size_bytes):
    if not size_bytes or size_bytes == 0:
        return "Unknown Size"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

# --- AUTO CLEANUP FUNCTION ---
def safe_remove(filepath):
    """File ko server se turant delete karne ke liye"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️ Successfully deleted from server: {filepath}")
    except Exception as e:
        print(f"⚠️ Cleanup Error: {e}")

# --- COMMAND HANDLERS ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.first_name if user else "User"
    add_user(user.id)
    
    welcome_text = (
        f"𝐖ᴇʟᴄᴏᴍᴇ <b>{user_name}</b> 𝐌ᴇᴅɪᴀ 𝐔ᴘʟᴏᴀᴅᴇʀ 𝐁ᴏᴛ.\n\n"
        "𝐖ᴇ 𝐂ᴀɴ ʜᴇʟᴘ ᴛᴏ 𝐌ᴜʟᴛɪᴘʟᴇ ғᴀsᴛ 𝐏ʀᴏsᴇss ғᴇᴀᴛᴜʀᴇs 𝐀ʀᴇ 𝐀ᴠᴀɪʟᴀʙʟᴇ  Dᴏᴡɴʟᴏᴀᴅ Mᴇᴅɪᴀ ғɪʀᴇ Wɪᴛʜ Fᴀsᴛ\n"
        "𝐉ᴜsᴛ 𝐒ᴇɴᴅ 𝐕ɪᴅᴇᴏ ʟɪɴᴋ, 𝐖ᴇ ᴅɪʀᴇᴄᴛ ᴜᴘʟᴏᴀᴅ ʏᴏᴜʀ ғɪʟᴇ, 𝐕ɪᴅᴇᴏ Sɪᴢᴇ\n"
        "𝐀ʟʟᴏᴡᴇᴅ 𝐃ᴏɴ'ᴛ sᴇɴᴅ 𝐁ɪɢ 𝐌ʙ sɪᴢᴇ,\n"
        "𝐓ᴀʀɢᴇᴛ 𝐖ᴇ ᴄᴀɴ ʜᴀɴᴅʟᴇ ғᴀsᴛ ᴇᴀsɪʟʏ\n"
        "𝐏ʟᴇᴀsᴇ 𝐆ɪᴠᴇ 𝐑ᴇᴏᴜᴇsᴛ ᴛᴏ sᴛᴀʀᴛ.\n\n"
        "𝐏ʟᴇᴀsᴇ 𝐒ʜᴀʀᴇ 𝐀ɴᴅ 𝐆ɪᴠᴇ 𝐒ᴜᴘᴘᴏʀᴛ."
    )

    keyboard = [
        [InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url="https://t.me/zexon_Bot_updates")],
        [
            InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url="https://t.me/zexon_Bot_updates"),
            InlineKeyboardButton("𝐒ʜᴀʀᴇ", url="https://t.me/URL_Save_Bot")
        ],
        [InlineKeyboardButton("𝐃ᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/zexon_x")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=reply_markup)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    total_users = len(users_set)
    status_text = f"<b>Bot Status 📊</b>\n\nTotal Active Users: <b>{total_users}</b>"
    await update.message.reply_text(status_text, parse_mode="HTML")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Kripya kisi message ko reply karke `/broadcast` likhein!")
        return

    reply_msg = update.message.reply_to_message
    total = len(users_set)
    success = 0
    failed = 0

    status_msg = await update.message.reply_text(f"⏳ Broadcasting to {total} users...")

    for u_id in list(users_set):
        try:
            await reply_msg.copy(chat_id=u_id)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"<b>📢 Broadcast Completed!</b>\n\n"
        f"✅ Successful: <b>{success}</b>\n"
        f"❌ Failed/Blocked: <b>{failed}</b>\n"
        f"👥 Total Target: <b>{total}</b>",
        parse_mode="HTML"
    )

# --- MEDIAFIRE EXTRACTION ---
def extract_mediafire_link(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None, None, None
        soup = BeautifulSoup(response.text, "html.parser")
        download_btn = soup.find("a", id="downloadButton")
        if download_btn and download_btn.get("href"):
            direct_link = download_btn["href"]
            
            filename = "downloaded_file"
            filename_div = soup.find("div", class_="filename")
            if filename_div:
                filename = filename_div.text.strip()
            else:
                filename = direct_link.split('/')[-1]

            head_resp = requests.head(direct_link, headers=headers, allow_redirects=True, timeout=10)
            content_length = head_resp.headers.get("content-length")
            file_size = int(content_length) if content_length else 0
            return direct_link, file_size, filename
    except Exception as e:
        print(f"Mediafire Extract Error: {e}")
    return None, None, None


# --- FULLY FIXED YOUTUBE & SOCIAL DOWNLOAD ENGINE ---
def run_yt_dlp_download(url, user_id):
    out_template = f"dl_video_{user_id}_%(id)s.%(ext)s"

    # 1. Direct yt-dlp Bypass using WEB_CREATOR & ANDROID_TESTSUITE
    try:
        common_opts = {
            'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]/best',
            'outtmpl': out_template,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'socket_timeout': 30,
            'retries': 5,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_testsuite', 'web_creator', 'ios'],
                    'skip': ['hls', 'dash']
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/18.11.34 (Linux; U; Android 11; en_US)',
            }
        }

        if os.path.exists('cookies_fixed.txt'):
            common_opts['cookiefile'] = 'cookies_fixed.txt'
        elif os.path.exists('cookies.txt'):
            common_opts['cookiefile'] = 'cookies.txt'

        with yt_dlp.YoutubeDL(common_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not os.path.exists(filename):
                base = os.path.splitext(filename)[0]
                for ext in [".mp4", ".mkv", ".webm", ".3gp"]:
                    if os.path.exists(base + ext):
                        filename = base + ext
                        break

            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                print("✅ Direct yt-dlp Download Success!")
                return filename, os.path.getsize(filename)

    except Exception as e:
        print(f"⚠️ Direct yt-dlp failed ({e}). Switching to Third-Party Proxy Engine...")

    # 2. Public Direct Download Engine Bypass
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.post("https://yt-download-api.vercel.app/api/yt", json={"url": url}, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            dl_link = data.get("url") or data.get("download_url")
            if dl_link:
                filename = f"dl_video_{user_id}_proxy.mp4"
                with requests.get(dl_link, stream=True, timeout=35) as r:
                    r.raise_for_status()
                    with open(filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                if os.path.exists(filename) and os.path.getsize(filename) > 0:
                    return filename, os.path.getsize(filename)
    except Exception as err:
        print(f"Engine 2 Error: {err}")

    # 3. Y2Mate Direct Scraping API Fallback
    try:
        match = re.search(r"(?:v=|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", url)
        if match:
            v_id = match.group(1)
            alt_url = f"https://tube.cadence.moe/latest_version?id={v_id}&itag=18"
            filename = f"dl_video_{user_id}_direct.mp4"
            with requests.get(alt_url, stream=True, timeout=25, headers={"User-Agent": "Mozilla/5.0"}) as r:
                if r.status_code == 200:
                    with open(filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                    if os.path.exists(filename) and os.path.getsize(filename) > 0:
                        print("✅ Public Stream Download Success!")
                        return filename, os.path.getsize(filename)
    except Exception as e:
        print(f"Stream Error: {e}")

    raise Exception("YouTube download restricted on host IP. Kripya thodi der baad check karein.")


# --- MAIN URL PROCESSOR ---
async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    text = update.message.text.strip()

    is_mediafire = "mediafire.com" in text
    is_yt = bool(re.search(r"(youtube\.com|youtu\.be)", text))
    is_ig = "instagram.com" in text
    is_fb = bool(re.search(r"(facebook\.com|fb\.watch)", text))

    if not (is_mediafire or is_yt or is_ig or is_fb):
        await update.message.reply_text("⚠️ Kripya valid MediaFire, YouTube, Instagram ya Facebook link bhejein!")
        return

    status_msg = await update.message.reply_text("𝐏ʀᴏsᴇssɪɴɢ...⏳")
    loop = asyncio.get_running_loop()

    # 1. MEDIAFIRE HANDLING
    if is_mediafire:
        local_filename = None
        try:
            direct_link, file_size, orig_filename = await loop.run_in_executor(executor, extract_mediafire_link, text)
            if not direct_link:
                await status_msg.edit_text("❌ MediaFire link invalid hai ya file expire ho chuki hai.")
                return

            if file_size > MEDIAFIRE_MAX_SIZE:
                size_str = human_readable_size(file_size)
                await status_msg.edit_text(
                    f"⚠️ File size ({size_str}) <b>400 MB limit</b> se bada hai!",
                    parse_mode="HTML"
                )
                return

            local_filename = f"{user_id}_{orig_filename}"
            await status_msg.edit_text(f"𝐅ɪʟᴇ ɴᴀᴍᴇ: <b>{orig_filename}</b> ({human_readable_size(file_size)}). ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...⚡", parse_mode="HTML")

            def download_mf():
                headers = {"User-Agent": "Mozilla/5.0"}
                with requests.get(direct_link, headers=headers, stream=True, timeout=60) as r:
                    r.raise_for_status()
                    with open(local_filename, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)

            await loop.run_in_executor(executor, download_mf)
            await status_msg.edit_text("𝐏ʟᴇᴀsᴇ ᴡᴀɪᴛ ᴜᴘʟᴏᴀᴅɪɴɢ...⚡")
            
            with open(local_filename, "rb") as f:
                await update.message.reply_document(document=f, filename=orig_filename)
            await status_msg.delete()

        except Exception as e:
            await status_msg.edit_text(f"❌ MediaFire Download Error: {str(e)}")
        finally:
            safe_remove(local_filename)

    # 2. YOUTUBE, INSTAGRAM, FACEBOOK HANDLING
    else:
        filename = None
        try:
            await status_msg.edit_text("𝐏ʀᴏɢʀᴇss ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...📥")
            filename, file_size = await loop.run_in_executor(executor, run_yt_dlp_download, text, user_id)

            if file_size > SOCIAL_MAX_SIZE:
                size_str = human_readable_size(file_size)
                await status_msg.edit_text(
                    f"⚠️ Video size ({size_str}) <b>200 MB limit</b> se bada hai.",
                    parse_mode="HTML"
                )
                return

            await status_msg.edit_text("𝐏ʟᴇᴀsᴇ ᴡᴀɪᴛ ᴜᴘʟᴏᴀᴅɪɴɢ...⚡")
            with open(filename, 'rb') as video_file:
                await update.message.reply_video(video=video_file, caption="ᴅᴏᴡɴʟᴏᴀᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ✨")

            await status_msg.delete()

        except Exception as e:
            await status_msg.edit_text(f"❌ Failed to download/send video: {str(e)}")
        finally:
            safe_remove(filename)

# --- MAIN ENGINE ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

    print("Bot is starting under active event loop...")
    print("Bot is successfully running! UI aligned. ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
    
