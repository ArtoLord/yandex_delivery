## Тестовое задание для поступления в школу backend-разработки
#### Развертывание
Скачиваем проект в `/srv/yandex_delivery/` на машине и передаем права на владение всеми файлами в ней `www-data`:
```bash
$ sudo chown -R www-data /srv/yandex_delivery/
```
Устанавливаем `postgres` и создаем базу данных для нашего проекта и пользователя для нее.
Создаем файл `/srv/yandex_delivery/prod_config.py` и заносим туда данные этой базы, а так-же меняем `DEBUG` на `True` и
добавляем имя хоста сервера в `ALLOWED_HOSTS`.
Создаем виртуальное окружение:
```bash
$ cd /srv/yandex_delivery/
$ python3 -m venv env
$ . env/bin/activate
$ pip install -r requirements.txt
```
Запускаем миграции:
```bash
$ export PROD=true
$ python manage.py migrate
```
Можно запустить тесты:
```bash
$ python manage.py test
```
Устанавливаем `nginx` и `uwsgi` и потом переносим конфиги в нужные папки:
```bash
$ sudo apt-get install uwsgi nginx
$ sudo ln -s /srv/yandex_delivery/conf/nginx.conf /etc/nginx/sites-enabled/delivery
$ sudo ln -s /srv/yandex_delivery/conf/uwsgi.ini /etc/uwsgi/apps-available/delivery.ini
$ sudo cp /srv/yandex_delivery/conf/delivery.service /etc/systemd/system/delivery.service
```
После этого можно запускать сервис:
```bash
$ sudo systemctl enable delivery
$ sudo systemctl start delivery
```