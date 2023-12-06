import logging
import os
import time

from events import create_random_event, create_client, get_all_topics, get_all_events

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()


def build_producers(client):
    result = {}
    for e in get_all_events():
        logger.info('Создаю продьюсера для топика %s', e.topic())
        result[e.topic()] = client.create_producer(e.topic(), schema=e.get_schema())
    return result


def main():
    logger.info('Создаю клиента')
    pulsar_url = os.environ.get('PULSAR_URL', 'pulsar://pulsar:6650')
    logger.debug('PULSAR по адресу %s', pulsar_url)
    with create_client(pulsar_url) as client:
        topic_producer = build_producers(client)
        try:
            while True:
                event = create_random_event()
                logger.debug('Отправляю событие %s', type(event))
                topic_producer[event.topic()].send(event)
                time.sleep(1)
        finally:
            logger.info('Закрываю продьюсеров')
            for p in topic_producer.values():
                p.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.critical('Необработанное исключение', exc_info=e)
        exit(1)
