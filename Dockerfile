# Python का बेस इमेज
FROM python:3.10-slim

# FFmpeg और अन्य जरूरी टूल्स इंस्टॉल करें
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# N_m3u8DL-RE डाउनलोड और इंस्टॉल करें
RUN wget https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v0.2.0-beta/N_m3u8DL-RE_Beta_linux-x64_20230628.tar.gz \
    && tar -zxvf N_m3u8DL-RE_Beta_linux-x64_20230628.tar.gz \
    && mv N_m3u8DL-RE_Beta_linux-x64/N_m3u8DL-RE /usr/local/bin/ \
    && chmod +x /usr/local/bin/N_m3u8DL-RE \
    && rm -rf N_m3u8DL-RE_Beta_linux-x64*

# वर्किंग डायरेक्टरी सेट करें
WORKDIR /app
COPY . /app

# Python पैकेज इंस्टॉल करें (yt-dlp इसमें आ जाएगा)
RUN pip install --no-cache-dir -r requirements.txt

# बॉट को चालू करें
CMD ["python", "bot.py"]
