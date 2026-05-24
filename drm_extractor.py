import os
import glob
import re
from bs4 import BeautifulSoup
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
from curl_cffi import requests as spoof_requests

def wvd_check():
    try:
        return glob.glob(f'{os.getcwd()}/WVDs/*.wvd')[0]
    except IndexError:
        raise FileNotFoundError("WVD file missing in folder.")

def parse_curl_headers(curl_text):
    """AI System: cURL string se browser ke saare asli headers nikalna"""
    headers = {}
    try:
        # Regex to extract all -H headers perfectly
        pattern = r"-H\s+['\"](.*?)['\"]"
        matches = re.findall(pattern, curl_text)
        for match in matches:
            if ':' in match:
                key, val = match.split(':', 1)
                # In 3 headers ko drop karna zaroori hai error se bachne ke liye
                if key.lower() not in ['host', 'content-length', 'accept-encoding']:
                    headers[key.strip()] = val.strip()
    except Exception as e:
        print(f"Header parsing error: {e}")
    return headers

def generate_drm_keys(video_url, curl_text):
    wvd = wvd_check()
    
    # Browser DNA (Headers) load ho rahe hain
    headers = parse_curl_headers(curl_text)
    
    # Agar galti se sirf token bhej diya, toh fallback logic
    if 'x-access-token' not in [k.lower() for k in headers.keys()]:
        clean_token = ''.join(curl_text.split())
        headers = {
            'x-access-token': clean_token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Origin': 'https://web.classplusapp.com',
            'Referer': 'https://web.classplusapp.com/'
        }

    api_url = f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={video_url}'
    
    try:
        # Impersonating Real Chrome WAF Bypass
        response_obj = spoof_requests.get(api_url, headers=headers, impersonate="chrome120")
        response = response_obj.json()
    except Exception as e:
        return {"error": f"Firewall Blocked Request: {e}"}

    if response.get('status') != 'ok':
        return {"error": f"API Error: {response.get('error', response)}"}

    mpd = response['drmUrls']['manifestUrl']
    lic = response['drmUrls']['licenseUrl']
    
    mpd_response = spoof_requests.get(mpd, impersonate="chrome120")
    soup = BeautifulSoup(mpd_response.text, 'xml')

    uuid_tag = soup.find('ContentProtection', attrs={'schemeIdUri': 'urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed'})
    if not uuid_tag or not uuid_tag.find('cenc:pssh'):
        return {"error": "PSSH not found."}
        
    pssh_data = uuid_tag.find('cenc:pssh').text

    ipssh = PSSH(pssh_data)
    device = Device.load(wvd)
    cdm = Cdm.from_device(device)
    session_id = cdm.open()
    
    challenge = cdm.get_license_challenge(session_id, ipssh)
    licence = spoof_requests.post(lic, data=challenge, headers=headers, impersonate="chrome120")
    
    if licence.status_code != 200:
        cdm.close(session_id)
        return {"error": f"License request failed ({licence.status_code})."}

    cdm.parse_license(session_id, licence.content)

    keys = []
    for key in cdm.get_keys(session_id):
        if key.type != 'SIGNING':
            keys.append(f'{key.kid.hex}:{key.key.hex()}')

    cdm.close(session_id)

    return {"mpd_url": mpd, "keys": keys}
