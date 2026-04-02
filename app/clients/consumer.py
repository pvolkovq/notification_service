import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from app.clients.mail import EmailClient
from app.clients.message import MessageClient
from app.clients.push import PushClient
from app.core.config import kafka_uri
from app.core.database import get_session, sessionmanager
from app.utils.parser import parse_uri_data


async def main() -> None:
    kafka_dsn, kafka_options = parse_uri_data(kafka_uri)
    consumer = AIOKafkaConsumer(
        kafka_options.pop("topic"),
        bootstrap_servers=f"{kafka_dsn.hostname}:{kafka_dsn.port}",
        security_protocol="SASL_PLAINTEXT",
        sasl_mechanism="PLAIN",
        sasl_plain_username=kafka_dsn.username,
        sasl_plain_password=kafka_dsn.password,
        key_deserializer=lambda m: m.decode(),
    )
    sessionmanager.init_db()
    await consumer.start()

    try:
        async for message in consumer:
            try:
                if not message.value:
                    continue
                key = message.key
                value = json.loads(message.value)
                client = None
                async for session in get_session():
                    if key == "sms":
                        client = MessageClient(
                            key=value.get("key"),
                            text=value.get("text"),
                            to=value.get("to"),
                            account_id=value.get("account_id"),
                            options=value.get("options", {}),
                            session=session,
                        )
                    elif key == "email":
                        client = EmailClient(
                            content=value.get("content"),
                            to=value.get("to"),
                            subject=value.get("subject"),
                            files=value.get("files"),
                            account_id=value.get("account_id"),
                            options=value.get("options", {}),
                            session=session,
                        )
                    elif key == "push":
                        client = PushClient(
                            token=value.get("value"),
                            text=value.get("text"),
                            account_id=value.get("account_id"),
                            options=value.get("options", {}),
                            session=session,
                        )
                    if client:
                        await client.process()
            except Exception as e:
                await session.rollback()
                logging.error(e)
            await session.close()
    finally:
        await consumer.stop()
        await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(main())
