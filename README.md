# mail_reader
Читалка писем для интеграции почты с Telegram.

Пересылает тему письма, имя и адрес отправтеля, текст письма, список вложений, сами вложения (может не пересылать, это настраиваемый параметр в файле config.py).

## Устновка
Клонируете репозиторий на сервер.

Получаете пароль для внешних приложений (для mail.ru), создаёте бота и канал в ТГ, добавляете бота в канал, все данные вносите в файл config.py

Задаёте расписание исполнения файла main.py, вы прекарасны!

## Explanation notebook
Пошаговая демонстрация как в общих чертах всё работает.

Почитать на Хабре https://habr.com/ru/post/688784/

## Что добавлено
Добавлена функция проходки по всем папкам. 
Почта открывается только для чтения. 
UID отправленных в телеграм новых писем сохраняются в базе данных, чтобы не отправлять письма повторно.
