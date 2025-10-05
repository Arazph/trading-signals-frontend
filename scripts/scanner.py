import os, json, datetime as dt, requests as r

COIN = "BTC"          # v0.1 picks BTC every hour (expand later)
SL   = 2.0

HF   = os.getenv("HF_URL")
now  = dt.datetime.utcnow().isoformat(timespec="seconds")+"Z"

def main():
    url = f"{HF}/signal?symbol={COIN}&sl_pct={SL}"
    sig = r.get(url, timeout=15).json()
    row = [now, COIN, sig["direction"], sig["entry"], sig["sl"], sig["tp"], sig["confidence"], sig["why"]]

    # Google Sheets (optional)
    key = os.getenv("GSHEET_KEY")
    gid = os.getenv("GSHEET_ID")
    if key and gid:
        sheet_append(gid, key, row)

    # Telegram (optional)
    bot  = os.getenv("TG_BOT")
    chat = os.getenv("TG_CHAT")
    if bot and chat:
        txt = f"{COIN} {sig['direction']}  Entry={sig['entry']}  SL={sig['sl']}  TP={sig['tp']}  Conf={sig['confidence']}%"
        r.post(f"https://api.telegram.org/bot{bot}/sendMessage", json={"chat_id":chat,"text":txt})

    # Discord (optional)
    hook = os.getenv("DISCORD")
    if hook:
        r.post(hook, json={"content": f"🚀 {COIN} {sig['direction']}  Entry={sig['entry']}  SL={sig['sl']}  TP={sig['tp']}  Conf={sig['confidence']}%"})

def sheet_append(gid, key, row):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{gid}/values/A:H/append?valueInputOption=RAW"
    r.post(url, json={"values": [row]}, headers={"Authorization": f"Bearer {key}"})

if __name__ == "__main__":
    main()
