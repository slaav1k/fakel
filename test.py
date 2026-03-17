import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from bot_secrets import TOKEN, PROXY_URL


async def test_proxy():
    try:
        # Создаем connector с прокси
        connector = ProxyConnector.from_url(
            PROXY_URL
        )

        # Тестируем прокси через прямой запрос к Telegram API
        async with aiohttp.ClientSession(connector=connector) as session:
            url = f"https://api.telegram.org/bot{TOKEN}/getMe"
            async with session.get(url) as resp:
                data = await resp.json()
                if data.get('ok'):
                    bot_info = data['result']
                    print(f"✅ Прокси работает! Бот: @{bot_info['username']}")
                else:
                    print(f"❌ Ошибка API: {data}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_proxy())