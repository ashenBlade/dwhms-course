# Датасет доступен по http://snap.stanford.edu/data/twitch_gamers.zip
import logging
from csv import reader

from neo4j import GraphDatabase, Driver


def load_edges(driver: Driver):
    logger = logging.getLogger('load_edges')
    logger.info('Загружаю узлы')
    max_nodes = 168000
    node_count = 0
    with open('large_twitch_features.csv', 'r') as edges_file:
        r = reader(edges_file, delimiter=',')
        next(r)  # Пропускаем заголовок
        for row in r:
            node_count += 1
            views, mature, life_time, created_at, updated_at, numeric_id, dead_count, language, affiliate = row
            driver.execute_query('CREATE (node: USER {id: $id, mature: $mature, views: $views})',
                                 id=numeric_id, mature=mature, views=views)
            if node_count % 1000 == 0:
                logger.info('Загружено: %s%%', round((node_count / max_nodes) * 100))

    logger.info('Узлы загружены')


def load_vertices(driver: Driver):
    logger = logging.getLogger('load_vertices')
    logger.info('Загружаю связи между узлами')
    max_edges = 6797558
    edge_count = 0
    with open('large_twitch_edges.csv', 'r') as vertices_file:
        r = reader(vertices_file, delimiter=',')
        next(r)  # Пропускаем заголовок
        for row in r:
            edge_count += 1
            first_id, second_id = row[0], row[1]
            driver.execute_query('MATCH (u1:USER {id: $first_id}), (u2:USER {id: $second_id}) '
                                 'CREATE (u1)-[:PLAYS_WITH]->(u2), (u2)-[:PLAYS_WITH]->(u1)',
                                 first_id=first_id, second_id=second_id)

            if edge_count % 1000 == 0:
                logger.info('Загружено: %s%%', round((edge_count / max_edges) * 100))

    logger.info('Связи загружены')
# gds.degree.stream

# https://neo4j.com/docs/graph-data-science/current/algorithms/degree-centrality/
# https://graphdatascience.ninja/versions.json

# Для 5.13.0 neo4j
# https://graphdatascience.ninja/neo4j-graph-data-science-2.5.3.jar


def create_edge_index(driver: Driver):
    logger = logging.getLogger('create_edge_index')
    logger.info('Создаю индекс для ID пользователя')
    driver.execute_query('CREATE RANGE INDEX user_id_index IF NOT EXISTS FOR (u:USER) ON (u.id)')


def main():
    with GraphDatabase.driver('neo4j://localhost:7687', auth=('neo4j', 'password')) as driver:
        # load_edges(driver)
        # create_edge_index(driver)
        load_vertices(driver)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('Необработанное исключение')
        print(e)
