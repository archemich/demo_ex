#  Демонстрационный экзамен
Необходимо создать рабочее пространство, позволяющее проводить тестирование новой технологии, такой как искусственный интеллект. Реализовать базу данных для внесения данных тестирования.
Необходимо протестировать виртуальную сеть используя созданные участником технологии. Для этой задачи участник создаёт систему управления объектами сети. А также разрабатывает алгоритмы искусственного интеллекта для системы управления.
В заключении участник проводит тестирование своей интеллектуальной системы управления. Составляет презентацию проделанной работы и создаёт инструкцию по использованию программы.

Выполнил студент группы КТбо3-11 Неприн Михаил Андреевич.

## Инструкция по установке
В терминале перейти в [папку проекта](/production/demo_ex) и вызвать команду
установки проекта через пакетный менеджер pip:
```shell
pip3 install -e .
``` 
Ключ -e обязателен, так как копирование файлов ресурсов в пакет не предусмотрено.

## Как использовать
Открыть проект можно с помощью команды:
```shell
demo_ex
``` 

Приложение поддерживает передачу аргументов и требует несколько обязательный аргументов:
- `--sqlite3` - Путь к файлу базы данных sqlite3, которая может быть еще не создана.
- `--neat-config` -  Путь к конфигурационному файлу Neat.
- `--drop` - Опциональный флаг, если нужно сбросить данные хранящиеся в базе данных.

Пример запуска программы:
```shell
demo_ex --sqlite3 .\demo_ex\data\db.sqlite3 --neat-config .\demo_ex\data\neat_config.txt
```
