import os
import glob
import requests
from bs4 import BeautifulSoup
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH

def wvd_check():
    try:
        # WVDs फोल्डर से .wvd फाइल खोजें
        extracted_device = glob.glob(f'{os.getcwd()}/WVDs/*.wvd')[0]
        return extracted_device
    except IndexError:
        raise FileNotFoundError("WVD file not found in 'WVDs' folder. Please upload it.")

def generate_drm_keys(video_url, user_token):
    """
    ClassPlus वीडियो URL और यूज़र द्वारा दिए गए Token का उपयोग करके DRM Keys निकालता है।
    """
    wvd = wvd_check()

    # Dynamic Token from User Input
    headers = {
        'x-access-token': user_token
    }

    # API Call for JW-Signed URL
    api_url = f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={video_url}'
    response = requests.get(api_url, headers=headers).json()

    if response.get('status') != 'ok':
        return {"error": f"Failed to fetch DRM URLs. Invalid Token or API Error. Response: {response}"}

    mpd = response['drmUrls']['manifestUrl']
    lic = response['drmUrls']['licenseUrl']
    
    mpd_response = requests.get(mpd)
    soup = BeautifulSoup(mpd_response.text, 'xml')

    # Extract PSSH
    uuid_tag = soup.find('ContentProtection', attrs={'schemeIdUri': 'urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed'})
    if not uuid_tag or not uuid_tag.find('cenc:pssh'):
        return {"error": "PSSH not found in MPD manifest."}
        
    pssh_data = uuid_tag.find('cenc:pssh').text

    # PyWidevine Decryption Logic
    ipssh = PSSH(pssh_data)
    device = Device.load(wvd)
    cdm = Cdm.from_device(device)
    session_id = cdm.open()
    
    challenge = cdm.get_license_challenge(session_id, ipssh)
    licence = requests.post(lic, data=challenge, headers=headers)
    
    if licence.status_code != 200:
        cdm.close(session_id)
        return {"error": f"License request failed with status {licence.status_code}"}

    cdm.parse_license(session_id, licence.content)

    keys = []
    for key in cdm.get_keys(session_id):
        if key.type != 'SIGNING':
            keys.append(f'{key.kid.hex}:{key.key.hex()}')

    cdm.close(session_id)

    return {"mpd_url": mpd, "keys": keys}
