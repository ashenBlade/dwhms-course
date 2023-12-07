import contextlib
import csv
import io
import logging
import os
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Type, ContextManager

import faker
import hdfs
import pulsar
from pulsar.schema import Record, String, Integer, Double


faker = faker.Faker(locale='ru')
event_classes: list[Type['BaseRecord']] = []
topic_to_event: dict[str, Type['BaseRecord']] = {}


def create_random_event() -> 'BaseRecord':
    cls = faker.random.choice(event_classes)
    return cls.create_random()


def get_all_events() -> list[Type['BaseRecord']]:
    return event_classes


MAX_FILE_SIZE_BYTES = 1024 * 1024  # 1Мб


def process_message(message: pulsar.Message, hdfs_client: hdfs.Client, logger: logging.Logger, max_file_size_bytes=MAX_FILE_SIZE_BYTES):
    # 1. Сериализуем запись в CSV
    topic_name: str = message.topic_name()
    if topic_name.startswith('persistent://public/default/'):
        topic_name = topic_name.removeprefix('persistent://public/default/')
    cls = topic_to_event[topic_name]
    csv_row = cls.serialize_csv(message.value())

    # 2. Записываем запись в CSV файл
    csv_path = f'/tmp/{cls.filename()}'
    try:
        with open(csv_path, 'a') as file:
            file.write(csv_row)
            size_exceed = max_file_size_bytes < os.path.getsize(csv_path)
    except Exception as e:
        logger.critical('Ошибка во время записи CSV в файл %s', csv_path, exc_info=e)
        raise e

    # Если размер не превышен - завершаемся
    if not size_exceed:
        return

    # 3. Записываем файл в HDFS
    logger.info('Размер файла превысил максимальный. Отправляю в HDFS')
    hdfs_path = cls.filename()
    try:
        with open(csv_path, 'rb') as file:
            try:
                hdfs_client.write(hdfs_path, data=file, append=True)
            except hdfs.util.HdfsError:
                hdfs_client.write(hdfs_path, data=file, append=False)
    except Exception as e:
        logger.critical('Ошибка во время отправки чанка в HDFS', exc_info=e)
        raise e

    # 4. Удаляем старый файл (ставим размер в 0)
    try:
        with open(csv_path, 'w') as file:
            file.truncate(0)
    except Exception as e:
        logger.critical('Ошибка во время удаления большого файла', exc_info=e)
        raise e


@contextlib.contextmanager
def create_client(service_url='pulsar://localhost:6650') -> ContextManager[pulsar.Client]:
    client = pulsar.Client(service_url, authentication=pulsar.AuthenticationBasic(username='admin', password='apachepulsar'))
    try:
        yield client
    finally:
        client.close()


def get_all_topics():
    return [
        e.topic() for e in event_classes
    ]


class BaseRecord(Record):
    def __init_subclass__(cls):
        event_classes.append(cls)
        topic_to_event[cls.topic()] = cls

    @classmethod
    def filename(cls):
        return f'{cls.topic()}.csv'

    @classmethod
    def get_schema(cls) -> pulsar.schema.Schema:
        return pulsar.schema.JsonSchema(cls)

    @classmethod
    @abstractmethod
    def topic(cls):
        raise NotImplementedError()

    @classmethod
    def create_random(cls) -> 'BaseRecord':
        base = cls.create_custom_random()
        base.timestamp = (datetime.now() + timedelta(seconds=faker.random.randint(-10, 10))).strftime('%Y-%m-%d %H:%M:%S')
        base.user_id = faker.random.randint(0, 100)
        return base

    @classmethod
    @abstractmethod
    def create_custom_random(cls) -> 'BaseRecord':
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_custom_fields(cls, obj) -> list:
        raise NotImplementedError

    @classmethod
    def serialize_csv(cls, obj) -> str:
        s = io.StringIO()
        writer = csv.writer(s, delimiter=';', quotechar='"')
        fields = [
            obj.timestamp,
            obj.user_id
        ]
        fields.extend(cls.get_custom_fields(obj))
        writer.writerow(fields)
        return s.getvalue()


class PageVisit(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    page_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'page-visit'

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.page_id]

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = PageVisit()
        obj.page_id = faker.random.randint(0, 1000)
        return obj


class Searching(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    query = String(required=True)

    @classmethod
    def topic(cls):
        return 'searching'

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.query]

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = Searching()
        obj.query = ' '.join(faker.words(3))
        return obj


def random_nullable_double():
    if faker.boolean(30):
        return faker.random.random()
    return None


