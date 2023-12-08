create table review_creating
(
    create_time timestamp,
    user_id int,
    review_id int,
    item_id int
)
    comment 'Создание отзывов'
    row format delimited
    fields terminated by ';'
    lines terminated by '\n'
    stored as textfile;

create table review_review
(
    create_time timestamp,
    user_id int,
    review_id int
)
    comment 'Просмотр отзывов'
    row format delimited
    fields terminated by ';'
    lines terminated by '\n'
    stored as textfile;

load data
    inpath '/user/root/review-creating.csv'
    into table review_creating;

load data
    inpath '/user/root/review-review.csv'
    into table review_review;