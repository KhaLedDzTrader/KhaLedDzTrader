import requests
import json
import os
import uuid
from bs4 import BeautifulSoup

SERVER_URL = 'https://serverdztrader.pythonanywhere.com/verify'

WHITELIST = frozenset({
    'USDPKR-OTC', 'USDNGN-OTC', 'BA-OTC', 'USDEGP-OTC', 'FB-OTC', 'USDCOP-OTC',
    'MCD-OTC', 'INTEL-OTC', 'PFE-OTC', 'USDINR-OTC', 'USDBRL-OTC',
    'NZDUSD-OTC', 'CADCHF-OTC', 'NZDCHF-OTC', 'XAUUSD-OTC', 'MSFT-OTC', 'USDPHP-OTC',
    'USCRUDE-OTC', 'XAGUSD-OTC', 'USDZAR-OTC', 'BTC-OTC', 'NZDJPY-OTC', 'NZDCAD-OTC',
    'USDBDT-OTC', 'JNJ-OTC', 'USDMXN-OTC', 'USDIDR-OTC', 'AXP-OTC',
    'USDDZD-OTC', 'UKBRENT-OTC', 'EURNZD-OTC', 'USDARS-OTC', 'USDTRY-OTC'
})

DEVICE_FILE = 'device.json'
VERIFIED_FILE = 'verified.json'

# الحد الأدنى للثقة للصفقات
MIN_CONFIDENCE = 98.0  # يمكن تغييره هنا بسهولة

def get_device_id():
    if os.path.exists(DEVICE_FILE):
        try:
            with open(DEVICE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("device_id")
        except:
            pass
    device_id = str(uuid.uuid4())
    with open(DEVICE_FILE, 'w') as f:
        json.dump({"device_id": device_id}, f)
    return device_id

def is_verified():
    if os.path.exists(VERIFIED_FILE):
        try:
            with open(VERIFIED_FILE, 'r') as f:
                data = json.load(f)
                return data.get("verified", False)
        except:
            return False
    return False

def set_verified():
    with open(VERIFIED_FILE, 'w') as f:
        json.dump({"verified": True}, f)

def verify_key_with_server(key):
    device_id = get_device_id()
    payload = {"device_id": device_id, "key": key}
    try:
        response = requests.post(SERVER_URL, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json() or {"status": "fail", "message": "Empty response from server"}
        else:
            return {"status": "fail", "message": f"HTTP {response.status_code}"}
    except requests.RequestException as e:
        print(f"Error connecting to server: {e}")
        return {"status": "fail", "message": "Cannot connect to server"}

def fetch_signals_from_site():
    try:
        url = "https://www.gammaxbd.xyz"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        signals = []

        rows = soup.select("#tradeFeedContainer .trade-row")
        for row in rows:
            pair_tag = row.select_one("span.font-semibold")
            action_tag = row.select_one("span.font-bold")
            time_tag = row.select("span")[2] if len(row.select("span")) > 2 else None
            confidence_tag = row.select_one("span.font-medium")

            if not pair_tag or not action_tag or not time_tag or not confidence_tag:
                continue

            pair = pair_tag.text.strip().replace("_", "-").upper()
            
            # تحديد الاتجاه بناءً على النص
            action_text = action_tag.text.strip().upper()
            if action_text == "CALL":
                action = "CALL"
            elif action_text == "PUT":
                action = "PUT"
            else:
                continue 

            time = time_tag.text.strip()
            try:
                confidence = float(confidence_tag.text.strip().replace("%", ""))
            except:
                confidence = 0

            # استخدم المتغير MIN_CONFIDENCE فقط
            if pair in WHITELIST and confidence >= MIN_CONFIDENCE:
                signals.append({
                    "pair": pair,
                    "time": time,
                    "action": action,
                    "confidence": confidence
                })

        return signals

    except Exception as e:
        print(f"Error fetching signals: {e}")
        return []