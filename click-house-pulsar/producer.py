import contextlib
import logging
import time
import typing

import pulsar
from faker import Faker
from pulsar.schema import Record, String, Integer

logging.basicConfig(level=logging.DEBUG)


class Event(Record):
    username = String()
    post = String()
    page = Integer()


@contextlib.contextmanager
def create_client() -> typing.ContextManager[pulsar.Client]:
    client = pulsar.Client('pulsar://localhost:6650',
                           authentication=pulsar.AuthenticationBasic(username='admin', password='apachepulsar'))
    try:
        yield client
    finally:
        logging.info('Закрываю клиента')
        client.close()


TOPIC_NAME = 'persistent://public/default/clickhouse-test'

def main():
    logger = logging.getLogger('logger')
    logger.info('Создаю клиента')
    with create_client() as client:
        logger.info('Создаю продьюсера')
        producer = client.create_producer(topic=TOPIC_NAME, schema=pulsar.schema.JsonSchema(Event))
        logger.info('Начинаю отправку сообщений')
        faker = Faker('ru')
        while True:
            event = create_event(faker)
            logger.debug('Отправляю событие')
            message_id = producer.send(event)
            logger.debug('Id сообщения: %s', message_id)
            time.sleep(10)


def create_event(faker):
    event = Event()
    event.username = faker.name()
    event.post = faker.word()
    event.page = faker.random.randint(0, 100)
    return event


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.critical('Необработанное исключение', exc_info=e)
