import os
import sys
import asyncio
import requests
import urllib.request
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import pyromod.listen

# Custom Files
import core as helper
from drm_extractor import generate_drm_keys

# ===== BOT SETUP =====
API_ID = 20807000
API_HASH = 'cde2366a7c61e23f4cb44618cbe6cf70'
BOT_TOKEN = '8564398983:AAGxMpPkmLcgZsPnVzIQzCUIro5KNk76QBw' # अपना असली टोकन यहाँ रखें
OWNER_ID = [5938871512, 890749443] 

bot = Client("ProDownloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# ===== COMMANDS =====
@bot.on_message(filters.command(["start"]) & filters.user(OWNER_ID))
async def start_command(bot: Client, message: Message):
    await message.reply_text(f"**Hello Bruh** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n>> I am Advance TXT Downloader Bot.\n>> Send /txt to start downloading.")

@bot.on_message(filters.command("stop") & filters.user(OWNER_ID))
async def stop_handler(_, m: Message):
    await m.reply_text("🚦**STOPPED & RESTARTING**🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

# ===== MAIN BATCH DOWNLOADER =====
@bot.on_message(filters.command(["txt"]) & filters.user(OWNER_ID))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text("⚡ 𝗦𝗘𝗡𝗗 𝗧𝗫𝗧 𝗙𝗜𝗟𝗘 ⚡")
    input_msg: Message = await bot.listen(editable.chat.id)
    
    if not input_msg.document:
        return await editable.edit("❌ Please send a valid .txt document.")
        
    x = await input_msg.download()
    await input_msg.delete(True)
    file_name, _ = os.path.splitext(os.path.basename(x))
    
    pdf_count, img_count, zip_count, video_count = 0, 0, 0, 0
    
    try:    
        with open(x, "r", encoding="utf-8") as f:
            content = f.read().splitlines()
        
        links = []
        for i in content:
            if "://" in i:
                url = i.split("://", 1)[1]
                full_url = i.split("://", 1)
                links.append(full_url)
                if ".pdf" in url: pdf_count += 1
                elif url.endswith((".png", ".jpeg", ".jpg")): img_count += 1
                elif ".zip" in url: zip_count += 1
                else: video_count += 1
        os.remove(x)
    except Exception as e:
        await editable.edit(f"😶 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗙𝗶𝗹𝗲 𝗜𝗻𝗽𝘂𝘁 😶\nError: {e}")
        if os.path.exists(x): os.remove(x)
        return
   
    await editable.edit(f"`𝗧𝗼𝘁𝗮𝗹 🔗 𝗟𝗶𝗻𝗸𝘀 𝗙𝗼𝘂𝗻𝗱 𝗔𝗿𝗲 {len(links)}\n\n🔹Img : {img_count}  🔹Pdf : {pdf_count}\n🔹Zip : {zip_count}  🔹Video : {video_count}\n\n𝗦𝗲𝗻𝗱 𝗙𝗿𝗼𝗺 𝗪𝗵𝗲𝗿𝗲 𝗬𝗼𝘂 𝗪𝗮𝗻𝘁 𝗧𝗼 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 (Index)`")
    input0: Message = await bot.listen(editable.chat.id)
    try: count = int(input0.text)
    except: count = 1
    await input0.delete(True)

    await editable.edit("📚 𝗘𝗻𝘁𝗲𝗿 𝗬𝗼𝘂𝗿 𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 📚\n\n🦠 𝗦𝗲𝗻𝗱 `1` 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗗𝗲𝗳𝗮𝘂𝗹𝘁 🦠")
    input1: Message = await bot.listen(editable.chat.id)
    b_name = file_name if input1.text == '1' else input1.text
    await input1.delete(True)
    
    await editable.edit("**📸 𝗘𝗻𝘁𝗲𝗿 𝗥𝗲𝘀𝗼𝗹𝘂𝘁𝗶𝗼𝗻 📸**\n➤ `144`, `240`, `360`, `480`, `720`, `1080`")
    input2: Message = await bot.listen(editable.chat.id)
    res_dict = {"144": "256x144", "240": "426x240", "360": "640x360", "480": "854x480", "720": "1280x720", "1080": "1920x1080"}
    raw_res = input2.text if input2.text in res_dict else "720"
    await input2.delete(True)

    await editable.edit("📛 𝗘𝗻𝘁𝗲𝗿 𝗬𝗼𝘂𝗿 𝗡𝗮𝗺𝗲 (Caption) 📛\n\n🐥 𝗦𝗲𝗻𝗱 `1` 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗗𝗲𝗳𝗮𝘂𝗹𝘁 🐥")
    input3: Message = await bot.listen(editable.chat.id)
    CR = "Group Admin:)™" if input3.text == '1' else input3.text
    await input3.delete(True)
   
    await editable.edit("**𝗘𝗻𝘁𝗲𝗿 𝗪𝗼𝗿𝗸𝗶𝗻𝗴 𝗧𝗼𝗸𝗲𝗻 (Classplus)**\nSend `1` if no DRM videos in this list.")
    input4: Message = await bot.listen(editable.chat.id)
    cp_token = input4.text
    await input4.delete(True)

    await editable.edit("𝗡𝗼𝘄 𝗦𝗲𝗻𝗱 𝗧𝗵𝗲 𝗧𝗵𝘂𝗺𝗯 𝗨𝗿𝗹 (Eg: https://envs.sh/Hlb.jpg)\n𝗢𝗿 𝗜𝗳 𝗗𝗼𝗻'𝘁 𝗪𝗮𝗻𝘁 𝗧𝗵𝗨𝗺𝗯𝗻𝗮𝗶𝗹 𝗦𝗲𝗻𝗱 = `no`")
    input6 = await bot.listen(editable.chat.id)
    thumb_url = input6.text
    await input6.delete(True)
    await editable.delete()

    if thumb_url.startswith("http"):
        try:
            urllib.request.urlretrieve(thumb_url, "thumb.jpg")
            thumb = "thumb.jpg"
        except:
            thumb = "no"
    else:
        thumb = "no"

    failed_count = 0

    # ===== DOWNLOADING LOOP =====
    for i in range(count - 1, len(links)):
        V = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
        url = "https://" + V
        
        name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").strip()
        safe_name = name1[:60]
        name = f'{str(i+1).zfill(3)}) {safe_name}'
        
        cc = f'**╭── ⋆⋅☆⋅⋆ ──╮**\n✦ **{str(i+1).zfill(3)}** ✦\n**╰── ⋆⋅☆⋅⋆ ──╯**\n\n🎭 **Title:** `{safe_name}`\n🖥️ **Resolution:** [{raw_res}p]\n📘 **Course:** `{b_name}`\n🚀 **Extracted By:** `{CR}`'
        Show = f"✈️ 𝗣𝗥𝗢𝗚𝗥𝗘𝗦𝗦 ✈️\n\n┠ 📈 Total Links = {len(links)}\n┠ 💥 Currently On = {str(i+1).zfill(3)}\n\n**📩 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚 📩**\n\n**🧚🏻‍♂️ Title** : {name}\n├── **Resolution** : {raw_res}p\n├── **Extracted By** : {CR}"
        
        try:
            # 1. IMAGE DOWNLOADER
            if any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png"]):
                prog = await m.reply_text(Show + "\n\n🖼️ **Downloading Image...**")
                urllib.request.urlretrieve(url, f"{name}.jpg")
                await bot.send_photo(chat_id=m.chat.id, photo=f'{name}.jpg', caption=cc)
                await prog.delete(True)
                os.remove(f'{name}.jpg')
                await asyncio.sleep(1)
                continue

            # 2. PDF DOWNLOADER (Includes direct Encrypted PDFs)
            elif ".pdf" in url:
                prog = await m.reply_text(Show + "\n\n📄 **Downloading PDF...**")
                cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                os.system(cmd)
                if os.path.exists(f'{name}.pdf'):
                    await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc)
                    os.remove(f'{name}.pdf')
                await prog.delete(True)
                await asyncio.sleep(1)
                continue

            # 3. CLASSPLUS / DRM LOGIC
            elif "classplus" in url or "cpvod" in url:
                clean_url = url.replace("master.m3u8", "master.mpd").replace("?quality=auto", "")
                
                prog = await m.reply_text(Show + "\n\n🔐 **DRM Decryption Started...**")
                
                # Passing the user-provided Token directly
                drm_data = generate_drm_keys(clean_url, cp_token)
                
                if "error" in drm_data:
                    await prog.edit(f"❌ **DRM Error:** `{drm_data['error']}`\n\n⚠️ Ensure your Classplus Token is valid and fresh!")
                    failed_count += 1
                    continue
                
                mpd_link = drm_data["mpd_url"]
                keys_list = drm_data["keys"]
                keys_string = " ".join([f"--key {k}" for k in keys_list])
                
                # Calling your helper file's decrypt & merge function
                res_file = await helper.decrypt_and_merge_video(mpd_link, keys_string, "./downloads/", name, raw_res)
                await prog.delete(True)
                await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
                await asyncio.sleep(1)
                continue

            # 4. NORMAL VIDEO (.m3u8 / YouTube etc.)
            else:
                prog = await m.reply_text(Show + "\n\n🎥 **Downloading Video...**")
                
                if "youtu" in url:
                    ytf = f"b[height<={raw_res}][ext=mp4]/bv[height<={raw_res}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
                else:
                    ytf = f"b[height<={raw_res}]/bv[height<={raw_res}]+ba/b/bv+ba"
                
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
                
                res_file = await helper.download_video(url, cmd, name)
                await prog.delete(True)
                await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
                await asyncio.sleep(1)

        except FloodWait as e:
            await m.reply_text(f"FloodWait! Sleeping for {e.value}s")
            await asyncio.sleep(e.value)
            continue
            
        except Exception as e:
            await m.reply_text(f'‼️ 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗙𝗮𝗶𝗹𝗲𝗱 ‼️\n\n📝 𝗡𝗮𝗺𝗲 » `{name}`\nError: {str(e)[:100]}')
            failed_count += 1
            continue   

    await m.reply_text(f"`✨ 𝗕𝗔𝗧𝗖𝗛 𝗦𝗨𝗠𝗠𝗔𝗥𝗬 ✨\n\n"
                       f"📚 𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 » {b_name}\n"
                       f"✨ 𝗧𝗫𝗧 𝗟𝗶𝗻𝗸𝘀 : {len(links)}\n"
                       f"🔹 𝗙𝗮𝗶𝗹𝗲𝗱 𝗨𝗿𝗹 » {failed_count}\n\n"
                       f"✅ 𝗦𝗧𝗔𝗧𝗨𝗦 » 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗`")

if __name__ == "__main__":
    if not os.path.exists("WVDs"):
        os.makedirs("WVDs")
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    bot.run()
