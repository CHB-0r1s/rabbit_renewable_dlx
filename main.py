import asyncio
import logging
from typing import Optional

import aio_pika
from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage

from settings import settings as s


async def declare_topology(channel):
    queue_name = "test_queue"

    exchange = await channel.declare_exchange("fanout", auto_delete=True, type="fanout")
    dlx_exchange = await channel.declare_exchange("dlx_exchange", auto_delete=True, type="fanout")

    dlx_queue = await channel.declare_queue(
        "dlx",
        auto_delete=True,
        arguments={
            "x-dead-letter-exchange": "fanout",
            "x-message-ttl": 30000,
        },
    )
    queue = await channel.declare_queue(
        queue_name,
        auto_delete=True,
        arguments={
            "x-dead-letter-exchange": "dlx_exchange",
            "x-max-length-bytes": 15,
        },
    )

    await queue.bind(exchange)
    await dlx_queue.bind(dlx_exchange)

    return queue, exchange, dlx_queue, dlx_exchange


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    connection = await aio_pika.connect_robust(s.rabbit_settings.dsn)

    async with connection:
        # Creating channel
        channel = await connection.channel()
        work_queue, work_exchange, dlx_queue, dlx_exchange = await declare_topology(channel)

        await work_exchange.publish(
            Message(
                bytes("Hello", "utf-8"),
                content_type="text/plain",
                headers={"foo": "bar"},
            ),
            "test_queue",
        )

        # incoming_message: Optional[AbstractIncomingMessage] = await work_queue.get(timeout=5, fail=False)
        #
        # if incoming_message:
        #     # Confirm message
        #     await incoming_message.ack()
        #     print(incoming_message.body)
        # else:
        #     print("Queue empty")


if __name__ == "__main__":
    asyncio.run(main())
