import sys
from datetime import datetime, timedelta
import asyncio
import aiohttp
import platform
import json


class HttpError(Exception):
    pass


class PrivatBankAPI:
    BASE_URL = 'https://api.privatbank.ua/p24api/exchange_rates?date='

    async def fetch_exchange_rates(self, date: str):
        url = f"{self.BASE_URL}{date}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise HttpError(f"Error status: {response.status} for {url}")


class ExchangeRateFetcher:
    def __init__(self, days: int, currencies: list):
        if days > 10:
            raise ValueError("The maximum number of days you can request is 10.")
        self.days = days
        self.currencies = currencies
        self.api = PrivatBankAPI()

    async def fetch_rates(self):
        results = []
        for i in range(self.days):
            date = (datetime.now() - timedelta(days=i)).strftime("%d.%m.%Y")
            try:
                data = await self.api.fetch_exchange_rates(date)
                rates = self.extract_relevant_rates(data)
                results.append({date: rates})
            except HttpError as e:
                print(e)
        return results

    def extract_relevant_rates(self, data):
        rates = {}
        for rate in data.get('exchangeRate', []):
            if rate['currency'] in self.currencies:
                rates[rate['currency']] = {
                    'sale': rate.get('saleRate', 'N/A'),
                    'purchase': rate.get('purchaseRate', 'N/A')
                }
        return rates


async def main(days, currencies):
    fetcher = ExchangeRateFetcher(days, currencies)
    results = await fetcher.fetch_rates()
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if len(sys.argv) < 3:
        print("Error: Please provide the number of days and at least one currency as arguments.")
        sys.exit(1)

    try:
        days = int(sys.argv[1])
        currencies = sys.argv[2:]
    except ValueError:
        print("Error: The number of days must be an integer.")
        sys.exit(1)

    asyncio.run(main(days, currencies))
