create table page_visits (
    timestamp datetime,
    user_id int,
    page_id int
) engine = MergeTree() order by timestamp;

create table searchings (
    timestamp datetime,
    user_id int,
    query String
) engine = MergeTree() order by timestamp;


create table filterings (
    timestamp datetime,
    user_id int,
    price_min double,
    price_max double,
    rating_min double,
    rating_max double
) engine = MergeTree() order by timestamp;

create table cart_adds (
    timestamp datetime,
    user_id int,
    item_id int
) engine = MergeTree() order by timestamp;

create table cart_deletes (
    timestamp datetime,
    user_id int,
    item_id int
) engine = MergeTree() order by timestamp;

create table orderings (
    timestamp datetime,
    user_id int,
    order_id int
) engine = MergeTree() order by timestamp;

create table order_cancels (
    timestamp datetime,
    user_id int,
    order_id int
) engine = MergeTree() order by timestamp;

create table review_reviews (
    timestamp datetime,
    user_id int,
    review_id int
) engine = MergeTree() order by timestamp;

create table review_creatings (
    timestamp datetime,
    user_id int,
    review_id int,
    item_id int
) engine = MergeTree() order by timestamp;

create table registerings (
    timestamp datetime,
    user_id int
) engine = MergeTree() order by timestamp;

create table logging_ins (
    timestamp datetime,
    user_id int,
    login_type int
) engine = MergeTree() order by timestamp;

create table profile_edits (
    timestamp datetime,
    user_id int
) engine = MergeTree() order by timestamp;

create table mailing_subscriptions (
    timestamp datetime,
    user_id int,
    subscription_type int
) engine = MergeTree() order by timestamp;

create table support_contacts (
    timestamp datetime,
    user_id int,
    support_type int
) engine = MergeTree() order by timestamp;

create table recommendation_views (
    timestamp datetime,
    user_id int,
    duration_seconds double
) engine = MergeTree() order by timestamp;

create table sale_participations (
    timestamp datetime,
    user_id int,
    sale_id int,
    item_id int
) engine = MergeTree() order by timestamp;

create table item_comparisons (
    timestamp datetime,
    user_id int,
    first_item_id int,
    second_item_id int,
    comparison_type int
) engine = MergeTree() order by timestamp;

create table order_history_viewings (
    timestamp datetime,
    user_id int,
    duration_seconds double
) engine = MergeTree() order by timestamp;

create table item_returns (
    timestamp datetime,
    user_id int,
    item_id int,
    order_id int,
    reason_type int,
    reason_user_message String
) engine = MergeTree() order by timestamp;

create table promo_usages (
    timestamp datetime,
    user_id int,
    coupon_id int,
    order_id int
) engine = MergeTree() order by timestamp;

create table category_views (
    timestamp datetime,
    user_id int,
    category_id int,
    parent_category_id int
) engine = MergeTree() order by timestamp;