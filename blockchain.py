import os, json
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
akun = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

with open("artifacts/contracts/AgroRecord.sol/AgroRecord.json") as f:
    abi = json.load(f)["abi"]

c = w3.eth.contract(
    address=Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS")),
    abi=abi,
)

def hitung_hash(data: dict) -> bytes:
    teks = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return Web3.keccak(text=teks)

def kirim_record(data: dict, status: int) -> str:
    tx = c.functions.submit(hitung_hash(data), status).build_transaction({
        "from": akun.address,
        "nonce": w3.eth.get_transaction_count(akun.address),
    })
    signed = akun.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
    tx_hash = w3.eth.send_raw_transaction(raw)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def verifikasi(id_record: int, data: dict) -> bool:
    r = c.functions.records(id_record).call()
    return r[0] == hitung_hash(data)

def total() -> int:
    return c.functions.total().call()
    
def catat_perubahan(hash_sebelum: str, hash_sesudah: str, status: int) -> str:
    hs = bytes.fromhex(hash_sebelum.removeprefix("0x"))
    hd = bytes.fromhex(hash_sesudah.removeprefix("0x"))
    tx = c.functions.catatPerubahan(hs, hd, status).build_transaction({
        "from": akun.address, "nonce": w3.eth.get_transaction_count(akun.address)})
    signed = akun.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
    h = w3.eth.send_raw_transaction(raw)
    w3.eth.wait_for_transaction_receipt(h)
    return h.hex()


def baca_perubahan(id_perubahan: int):
    r = c.functions.perubahan(id_perubahan).call()
    return r[0].hex(), r[1].hex()


def total_perubahan() -> int:
    return c.functions.totalPerubahan().call()