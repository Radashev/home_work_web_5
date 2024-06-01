import asyncio
import logging

import httpx
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from datetime import datetime
from datetime import timedelta

from aiohttp import web
import aiofiles
import os

logging.basicConfig(level=logging.INFO)


async def request(url: str) -> dict | str:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            return "Не вийшло в мене взнати курс. Приват не відповідає . Дякую Юрію Кучмі за курс.   :)"


async def get_exchange():
    response = await request(f'https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5')
    # переробить на більш придатний результат
    return str(response)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith("exchange"):
                days = message.split()[1] if len(message.split()) > 1 else '1'
                exchange = await get_exchange(days)
                await self.send_to_clients(exchange)
                await log_command(message)
            elif message == 'Hello server':
                await self.send_to_clients("Привіт всім!")
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def log_command(command):
    async with aiofiles.open('exchange_log.txt', mode='a') as f:
        await f.write(f"{datetime.now()} - {command}\n")


async def index(request):
    return web.FileResponse('./static/index.html')


async def init_app():
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_static('/static/', path=str(os.getcwd()) + '/static', name='static')
    return app


async def main():
    server = Server()
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    async with websockets.serve(server.ws_handler, 'localhost', 8081):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(main())
