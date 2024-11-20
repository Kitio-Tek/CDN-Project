# origin_server/dht_node.py
import asyncio
from kademlia.network import Server

async def start_dht_node():
    server = Server()
    await server.listen(8468)
    # Bootstrap with itself for simplicity; in a real setup, use multiple bootstrap nodes
    await server.bootstrap([('127.0.0.1', 8468)])
    return server

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = loop.run_until_complete(start_dht_node())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
