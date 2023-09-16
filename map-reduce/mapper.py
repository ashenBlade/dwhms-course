import abc
import csv
import logging
import sys

logger = logging.getLogger('mapper')

class RowResult(abc.ABC):
    @abc.abstractmethod
    def serialize(self) -> str:
        """
        Сериализовать в строку: "*anime_id*;*anime_id*=[*genre1*, *genre2*, ...]"
        Эта строка содержит разделенные ';' (либо)
         - ID аниме, просмотр которого бросили
         - ID аниме и список строк его жанров через запятую
        :return:
        """
        raise NotImplementedError()


class DroppedAnimeResult(RowResult):
    anime_id: str
    def __init__(self, anime_id):
        self.anime_id = anime_id

    def serialize(self) -> str:
        return f'{self.anime_id};'


class AnimeGenresResult(RowResult):
    genres: list[str]
    anime_id: str
    def __init__(self, anime_id, genres):
        self.anime_id = anime_id
        self.genres = genres

    def serialize(self) -> str:
        return f';{self.anime_id}={repr(self.genres)}'


def parse_row(row: str) -> RowResult | None:
    # проверяем, что не заголовок
    if row.startswith(('MAL_ID','user_id')):
        return None

    commas_count = row.count(',')
    if commas_count == 4:
        # user_id,anime_id,rating,watching_status,watched_episodes
        _, anime_id, _, status, _ = row.split(',')
        if status == '4':
            return DroppedAnimeResult(anime_id)
        return None

    if 30 <= commas_count:
        for row in csv.reader([row], quotechar='"', delimiter=','):
            genre_str = row[3]
            if (not genre_str) or genre_str == 'Unknown':
                return None
            anime_id = row[0]
            genres = [
                r.strip().lower()
                for r in genre_str.split(',')
            ]
            return AnimeGenresResult(anime_id, genres)

    raise ValueError('В переданной строке странное кол-во столбцов')


def extract_genres(row: str) -> list[str]:
    third_comma_index = None
    found_comma_count = 0
    for i, ch in enumerate(row):
        if ch == ',':
            if found_comma_count == 2:
                third_comma_index = i
                break
            found_comma_count += 1

    if third_comma_index is None:
        raise ValueError('Не удалось найти третью запятую')

    next_char = row[third_comma_index + 1]
    if next_char == '"':
        # Это список
        # Находим первую "
        first_quote_index = third_comma_index + 1
        # Находим вторую "
        second_quote_index = row.index('"', first_quote_index + 1)
        return row[(first_quote_index + 1):second_quote_index].split(',')
    else:
        # Это одно слово
        second_comma_index = row.index(',', third_comma_index + 1)
        return row[(third_comma_index + 1):second_comma_index]


def main():
    """
    animelist.csv
        user_id,anime_id,rating,watching_status,watched_episodes
        0,67,9,1,1
        0,6702,7,1,4

    anime.csv
        MAL_ID,Name,Score,Genres,English name,Japanese name,Type,Episodes,Aired,Premiered,Producers,Licensors,Studios,Source,Duration,Rating,Ranked,Popularity,Members,Favorites,Watching,Completed,On-Hold,Dropped,Plan to Watch,Score-10,Score-9,Score-8,Score-7,Score-6,Score-5,Score-4,Score-3,Score-2,Score-1
        1,Cowboy Bebop,8.78,"Action, Adventure, Comedy, Drama, Sci-Fi, Space",Cowboy Bebop,カウボーイビバップ,TV,26,"Apr 3, 1998 to Apr 24, 1999",Spring 1998,Bandai Visual,"Funimation, Bandai Entertainment",Sunrise,Original,24 min. per ep.,R - 17+ (violence & profanity),28.0,39,1251960,61971,105808,718161,71513,26678,329800,229170.0,182126.0,131625.0,62330.0,20688.0,8904.0,3184.0,1357.0,741.0,1580.0
    """
    for line in sys.stdin:
        try:
            result = parse_row(line)
            if result:
                print(result.serialize())
        except ValueError as ve:
            logger.debug("Ошибка при обработке строки: %s", line, exc_info=ve)


if __name__ == '__main__':
    main()
