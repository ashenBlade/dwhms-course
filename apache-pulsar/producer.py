import pulsar

from common import create_client, create_schema, UserMessage, TOPIC_NAME


def main():
    with create_client() as client:
        producer = client.create_producer(topic=TOPIC_NAME, schema=(create_schema()),
                                          producer_name='sample-producer')
        message = UserMessage()
        message.message = 'hello, world'
        message.username = 'username sample'
        message.attachments = [
            'first'
        ]
        producer.send(message)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(ex)
