# WhaleWatcher

**Мониторинг крупных ERC‑20 транзакций в Mempool Ethereum**

WhaleWatcher в режиме реального времени отслеживает `pending`-транзакции в Ethereum и выводит в консоль любые переводы ERC‑20 токенов, превышающие заданный порог.

## Функциональность

- Подключение по WebSocket к любому провайдеру (Infura, Alchemy и т.п.).
- Фильтрация `pending`-транзакций по сигнатуре `transfer(address,uint256)`.
- Автоматическое определение числа десятичных знаков (decimals) у токена.
- Вывод транзакций, где сумма ≥ `THRESHOLD` токенов.

## Как использовать

1. **Склонируйте репозиторий**

   ```bash
   git clone https://github.com/yourusername/WhaleWatcher.git
   cd WhaleWatcher
