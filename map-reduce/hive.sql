--- beeline
--- !connect jdbc:hive2://localhost:10000
--- user: root
--- pass: root

create table anime(id int, genre string, title string, status int)
comment 'Данные по просмотрам аниме'
row format delimited
fields terminated by ','
lines terminated by '\n'
stored as textfile;

load data inpath '/user/root/anime.csv'
overwrite into table anime;

select genre, count(*) as dropped
from anime
where status = 4
group by genre
order by dropped desc;

-- +----------------+----------+
-- |     genre      | dropped  |
-- +----------------+----------+
-- | comedy         | 4205     |
-- | action         | 3676     |
-- | romance        | 2394     |
-- | fantasy        | 2391     |
-- | school         | 2189     |
-- | shounen        | 2177     |
-- | drama          | 2070     |
-- | supernatural   | 1959     |
-- | adventure      | 1787     |
-- | sci-fi         | 1522     |
-- | slice of life  | 1283     |
-- | ecchi          | 1116     |
-- | mystery        | 995      |
-- | magic          | 947      |
-- | seinen         | 901      |
-- | super power    | 890      |
-- | harem          | 778      |
-- | psychological  | 554      |
-- | shoujo         | 540      |
-- | mecha          | 462      |
-- | historical     | 461      |
-- | demons         | 455      |
-- | horror         | 426      |
-- | military       | 391      |
-- | sports         | 347      |
-- | game           | 318      |
-- | martial arts   | 315      |
-- | parody         | 303      |
-- | music          | 257      |
-- | vampire        | 239      |
-- | thriller       | 201      |
-- | kids           | 144      |
-- | police         | 143      |
-- | samurai        | 131      |
-- | space          | 127      |
-- | shoujo ai      | 115      |
-- | josei          | 111      |
-- | hentai         | 78       |
-- | shounen ai     | 67       |
-- | dementia       | 57       |
-- | cars           | 12       |
-- | yaoi           | 9        |
-- | yuri           | 3        |
-- +----------------+----------+