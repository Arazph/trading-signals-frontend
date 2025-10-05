import os, json, datetime as dt, requests as r

COIN = "BTC"          # v0.1 picks BTC every hour (expand later)
SL   = 2.0

HF   = os.getenv("HF_URL")
now  = dt.datetime.utcnow().isoformat(timespec="seconds")+"Z"

def main():
    url = f"{HF}/signal?symbol={COIN}&sl_pct={SL}"
    sig = r.get(url, timeout=15).json()
    row = [now, COIN, sig["direction"], sig["entry"], sig["sl"], sig["tp"], sig["confidence"], sig["why"]]
    print("Signal row:", row)

    # Google Sheets – hard-coded correct ID for this test
    key = os.getenv("GSHEET_KEY")
    gid = "1dxt49XwMX2XSQu1rFajR8_L-QuMJUrmFm2LVhK3v3c0"   # <-- hard-coded
    if key:
        sheet_append(gid, key, row)

    # Telegram
    bot  = os.getenv("TG_BOT")
    chat = os.getenv("TG_CHAT")
    if bot and chat:
        txt = f"{COIN} {sig['direction']}  Entry={sig['entry']}  SL={sig['sl']}  TP={sig['tp']}  Conf={sig['confidence']}%"
        r.post(f"https://api.telegram.org/bot{bot}/sendMessage", json={"chat_id":chat,"text":txt})
        print("Telegram sent")

    # Discord
    hook = os.getenv("DISCORD")
    if hook:
        r.post(hook, json={"content": f"🚀 {COIN} {sig['direction']}  Entry={sig['entry']}  SL={sig['sl']}  TP={sig['tp']}  Conf={sig['confidence']}%"})
        print("Discord posted")
def sheet_append(gid, key, row):
    print("Raw GSHEET_ID from env:", repr(gid))
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{gid.strip()}/values/A:H/append?valueInputOption=RAW"
    body = {"values": [row]}
    hdr  = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    print("Google URL:", url)
    resp = r.post(url, json=body, headers=hdr, timeout=15)
    print("Google status:", resp.status_code)
    if resp.status_code != 200:
        print("Google reply:", resp.text[:500])
        resp.raise_for_status()
    print("Google append OK")

if __name__ == "__main__":
    main()
