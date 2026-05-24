import os
import time
import math
import asyncio

# 1. Normal Video Downloader
async def download_video(url, cmd, name):
    """yt-dlp का उपयोग करके साधारण वीडियो डाउनलोड करता है"""
    # Background में command रन करने के लिए
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    
    # फाइल उसी फोल्डर में name.mp4 के नाम से सेव होगी
    return f"{name}.mp4"

# 2. DRM Video Decryptor & Merger
async def decrypt_and_merge_video(mpd_link, keys_string, download_dir, name, raw_res):
    """N_m3u8DL-RE का उपयोग करके DRM वीडियो डाउनलोड और डिक्रिप्ट करता है"""
    
    # अगर downloads फोल्डर नहीं है तो बना ले
    os.makedirs(download_dir, exist_ok=True)
    
    # N_m3u8DL-RE कमांड
    cmd = f'N_m3u8DL-RE "{mpd_link}" {keys_string} -M format=mp4 --save-name "{name}" --save-dir "{download_dir}"'
    
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    
    # फाइनल फाइल का पाथ रिटर्न करें
    return os.path.join(download_dir, f"{name}.mp4")

# 3. Telegram Upload Progress Bar
async def progress_bar(current, total, msg, start_time):
    """टेलीग्राम पर सुंदर प्रोग्रेस बार दिखाने के लिए"""
    now = time.time()
    diff = now - start_time
    
    # हर 5 सेकंड में प्रोग्रेस बार अपडेट करें ताकि Telegram का FloodWait न आए
    if round(diff % 5.0) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        
        progress = "[{0}{1}] \n**Progress**: {2}%\n".format(
            ''.join(["█" for _ in range(math.floor(percentage / 5))]),
            ''.join(["░" for _ in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2)
        )
        
        try:
            await msg.edit(
                f"🚀 **Uploading to Telegram...**\n\n{progress}"
            )
        except:
            pass # Message edit limit hit होने पर इग्नोर करें

# 4. Sender & File Cleanup
async def send_vid(bot, m, cc, res_file, thumb, name, prog):
    """टेलीग्राम पर वीडियो भेजता है और सर्वर से फाइल को डिलीट करता है"""
    
    if not os.path.exists(res_file):
        await prog.edit(f"❌ **Error:** Video file `{name}` not found after processing.")
        return

    await prog.edit("🚀 **Starting Upload...**")
    start_time = time.time()
    
    try:
        # अगर Thumbnail नहीं है
        if thumb == "no" or not os.path.exists(thumb):
            await bot.send_video(
                chat_id=m.chat.id,
                video=res_file,
                caption=cc,
                supports_streaming=True,
                progress=progress_bar,
                progress_args=(prog, start_time)
            )
        # अगर Thumbnail मौजूद है
        else:
            await bot.send_video(
                chat_id=m.chat.id,
                video=res_file,
                caption=cc,
                thumb=thumb,
                supports_streaming=True,
                progress=progress_bar,
                progress_args=(prog, start_time)
            )
        await prog.delete()
        
    except Exception as e:
        await prog.edit(f"❌ **Upload Failed:** {str(e)[:100]}")
        
    finally:
        # 🧹 सर्वर की स्टोरेज बचाने के लिए वीडियो सेंड होने के बाद उसे डिलीट कर दें
        if os.path.exists(res_file):
            os.remove(res_file)
