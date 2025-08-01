# Продакшен-деплой (Server)

В этом разделе мы опишем, как развернуть и поддерживать BannerProject на Debian-сервере с Gunicorn + systemd + Nginx.

> - Репозиторий находится в `/srv/publicationinfo/banner_project`  
> - Виртуальное окружение — `/srv/publicationinfo/banner_project/venv`  
> - `manage.py` лежит в `/srv/publicationinfo/banner_project/banner_project/manage.py`  
> - systemd-unit: `banner_project.service` (работает от `root`, указывает `DJANGO_SETTINGS_MODULE=banner_project.settings.prod`, `WorkingDirectory=/srv/.../banner_project/banner_project`)  
> - Nginx отдаёт статику по `/static/` с алиасом на `/srv/publicationinfo/banner_project/staticfiles/`  
> - Домен — `publicationinfo.online`

---

## 1. Подготовка кода

```bash
# зайти в папку проекта (где лежит requirements.txt и папка banner_project/)
cd /srv/publicationinfo/banner_project
```

## 2. Виртуальное окружение и зависимости
```bash
# создаём venv, если его нет
python3 -m venv venv

# активируем
source venv/bin/activate

# обновляем pip и ставим зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Настройки окружения

В проде проект берёт настройки из модуля banner_project.settings.prod, all-hosts и CSRF прописаны в settings/prod.py, поэтому дополнительных .env files обычно не нужно.
Если понадобится добавить что-то ещё, можно экспортировать переменные в ExecStart через Environment= в systemd-юните.

## 4. Миграции и статика
```bash
# ещё внутри venv
cd banner_project
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```
Это создаст (или обновит) файлы в /srv/publicationinfo/banner_project/staticfiles/.

## 5. Перезапуск сервисов
```bash
# перезагружаем systemd-конфигурацию (если меняли unit)
sudo systemctl daemon-reload

# рестарт Gunicorn
sudo systemctl restart banner_project.service

# проверяем статус
sudo systemctl status banner_project.service

# перезагрузка Nginx (если меняли конфиг)
sudo systemctl reload nginx
```

## 6. Основная информаци

Откройте в браузере https://publicationinfo.online/ — основное приложение.

Откройте https://publicationinfo.online/admin — доступ к админке.

В логах `sudo journalctl -u banner_project -f` и `sudo tail -f /var/log/nginx/error.log` следите за ошибками.