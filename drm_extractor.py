import os
import glob
import requests
from bs4 import BeautifulSoup
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH

def wvd_check():
    try:
        return glob.glob(f'{os.getcwd()}/WVDs/*.wvd')[0]
    except IndexError:
        raise FileNotFoundError("WVD file not found in 'WVDs' folder. Please upload it.")

def generate_drm_keys(video_url, user_token):
    wvd = wvd_check()
    
    # 1. Token Cleanup: टेलीग्राम द्वारा डाले गए किसी भी स्पेस या नई लाइन को पूरी तरह खत्म करना
    clean_token = ''.join(user_token.split())

    # 2. Advance Headers: Classplus को 100% असली ब्राउज़र होने का यकीन दिलाना
    headers = {
        'x-access-token': clean_token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://web.classplusapp.com',
        'Referer': 'https://web.classplusapp.com/',
        'Api-Version': '50',
        'Device-Id': 'Web-Browser'
    }

    api_url = f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={video_url}'
    
    try:
        response = requests.get(api_url, headers=headers).json()
    except Exception as e:
        return {"error": f"API Request Blocked. Error: {e}"}

    if response.get('status') != 'ok':
        return {"error": f"API Error: {response.get('error', 'Bad token')} - Server rejected the IP or Token."}

    mpd = response['drmUrls']['manifestUrl']
    lic = response['drmUrls']['licenseUrl']
    
    mpd_response = requests.get(mpd)
    soup = BeautifulSoup(mpd_response.text, 'xml')

    uuid_tag = soup.find('ContentProtection', attrs={'schemeIdUri': 'urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed'})
    if not uuid_tag or not uuid_tag.find('cenc:pssh'):
        return {"error": "PSSH not found in MPD."}
        
    pssh_data = uuid_tag.find('cenc:pssh').text

    ipssh = PSSH(pssh_data)
    device = Device.load(wvd)
    cdm = Cdm.from_device(device)
    session_id = cdm.open()
    
    challenge = cdm.get_license_challenge(session_id, ipssh)
    licence = requests.post(lic, data=challenge, headers=headers)
    
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
