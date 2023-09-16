#!/usr/bin/env bash

# Перечисляем все файлы внутри корневой директории
hdfs dfs -ls / 2>/dev/null

# Создаем пустой текстовый файл
hdfs dfs -touchz /plain.txt

# Записываем текст в файл
echo "Hello, world!" > test.txt
hdfs dfs -appendToFile ./test.txt /plain.txt

# Читаем записанные данные
hdfs dfs -cat /plain.txt
