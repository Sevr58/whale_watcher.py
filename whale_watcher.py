#!/usr/bin/env python3
"""
WhaleWatcher — утилита для мониторинга «крупных» (whale) ERC‑20 транзакций в Pending Mempool Ethereum
по заданному порогу. Позволяет в режиме реального времени видеть, когда перевод токенов
превышает ваш порог и получать о нём уведомление в консоли.
"""

import os
import time
import logging
from decimal import Decimal

from web3 import Web3
from dotenv import load_dotenv

# Минимальный ABI для чтения decimals
ERC20_ABI = [{
    "constant": True,
    "inputs": [],
    "name": "decimals",
    "outputs": [{"name": "", "type": "uint8"}],
    "type": "function"
}]

def main():
    # Загрузка переменных окружения
    load_dotenv()
    ws_url = os.getenv("WS_URL")
    if not ws_url:
        raise RuntimeError("Укажите WebSocket‑URL вашего провайдера в переменной WS_URL")
    try:
        threshold: Decimal = Decimal(os.getenv("THRESHOLD", "100000"))
    except Exception:
        raise RuntimeError("THRESHOLD должен быть числом, например 50000")

    # Инициализация Web3
    w3 = Web3(Web3.WebsocketProvider(ws_url))
    if not w3.isConnected():
        raise RuntimeError("Не удалось подключиться к Ethereum через WS_URL")

    # Подготовка фильтра для pending-транзакций
    pending_filter = w3.eth.filter("pending")
    transfer_sig = w3.keccak(text="transfer(address,address,uint256)").hex()[:10]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    logging.info(f"Запущен мониторинг ERC‑20 переводов ≥ {threshold} токенов")

    while True:
        try:
            for tx_hash in pending_filter.get_new_entries():
                tx = w3.eth.get_transaction(tx_hash)
                # Ищем только вызовы transfer()
                if tx.input.startswith(transfer_sig) and tx.to:
                    token = w3.eth.contract(address=tx.to, abi=ERC20_ABI)
                    try:
                        dec = token.functions.decimals().call()
                    except Exception:
                        continue  # не ERC‑20‑совместимый контракт
                    # Декодирование аргументов: адрес получателя + сумма
                    raw = tx.input[10:]
                    recipient = "0x" + raw[0:64][-40:]
                    amount = int(raw[64:], 16)
                    human_amount = Decimal(amount) / (Decimal(10) ** dec)
                    if human_amount >= threshold:
                        logging.info(
                            f"Кит перевёл {human_amount} токенов контракта {tx.to} → {recipient} "
                            f"(hash: {tx_hash.hex()})"
                        )
        except Exception as e:
            logging.error(f"Ошибка в основном цикле: {e}")
            time.sleep(5)
        time.sleep(1)


if __name__ == "__main__":
    main()
