import os
import requests
import time
from eth_account import Account
from datetime import datetime
import pytz
from colorama import Fore, Style, init

# Init
os.system('clear' if os.name == 'posix' else 'cls')
init(autoreset=True)

FAUCET_URL = "https://apifaucet-t.polarise.org/claim"
FAUCET_PAGE = "https://faucet.polarise.org"
SITE_KEY = "6Le97hIsAAAAAFsmmcgy66F9YbLnwgnWBILrMuqn"

# ================= LOGGER =================
def log(msg, level="INFO"):
    wib = pytz.timezone("Asia/Jakarta")
    ts = datetime.now(wib).strftime("%H:%M:%S")
    color = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "ERROR": Fore.RED,
        "WARN": Fore.YELLOW
    }.get(level, Fore.WHITE)
    print(f"[{ts}] {color}[{level}] {Style.RESET_ALL}{msg}")

# ================= 2CAPTCHA =================
class TwoCaptcha:
    def __init__(self, api_key):
        self.key = api_key
        self.base = "https://2captcha.com"

    def solve(self):
        try:
            create = requests.post(
                f"{self.base}/in.php",
                data={
                    "key": self.key,
                    "method": "userrecaptcha",
                    "googlekey": SITE_KEY,
                    "pageurl": FAUCET_PAGE,
                    "json": 1
                },
                timeout=30
            ).json()

            if create.get("status") != 1:
                return None

            task_id = create["request"]

            for _ in range(24):
                time.sleep(5)
                res = requests.get(
                    f"{self.base}/res.php",
                    params={
                        "key": self.key,
                        "action": "get",
                        "id": task_id,
                        "json": 1
                    },
                    timeout=30
                ).json()

                if res.get("status") == 1:
                    return res["request"]
        except:
            pass
        return None

# ================= FAUCET =================
def claim_faucet(address, solver):
    log("Solving captcha...")
    token = solver.solve()
    if not token:
        log("Captcha failed", "ERROR")
        return False

    try:
        res = requests.post(
            FAUCET_URL,
            json={
                "address": address,
                "denom": "uluna",
                "response": token
            },
            timeout=30
        ).json()

        if res.get("code") == 200:
            log(f"Faucet success → {res.get('amount')} POLAR", "SUCCESS")
            return True
        else:
            log(f"Faucet failed: {res}", "ERROR")
    except Exception as e:
        log(str(e), "ERROR")
    return False

# ================= MAIN =================
def main():
    if not os.path.exists("accounts.txt"):
        log("accounts.txt not found", "ERROR")
        return

    if not os.path.exists("2captcha.txt"):
        log("2captcha.txt not found", "ERROR")
        return

    with open("2captcha.txt") as f:
        captcha_key = f.read().strip()

    solver = TwoCaptcha(captcha_key)

    with open("accounts.txt") as f:
        keys = [x.strip() for x in f if x.strip()]

    for i, pk in enumerate(keys, 1):
        print(f"\n{Fore.YELLOW}=== Account {i}/{len(keys)} ==={Style.RESET_ALL}")
        acc = Account.from_key(pk)
        claim_faucet(acc.address, solver)
        time.sleep(3)

if __name__ == "__main__":
    main()
