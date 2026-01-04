import requests
import time
from web3 import Web3
from eth_account import Account

RPC_URL = "https://chainrpc.polarise.org/"
FAUCET_URL = "https://apifaucet-t.polarise.org/claim"
SITEKEY = "6Le97hIsAAAAAFsmmcgy66F9YbLnwgnWBILrMuqn"
PAGEURL = "https://faucet.polarise.org"
MIN_BALANCE = 0.1

w3 = Web3(Web3.HTTPProvider(RPC_URL))

with open("2captcha.txt", "r", encoding="utf-8") as f:
    CAPTCHA_KEY = f.read().strip()

def solve_captcha():
    r = requests.post("https://2captcha.com/in.php", data={
        "key": CAPTCHA_KEY,
        "method": "userrecaptcha",
        "googlekey": SITEKEY,
        "pageurl": PAGEURL,
        "json": 1
    }).json()

    if r.get("status") != 1:
        return None

    task_id = r["request"]

    for _ in range(24):
        time.sleep(5)
        res = requests.get("https://2captcha.com/res.php", params={
            "key": CAPTCHA_KEY,
            "action": "get",
            "id": task_id,
            "json": 1
        }).json()

        if res.get("status") == 1:
            return res["request"]

    return None

def claim_faucet(address, captcha):
    r = requests.post(
        FAUCET_URL,
        json={
            "address": address.lower(),
            "denom": "uluna",
            "amount": "1",
            "response": captcha
        },
        headers={
            "content-type": "application/json",
            "origin": "https://faucet.polarise.org",
            "referer": "https://faucet.polarise.org",
            "user-agent": "Mozilla/5.0"
        },
        timeout=60
    )

    if r.status_code == 200:
        return r.json().get("txhash")

    return None

print("Load accounts from mail.txt")

with open("mail.txt", "r", encoding="utf-8") as f:
    private_keys = []
    for line in f:
        if ":" in line:
            parts = line.strip().split(":")
            if len(parts) >= 2:
                private_keys.append(parts[1])

print(f"Total akun: {len(private_keys)}\n")

for pk in private_keys:
    try:
        account = Account.from_key(pk)
        address = account.address

        balance = w3.from_wei(w3.eth.get_balance(address), "ether")

        print(f"Address : {address}")
        print(f"Balance : {balance} POLAR")

        if balance >= MIN_BALANCE:
            print("Balance cukup, skip\n")
            continue

        print("Balance kurang, solve captcha...")
        captcha = solve_captcha()

        if not captcha:
            print("Captcha gagal\n")
            continue

        tx = claim_faucet(address, captcha)

        if tx:
            print(f"Faucet sukses | Tx: {tx}\n")
        else:
            print("Faucet gagal\n")

        time.sleep(10)

    except Exception as e:
        print("Error:", e, "\n")

print("Selesai")
