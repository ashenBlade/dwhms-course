import logging
import sys
from enum import Enum

from pyspark.sql import SparkSession


class WatchStatus(Enum):
    Dropped = 3


def main():
    logging.info('Подключаюсь к спарку')
    with SparkSession.builder.master('spark://localhost:7077').getOrCreate() as spark:
        logging.debug('Настраиваю конфигурацию')
        spark.conf.set('spark.sql.repl.eagerEval.enabled', True)
        logging.info('Читаю файл с данными')
        df = spark.read.csv('anime.csv', header=False, inferSchema=True, sep=',')
        print(spark)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as ki:
        pass
    except Exception as e:
        print('Необработанное исключение поймано')
        print(e)
        sys.exit(1)
