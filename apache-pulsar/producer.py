import pulsar

from common import create_client, create_schema, UserMessage, TOPIC_NAME, NEW_VERSION


def main():
    print("Подключаюсь")
    with create_client() as client:
        producer = client.create_producer(topic=TOPIC_NAME, schema=create_schema(),
                                          producer_name='sample-producer')
        message = UserMessage()
        message.message = 'hello, world'
        message.username = 'username sample'

        if NEW_VERSION:
            print("Отправляю новую версию")
            message.comment = "this is a comment"
        else:
            print('Отправляю старую версию')

        producer.send(message)
        print('Отправлено')


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(ex)
