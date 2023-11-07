import common


def main():

    with common.create_client() as client:
        consumer = client.subscribe(topic=common.TOPIC_NAME,
                                    subscription_name='sample-subscriber',
                                    schema=common.create_schema())

        user_message: common.UserMessage
        while True:
            msg = consumer.receive()
            user_message = msg.value()
            print(f'Получено:\n\t{user_message.username = }\n\t{user_message.message = }\n\t{msg.schema_version() = }')

            consumer.acknowledge(msg)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(ex)
