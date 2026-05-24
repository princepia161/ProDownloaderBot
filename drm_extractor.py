import os
import glob
import base64
import json
from bs4 import BeautifulSoup
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
from curl_cffi import requests as spoof_requests

def wvd_check():
    try:
        return glob.glob(f'{os.getcwd()}/WVDs/*.wvd')[0]
    except IndexError:
        raise FileNotFoundError("WVD file not found in 'WVDs' folder. Please upload it.")

# 🧠 Token के अंदर से Fingerprint निकालने का लॉजिक
def extract_fingerprint(token):
    try:
        payload = token.split('.')[1]
        payload += '=' * (-len(payload) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload).decode('utf-8'))
        return decoded.get('fingerprintId', '')
    except:
        return ''

def generate_drm_keys(video_url, user_token):
    wvd = wvd_check()
    clean_token = ''.join(user_token.split())
    
    # फिंगरप्रिंट एक्सट्रैक्ट करना
    fingerprint = extract_fingerprint(clean_token)

    headers = {
        'x-access-token': clean_token,
        'fingerprintId': fingerprint, # 👈 यह Header Server को ब्लॉक करने से रोकेगा
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://web.classplusapp.com',
        'Referer': 'https://web.classplusapp.com/'
    }

    # API Call
    api_url = f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={video_url}'
    
    try:
        response_obj = spoof_requests.get(api_url, headers=headers, impersonate="chrome120")
        response = response_obj.json()
    except Exception as e:
        return {"error": f"Request Blocked by Security: {e}"}

    if response.get('status') != 'ok':
        return {"error": f"API Error: {response.get('error', response)}"}

    mpd = response['drmUrls']['manifestUrl']
    lic = response['drmUrls']['licenseUrl']
    
    mpd_response = spoof_requests.get(mpd, impersonate="chrome120")
    soup = BeautifulSoup(mpd_response.text, 'xml')

    uuid_tag = soup.find('ContentProtection', attrs={'schemeIdUri': 'urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed'})
    if not uuid_tag or not uuid_tag.find('cenc:pssh'):
        return {"error": "PSSH not found in MPD manifest."}
        
    pssh_data = uuid_tag.find('cenc:pssh').text

    ipssh = PSSH(pssh_data)
    device = Device.load(wvd)
    cdm = Cdm.from_device(device)
    session_id = cdm.open()
    
    challenge = cdm.get_license_challenge(session_id, ipssh)
    licence = spoof_requests.post(lic, data=challenge, headers=headers, impersonate="chrome120")
    
    if licence.status_code != 200:
        cdm.close(session_id)
        return {"error": f"License request failed (Status {licence.status_code})."}

    cdm.parse_license(session_id, licence.content)

    keys = []
    for key in cdm.get_keys(session_id):
        if key.type != 'SIGNING':
            keys.append(f'{key.kid.hex}:{key.key.hex()}')

    cdm.close(session_id)

    return {"mpd_url": mpd, "keys": keys}
