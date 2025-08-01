# Установка и запуск локально

## 1. Клонировать репозиторий
```bash
git clone https://github.com/your-org/banner_project.git
cd banner_project
```


## 2. Создать и активировать виртуальное окружение
```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# или
.\.venv\Scripts\activate    # Windows PowerShell
```


## 3. Установка зависимостей
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
## 4. Применить миграции и собрать статику
```bash
cd banner_project
python manage.py migrate
python manage.py collectstatic --noinput
```