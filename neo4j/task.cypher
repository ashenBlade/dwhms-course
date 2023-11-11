// Использую алгоритм центроида для определения наиболее "властных" стримеров

// Создаем граф для дальнейшей работы - все USER, связанные PLAYS_WITH
CALL gds.graph.project(
  'twitchGraph',
  'USER',
  'PLAYS_WITH'
)

// Теперь запускаем алгоритм и находим топовых стримеров
CALL gds.degree.stream(
  'twitchGraph',
  {
      orientation: 'NATURAL'
  }
)
YIELD nodeId, score
RETURN nodeId, score // Выбираем только узел и его ранг
ORDER BY score DESC  // Сначала самые популярные
LIMIT 500 // Берем только 500


// Удаляем созданный граф
CALL gds.graph.drop('twitchGraph')