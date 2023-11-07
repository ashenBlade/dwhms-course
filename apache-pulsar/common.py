import contextlib
import typing

import pulsar
from pulsar.schema import Record, String, Array


# во второй версии добавляю поле attachments
class UserMessage(Record):
    username = String()
    message = String()
    attachments = Array(String())


@contextlib.contextmanager
def create_client() -> typing.ContextManager[pulsar.Client]:
    client = pulsar.Client('pulsar://localhost:6650',
                           authentication=pulsar.AuthenticationBasic(username='admin', password='apachepulsar'))
    try:
        yield client
    finally:
        client.close()


def create_schema():
    return pulsar.schema.JsonSchema(UserMessage)


TOPIC_NAME = 'persistent://public/default/dwhms-test'
CLUSTER_NAME = 'cluster-a'