class Filtering(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    price_min = Double()
    price_max = Double()
    rating_min = Double()
    rating_max = Double()

    @classmethod
    def topic(cls):
        return 'filtering'

    @classmethod
    def get_custom_fields(cls, obj):
        return [
            obj.price_min, obj.price_max,
            obj.rating_min, obj.rating_max
        ]

    @classmethod
    def create_custom_random(cls):
        obj = Filtering()
        obj.price_min = random_nullable_double()
        obj.price_max = random_nullable_double()
        obj.rating_min = random_nullable_double()
        obj.rating_max = random_nullable_double()
        return obj


class CartAdd(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    item_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'cart-add'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = CartAdd()
        obj.item_id = faker.random.randint(0, 1000)
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [
            obj.item_id
        ]


class CartDelete(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    item_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'cart-delete'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = CartDelete()
        obj.item_id = faker.random.randint(0, 1000)
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.item_id]


class Ordering(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    order_id = Integer(required=True)

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = Ordering()
        obj.order_id = faker.random.randint(0, 1000)
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.order_id]

    @classmethod
    def topic(cls):
        return 'ordering'


class OrderCancel(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    order_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'order-cancel'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = OrderCancel()
        obj.order_id = faker.random.randint(0, 1000)
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.order_id]


class ReviewReview(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    review_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'review-review'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = ReviewReview()
        obj.review_id = faker.random.randint(0, 1000)
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.review_id]


class ReviewCreating(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    review_id = Integer(required=True)
    item_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'review-creating'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = ReviewCreating()
        obj.review_id = faker.random.randint(0, 1000)
        obj.item_id = faker.random.randint(0, 1000)
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [
            obj.review_id,
            obj.item_id
        ]


class Registering(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'registering'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        return Registering()

    @classmethod
    def get_custom_fields(cls, obj):
        return []


class LoginType:
    Email = 0
    OneTimePassword = 1
    External = 2


class LoggingIn(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    login_type = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'logging-in'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = LoggingIn()
        obj.login_type = faker.random.choice([LoginType.Email, LoginType.OneTimePassword, LoginType.External])
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.login_type]


class ProfileEdit(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'profile-edit'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        return ProfileEdit()

    @classmethod
    def get_custom_fields(cls, obj):
        return []


class SubscriptionType:
    All = 1
    NewsLetter = 2
    Sales = 3


class MailingSubscription(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    subscription_type = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'mailing-subscription'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = MailingSubscription()
        obj.subscription_type = faker.random.choice([SubscriptionType.All, SubscriptionType.Sales, SubscriptionType.NewsLetter])
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.subscription_type]


class SupportType:
    Email = 1
    Call = 2
    Chat = 3


class SupportContact(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    support_type = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'support-contact'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = SupportContact()
        obj.support_type = faker.random.choice([SupportType.Email, SupportType.Chat, SupportType.Call])
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.support_type]


class RecommendationView(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    duration_seconds = Double(required=True)

    @classmethod
    def topic(cls):
        return 'recommendation-view'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = RecommendationView()
        obj.duration_seconds = faker.random.random() * 100
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.duration_seconds]


class SaleParticipation(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    sale_id = Integer(required=True)
    item_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'sale-participation'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = SaleParticipation()
        obj.sale_id = faker.random.randint(0, 1000)
        obj.item_id = faker.random.randint(0, 1000)
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.sale_id, obj.item_id]


class ComparisonType:
    All = 0
    Price = 1
    Characteristics = 2
    DeliveryDate = 3


class ItemComparison(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    first_item_id = Integer(required=True)
    second_item_id = Integer(required=True)
    comparison_type = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'item-comparison'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = ItemComparison()
        obj.first_item_id = faker.random.randint(0, 1000)
        obj.second_item_id = faker.random.randint(0, 1000)
        obj.comparison_type = faker.random.choice([ComparisonType.All, ComparisonType.Price, ComparisonType.Characteristics, ComparisonType.DeliveryDate])
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [
            obj.first_item_id,
            obj.second_item_id,
            obj.comparison_type
        ]


class OrderHistoryViewing(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    duration_seconds = Double(required=True)

    @classmethod
    def topic(cls):
        return 'order-history-viewing'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = OrderHistoryViewing()
        obj.duration_seconds = faker.random.random() * 100
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [obj.duration_seconds]


class ReasonType:
    Another = 0
    Malfunction = 1
    Expired = 2
    Misfit = 3
    LowQuality = 4


class ItemReturn(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    item_id = Integer(required=True)
    order_id = Integer(required=True)
    reason_type = Integer(required=True)
    reason_user_message = String(required=False)

    @classmethod
    def topic(cls):
        return 'item-return'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = ItemReturn()
        obj.item_id = faker.random.randint(0, 1000)
        obj.order_id = faker.random.randint(0, 1000)
        reason_type = faker.random.choice([
            ReasonType.Misfit,
            ReasonType.Another,
            ReasonType.Expired,
            ReasonType.Malfunction,
            ReasonType.LowQuality
        ])
        obj.reason_type = reason_type
        if reason_type == ReasonType.Another:
            obj.reason_user_message = ' '.join(faker.words())
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [
            obj.item_id,
            obj.order_id,
            obj.reason_type,
            obj.reason_user_message
        ]


class PromoUsage(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    coupon_id = Integer(required=True)
    order_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'promo-usage'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = PromoUsage()
        obj.coupon_id = faker.random.randint(0, 1000)
        obj.order_id = faker.random.randint(0, 1000)
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [
            obj.coupon_id,
            obj.order_id
        ]


class CategoryView(BaseRecord):
    timestamp = String(required=True)
    user_id = Integer(required=True)
    category_id = Integer(required=True)
    parent_category_id = Integer()

    @classmethod
    def topic(cls):
        return 'category-view'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = CategoryView()
        obj.category_id = faker.random.randint(0, 1000)
        if faker.random.random() < 0.3:
            obj.parent_category_id = faker.random.randint(0, 1000)
        return obj

    @classmethod
    def get_custom_fields(cls, obj):
        return [
            obj.category_id,
            obj.parent_category_id
        ]
