import csv
import io
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import faker
import pulsar
from pulsar.schema import Record, String, Integer, Double


faker = faker.Faker(locale='ru')


class BaseRecord(ABC, Record):

    # __init_subclass__(cls):

    timestamp = String(required=True)
    user_id = Integer(required=True)

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
        base.timestamp = datetime.now() + timedelta(seconds=faker.random.randint(-10, 10))
        base.user_id = faker.random.randint(0, 100)
        return base

    @classmethod
    @abstractmethod
    def create_custom_random(cls) -> 'BaseRecord':
        raise NotImplementedError()

    @abstractmethod
    def get_custom_fields(self) -> list:
        raise NotImplementedError

    def serialize_csv(self) -> str:
        s = io.StringIO()
        writer = csv.writer(s, delimiter=';', quotechar='"')
        fields = [
            self.timestamp,
            self.user_id
        ]
        fields.extend(self.get_custom_fields())
        writer.writerow(fields)
        return s.getvalue()


class PageVisit(BaseRecord):
    page_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'page-visit'

    def get_custom_fields(self):
        return [self.page_id]

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = PageVisit()
        obj.page_id = faker.random.randint(0, 1000)
        return obj


class Searching(BaseRecord):
    query = String(required=True)

    @classmethod
    def topic(cls):
        return 'searching'

    def get_custom_fields(self):
        return [self.query]

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
    price_min = Double()
    price_max = Double()
    rating_min = Double()
    rating_max = Double()

    @classmethod
    def topic(cls):
        return 'filtering'

    def get_custom_fields(self):
        return [
            self.price_min, self.price_max,
            self.rating_min, self.rating_max
        ]

    def create_custom_random(self):
        obj = Filtering()
        obj.price_min = random_nullable_double()
        obj.price_max = random_nullable_double()
        obj.rating_min = random_nullable_double()
        obj.rating_max = random_nullable_double()
        return obj


class CartAdd(BaseRecord):
    item_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'cart-add'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = CartAdd()
        obj.item_id = faker.random.randint(0, 1000)
        return obj

    def get_custom_fields(self) -> list:
        return [
            self.item_id
        ]


class CartDelete(BaseRecord):
    item_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'cart-delete'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = CartDelete()
        obj.item_id = faker.random.randint(0, 1000)
        return obj

    def get_custom_fields(self) -> list:
        return [self.item_id]


class Ordering(BaseRecord):
    order_id = Integer(required=True)

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = Ordering()
        obj.order_id = faker.random.randint(0, 1000)
        return obj

    def get_custom_fields(self) -> list:
        return [self.order_id]

    @classmethod
    def topic(cls):
        return 'ordering'


class OrderCancel(BaseRecord):
    order_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'order-cancel'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = OrderCancel()
        obj.order_id = faker.random.randint(0, 1000)
        return obj

    def get_custom_fields(self) -> list:
        return [self.order_id]


class ReviewReview(BaseRecord):
    review_id = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'review-review'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = ReviewReview()
        obj.review_id = faker.random.randint(0, 1000)

    def get_custom_fields(self) -> list:
        return [self.review_id]


class ReviewCreating(BaseRecord):
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

    def get_custom_fields(self) -> list:
        return [
            self.review_id,
            self.item_id
        ]


class Registering(BaseRecord):
    @classmethod
    def topic(cls):
        return 'registering'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        return Registering()

    def get_custom_fields(self) -> list:
        return []


class LoginType:
    Email = 0
    OneTimePassword = 1
    External = 2


class LoggingIn(BaseRecord):
    login_type = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'logging-in'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = LoggingIn()
        obj.login_type = faker.random.choice([LoginType.Email, LoginType.OneTimePassword, LoginType.External])
        return obj

    def get_custom_fields(self) -> list:
        return [self.login_type]


class ProfileEdit(BaseRecord):
    @classmethod
    def topic(cls):
        return 'profile-edit'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        return ProfileEdit()

    def get_custom_fields(self) -> list:
        return []


class SubscriptionType:
    All = 1
    NewsLetter = 2
    Sales = 3


class MailingSubscription(BaseRecord):
    subscription_type = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'mailing-subscription'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = MailingSubscription()
        obj.subscription_type = faker.random.choice([SubscriptionType.All, SubscriptionType.Sales, SubscriptionType.NewsLetter])
        return obj

    def get_custom_fields(self) -> list:
        return [self.subscription_type]


class SupportType:
    Email = 1
    Call = 2
    Chat = 3


class SupportContact(BaseRecord):
    support_type = Integer(required=True)

    @classmethod
    def topic(cls):
        return 'support-contact'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = SupportContact()
        obj.support_type = faker.random.choice([SupportType.Email, SupportType.Chat, SupportType.Call])
        return obj

    def get_custom_fields(self) -> list:
        return [self.support_type]


class RecommendationView(BaseRecord):
    duration_seconds = Double(required=True)

    @classmethod
    def topic(cls):
        return 'recommendation-view'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = RecommendationView()
        obj.duration_seconds = faker.random.random() * 100
        return obj

    def get_custom_fields(self) -> list:
        return [self.duration_seconds]


class SaleParticipation(BaseRecord):
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

    def get_custom_fields(self) -> list:
        return [self.sale_id, self.item_id]


class ComparisonType:
    All = 0
    Price = 1
    Characteristics = 2
    DeliveryDate = 3


class ItemComparison(BaseRecord):
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

    def get_custom_fields(self) -> list:
        return [
            self.first_item_id,
            self.second_item_id,
            self.comparison_type
        ]


class OrderHistoryViewing(BaseRecord):
    duration_seconds = Double(required=True)

    @classmethod
    def topic(cls):
        return 'order-history-viewing'

    @classmethod
    def create_custom_random(cls) -> 'BaseRecord':
        obj = OrderHistoryViewing()
        obj.duration_seconds = faker.random.random() * 100
        return obj

    def get_custom_fields(self) -> list:
        return [self.duration_seconds]


class ReasonType:
    Another = 0
    Malfunction = 1
    Expired = 2
    Misfit = 3
    LowQuality = 4


class ItemReturn(BaseRecord):
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

    def get_custom_fields(self) -> list:
        return [
            self.item_id,
            self.order_id,
            self.reason_type,
            self.reason_user_message
        ]


class PromoUsage(BaseRecord):
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

    def get_custom_fields(self) -> list:
        return [
            self.coupon_id,
            self.order_id
        ]


class CategoryView(BaseRecord):
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

    def get_custom_fields(self) -> list:
        return [
            self.category_id,
            self.parent_category_id
        ]
