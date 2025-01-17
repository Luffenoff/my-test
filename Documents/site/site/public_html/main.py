from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
from flask_caching import Cache
import os
import sys
sys.path.append('/home/c/cd63130/site/env/lib/python3.10/site-packages/')
import sqlite3
import requests
import logging
from dotenv import load_dotenv
from database import create_table, add_user, update_user, get_user, get_db_connection
from functools import wraps 
from datetime import datetime, timedelta
import json
from threading import Thread  # Добавить импорт
import time  # Добавить импорт
from werkzeug.utils import secure_filename  # Добавить импорт
from extensions import db
from models import User, News, RepairWork, ServicedObject, SystemLog, Contacts  # Обновите импорт
from utils import encrypt_ip
import shutil
import logging.handlers
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from sqlalchemy.exc import SQLAlchemyError

# Инициализация Flask должна быть в начале файла, перед использованием app
if os.environ.get('TIMEWEBCLOUD_DOMAIN'):
    APPLICATION_ROOT = '/passenger_wsgi.py'
else:
    APPLICATION_ROOT = ''

app = Flask(__name__)

# Убедитесь, что путь к директории существует
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
if not os.path.exists(db_path):
    os.makedirs(db_path)

# Конфигурация
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['APPLICATION_ROOT'] = APPLICATION_ROOT
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False

# Определяем базовую директорию проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Определяем пути к базе данных
if os.environ.get('TIMEWEBCLOUD_DOMAIN'):
    SITE_ROOT = '/home/c/cd63130/site'
    INSTANCE_PATH = os.path.join(SITE_ROOT, 'public_html/instance')
    DB_PATH = os.path.join(INSTANCE_PATH, 'site.db')
    UPLOAD_FOLDER = os.path.join(INSTANCE_PATH, 'uploads')
    LOG_DIR = os.path.join(INSTANCE_PATH, 'logs')
else:
    INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
    DB_PATH = os.path.join(INSTANCE_PATH, 'site.db')
    UPLOAD_FOLDER = os.path.join(INSTANCE_PATH, 'uploads')
    LOG_DIR = os.path.join(INSTANCE_PATH, 'logs')

# Создаем необходимые директории
for path in [INSTANCE_PATH, UPLOAD_FOLDER, LOG_DIR]:
    try:
        os.makedirs(path, mode=0o755, exist_ok=True)
    except Exception as e:
        print(f"Ошибка создания директории {path}: {e}")

# Обновляем конфигурацию Flask
app.config.update(
    SQLALCHEMY_DATABASE_URI=f'sqlite:///{DB_PATH}',
    TEMPLATES_AUTO_RELOAD=True,
    SECRET_KEY='prk123',  # Используйте надежный секретный ключ
    WTF_CSRF_SECRET_KEY='123prk'  # Отдельный ключ для CSRF
)

# Инициализация базы данных
db.init_app(app)

# ПЕРЕМЕЩАЕМ проверку админа в функцию
def init_admin():
    try:
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin')
            user.set_password('admin')
            db.session.add(user)
            db.session.commit()
    except Exception as e:
        print(f"Error initializing admin: {e}")

# Вызываем функцию только при запуске сервера
if __name__ == "__main__":
    init_admin()
    app.run(debug=True)

# Импорт моделей после инициализации db
from models import News, RepairWork, ServicedObject, SystemLog, Contacts, User

# ВАЖНО: Определяем декоратор admin_required здесь, до всех маршрутов
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Для доступа к этой странице необходимо войти как администратор', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Создает соединение с базой данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        logging.error(f"Database connection error: {str(e)}")
        raise

def create_visits_table():
    """Создает таблицу посещений если её нет"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_url TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Таблица visits создана успешно")
    except Exception as e:
        print(f"Ошибка при создании таблицы visits: {e}")

# Настройка путей для логов (после инициализации Flask)
LOG_DIR = os.path.join(BASE_DIR, 'instance', 'logs')
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception as e:
    print(f"Ошибка создания директории логов: {e}")
    LOG_DIR = '/tmp/flask_logs'
    os.makedirs(LOG_DIR, exist_ok=True)

# Пути к файлам логов (используем абсолютные пути)
system_log_path = os.path.join(LOG_DIR, 'system.log')
site_log_path = os.path.join(LOG_DIR, 'site.log')
admin_log_path = os.path.join(LOG_DIR, 'admin.log')

# Создаем файлы логов если их нет
for log_file in [system_log_path, site_log_path, admin_log_path]:
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            pass  # Просто создаем файл если его нет
    except Exception as e:
        print(f"Ошибка создания файла лога {log_file}: {e}")

# Настройка логгеров
try:
    # Системный логгер
    system_logger = logging.getLogger('system')
    system_logger.setLevel(logging.ERROR)
    system_handler = logging.handlers.RotatingFileHandler(
        system_log_path,
        maxBytes=1024*1024,
        backupCount=5,
        encoding='utf-8',
        mode='a'
    )
    system_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    system_logger.addHandler(system_handler)

    # Логгер сайта
    site_logger = logging.getLogger('site')
    site_logger.setLevel(logging.INFO)
    site_handler = logging.handlers.RotatingFileHandler(
        site_log_path,
        maxBytes=1024*1024,
        backupCount=5,
        encoding='utf-8',
        mode='a'
    )
    site_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    site_logger.addHandler(site_handler)

    # Логгер администратора
    admin_logger = logging.getLogger('admin')
    admin_logger.setLevel(logging.INFO)
    admin_handler = logging.handlers.RotatingFileHandler(
        admin_log_path,
        maxBytes=1024*1024,
        backupCount=5,
        encoding='utf-8',
        mode='a'
    )
    admin_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    admin_logger.addHandler(admin_handler)

except Exception as e:
    print(f"Ошибка настройки логирования: {e}")
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

# Создаем таблицы ПОСЛЕ инициализации приложения и БД
with app.app_context():
    try:
        db.create_all()
        create_visits_table()
    except Exception as e:
        print(f"Ошибка создания таблиц: {e}")

# Глобальная переменная для хранения данных о погоде
weather_data = {
    'temp': 0,
    'description': 'Загрузка...',
    'updated_at': 'Загрузка...',
    'humidity': 0,
    'pressure': 0,
    'wind_speed': 0
}

def get_weather():
    API_KEY = '377436ab6abe65f7ba01a3442e683565'
    CITY = 'Perm'
    
    try:
        url = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=ru'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            weather_data.update({
                'temp': round(data['main']['temp']),
                'description': data['weather'][0]['description'],
                'updated_at': datetime.now().strftime('%H:%M'),
                'humidity': data['main']['humidity'],
                'pressure': round(data['main']['pressure'] * 0.750062),
                'wind_speed': round(data['wind']['speed'])
            })
            print("Погода успешно обновлена")
    except Exception as e:
        print(f"Ошибка получения погоды: {e}")

def update_weather_loop():
    """Функция периодического обновления погоды"""
    while True:
        get_weather()
        time.sleep(1800)  # Обновление каждые 30 минут

# Получаем погоду сразу при запуске
get_weather()

# Запускаем периодическое обновление в отдельном потоке
weather_thread = Thread(target=update_weather_loop, daemon=True)
weather_thread.start()

# Добавьте конфигурацию для загрузки файлов
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Функция проверки расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def archive_and_clean_logs():
    """Архивирует логи старше месяца и очищает основной файл логов"""
    try:
        archive_dir = os.path.join(BASE_DIR, 'instance', 'log_archives')
        os.makedirs(archive_dir, exist_ok=True)

        current_date = datetime.now()
        archive_filename = f'system_logs_{current_date.strftime("%Y_%m")}.log'
        archive_path = os.path.join(archive_dir, archive_filename)

        if os.path.exists(system_log_path):
            shutil.copy2(system_log_path, archive_path)

            # Очищаем базу данных от старых логов
            month_ago = current_date - timedelta(days=30)
            old_logs = SystemLog.query.filter(SystemLog.timestamp < month_ago).all()
            
            with open(archive_path, 'a', encoding='utf-8') as f:
                for log in old_logs:
                    f.write(f"{log.timestamp} - {log.action} - {log.category} - {log.description}\n")
            
            for log in old_logs:
                db.session.delete(log)
            db.session.commit()

            # Очищаем основной файл логов
            with open(system_log_path, 'w', encoding='utf-8') as f:
                f.write(f"Log file cleaned on {current_date}\n")

    except Exception as e:
        print(f"Ошибка архивации логов: {e}")



# Переименуем функцию before_request
@app.before_request
def log_page_visit():
    if not request.path.startswith('/static'):
        site_logger.info(f"Page visit: {request.path} - IP: {encrypt_ip(request.remote_addr)}")
        # Также сохраняем в базу данных
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO visits (page_url, ip_address)
                    VALUES (?, ?)
                ''', (request.path, request.remote_addr))
                conn.commit()
        except Exception as e:
            print(f"Ошибка при записи посещения: {e}")

@app.route("/manage_content")
@admin_required
def manage_content():
    news_items = News.query.order_by(News.date_posted.desc()).all()
    objects = ServicedObject.query.order_by(ServicedObject.date_added.desc()).all()
    repairs = RepairWork.query.order_by(RepairWork.date_added.desc()).all()
    daily_visits = get_daily_visits()
    chart_data = get_visits_chart_data()
    system_logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(100).all()
    
    return render_template('admin_dashboard.html', 
                         news_items=news_items,
                         objects=objects,
                         repairs=repairs,
                         daily_visits=daily_visits,
                         chart_data=chart_data,
                         system_logs=system_logs)

# Применяем декоратор к основным маршрутам
@app.route("/")
def home():
    try:
        news = News.query.order_by(News.date_posted.desc()).all()
        return render_template("index.html", news_items=news, weather=weather_data)
    except Exception as e:
        logging.error(f"Error in home: {e}")
        return render_template("index.html", news_items=[], weather=weather_data)

@app.route("/company")
def company():
    return render_template("company.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route('/repair-works')
def repair_works():
    try:
        repairs = RepairWork.query.order_by(RepairWork.date_added.desc()).all()
        return render_template('repair_works.html', repairs=repairs)
    except Exception as e:
        logging.error(f"Error in repair_works: {str(e)}")
        flash('Ошибка при загрузке данных', 'error')
        return render_template('repair_works.html', repairs=[])

@app.route('/serviced-objects')
def serviced_objects():
    try:
        objects = ServicedObject.query.order_by(ServicedObject.date_added.desc()).all()
        return render_template('serviced_objects.html', objects=objects)
    except Exception as e:
        logging.error(f"Error in serviced_objects: {str(e)}")
        flash('Ошибка при загрузке данных', 'error')
        return render_template('serviced_objects.html', objects=[])

@app.route("/objects")
def objects():
    # Получаем отсортированные по дате добавления записи
    repairs = RepairWork.query.order_by(RepairWork.date_added.desc()).all()
    serviced_objects = ServicedObject.query.order_by(ServicedObject.date_added.desc()).all()
    
    return render_template("objects.html", 
                         repairs=repairs,
                         objects=serviced_objects)

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

@app.route("/ad_user_required_root")
@admin_required
def ad_user_required_root():
    try:
        # Добавим отладочный вывод
        print("Loading admin dashboard...")
        
        news = News.query.order_by(News.date_posted.desc()).all()
        repairs = RepairWork.query.order_by(RepairWork.date_added.desc()).all()
        objects = ServicedObject.query.order_by(ServicedObject.date_added.desc()).all()
        
        # Отладочный вывод
        print(f"Found {len(news)} news items")
        print(f"Found {len(repairs)} repair items")
        print(f"Found {len(objects)} object items")

        return render_template(
            "admin_dashboard.html",
            news_items=news,
            repairs=repairs,
            objects=objects
        )
    except Exception as e:
        print(f"Error in ad_user_required_root: {str(e)}")  # Отладочный вывод
        logging.error(f"Error in ad_user_required_root: {e}")
        flash("Произошла ошибка при загрузке панели администратора", "error")
        return redirect(url_for('home'))

def init_db():
    try:
        create_table()  # существующая функция
        create_visits_table()  # новая функция для таблицы посещений
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

def get_db_connection():
    try:
        conn = sqlite3.connect('instance/site.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        raise
    
##if __name__ == "__main__":
    
# Добавить декоратор admin_required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Требуется авторизация администратора', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
    
    

# Добавьте эти маршруты после существующих
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            with app.app_context():  # Добавляем контекст приложения
                user = User.query.filter_by(username=username).first()
                
                if user and check_password_hash(user.password, password):
                    session['is_admin'] = True
                    flash('Вы успешно вошли в систему', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Неверное имя пользователя или пароль', 'error')
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            flash('Ошибка при входе в систему', 'error')
            return render_template('admin_login.html')
    
    return render_template('admin_login.html')

# Добавляем маршрут для выхода
@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('home'))

# Удаление новости
@app.route('/admin/delete_news/<int:news_id>', methods=['POST'])
@admin_required
def delete_news(news_id):
    try:
        news = News.query.get_or_404(news_id)
        db.session.delete(news)
        db.session.commit()
        flash('Новость удалена', 'success')
        log_action('delete', 'news', f'Удалена новость ID: {news_id}')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении новости', 'error')
        log_action('error', 'news', f'Ошибка удаления новости: {str(e)}')
    return redirect(url_for('admin_dashboard'))

# Удаление объекта
@app.route('/admin/delete_object/<int:object_id>', methods=['POST'])
@admin_required
def delete_object(object_id):
    try:
        obj = ServicedObject.query.get_or_404(object_id)
        db.session.delete(obj)
        db.session.commit()
        flash('Объект удален', 'success')
        log_action('delete', 'object', f'Удален объект ID: {object_id}')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении объекта', 'error')
        log_action('error', 'object', f'Ошибка удаления объекта: {str(e)}')
    return redirect(url_for('admin_dashboard'))

# Удаление ремонтных работ
@app.route("/delete_repair/<int:repair_id>", methods=['POST'])
@admin_required
def delete_repair(repair_id):
    try:
        repair = RepairWork.query.get_or_404(repair_id)
        log_action('delete', 'repair', f'Удалены ремонтные работы: {repair.address}')
        db.session.delete(repair)
        db.session.commit()
        flash('Ремонтные работы успешно удалены', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении ремонтных работ', 'error')
    return redirect(url_for('manage_content', _anchor='management'))

def get_daily_visits():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM visits 
                WHERE date(visit_date) = date('now')
            ''')
            result = cursor.fetchone()
            return result['count'] if result else 0
    except Exception as e:
        print(f"Error getting daily visits: {str(e)}")
        return 0

def get_visits_chart_data():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date(visit_date) as date, COUNT(*) as count 
                FROM visits 
                WHERE visit_date >= date('now', '-7 days')
                GROUP BY date(visit_date)
                ORDER BY date
            ''')
            results = cursor.fetchall()
            
            # Подготовка данных для графика
            dates = []
            counts = []
            for row in results:
                dates.append(row['date'])
                counts.append(row['count'])
                
            return {
                'labels': dates,
                'values': counts
            }
    except Exception as e:
        print(f"Error getting chart data: {str(e)}")
        return {'labels': [], 'values': []}

@app.route('/admin/update_contacts', methods=['POST'])
@admin_required
def update_contacts():
    try:
        contacts = Contacts.query.first()
        if not contacts:
            contacts = Contacts()
            db.session.add(contacts)
        
        contacts.phone = request.form.get('phone')
        contacts.email = request.form.get('email')
        contacts.address = request.form.get('address')
        contacts.working_hours = request.form.get('working_hours')
        
        db.session.commit()
        flash('Контактные данные обновлены', 'success')
        log_action('update', 'contacts', 'Обновлены контактные данные')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при обновлении контактов', 'error')
        log_action('error', 'contacts', f'Ошибка обновления контактов: {str(e)}')
    return redirect(url_for('admin_dashboard'))

def archive_and_clean_logs():
    """Архивирует логи старше месяца и очищает основной файл логов"""
    try:
        # Создаем директорию для архивов если её нет
        archive_dir = os.path.join('instance', 'log_archives')
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)

        current_date = datetime.now()
        archive_filename = f'system_logs_{current_date.strftime("%Y_%m")}.log'
        archive_path = os.path.join(archive_dir, archive_filename)

        # Копируем текущий файл логов в архив
        if os.path.exists('instance/system.log'):
            shutil.copy2('instance/system.log', archive_path)

            # Очищаем базу данных от старых логов
            month_ago = current_date - timedelta(days=30)
            old_logs = SystemLog.query.filter(SystemLog.timestamp < month_ago).all()
            
            # Сохраняем старые логи в архивный файл
            with open(archive_path, 'a', encoding='utf-8') as f:
                for log in old_logs:
                    f.write(f"{log.timestamp} - {log.action} - {log.category} - {log.description}\n")
            
            # Удаляем старые логи из базы данных
            for log in old_logs:
                db.session.delete(log)
            db.session.commit()

            # Очищаем основной файл логов
            with open('instance/system.log', 'w') as f:
                f.write(f"Log file cleaned on {current_date}\n")

            logging.info(f"Logs archived to {archive_filename}")
    except Exception as e:
        logging.error(f"Error archiving logs: {str(e)}")



# Настройка логирования системных событий
#system_logger = logging.getLogger('system')
#system_logger.setLevel(logging.INFO)
#system_handler = logging.FileHandler('instance/system.log')
#system_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
#system_logger.addHandler(system_handler)

# Настройка логирования активности сайта
#site_logger = logging.getLogger('site')
#site_logger.setLevel(logging.INFO)
#site_handler = logging.handlers.RotatingFileHandler(
   # 'instance/site_activity.log',  # Изменили имя файла
    #maxBytes=1024*1024,  # 1MB
   # backupCount=5
#)
#site_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#site_logger.addHandler(site_handler)

# Настройка логирования действий администратора
#admin_logger = logging.getLogger('admin')
#admin_logger.setLevel(logging.INFO)
#admin_handler = logging.FileHandler('instance/site_activity.log')
#admin_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
#admin_logger.addHandler(admin_handler)

# Функция логирования действий администратора
def log_action(action, category, description):
    try:
        encrypted_ip = encrypt_ip(request.remote_addr)
        log = SystemLog(
            action=action,
            category=category,
            description=description,
            ip_address=encrypted_ip
        )
        db.session.add(log)
        db.session.commit()

        # Записываем в лог действий администратора
        admin_logger.info(f"{action} - {category} - {description} - {encrypted_ip}")

    except Exception as e:
        system_logger.error(f"Error logging action: {str(e)}")

# Функция отслеживания посещений
@app.before_request
def track_visits():
    if not request.path.startswith('/static'):
        site_logger.info(f"Page visit: {request.path} - IP: {encrypt_ip(request.remote_addr)}")

@app.context_processor
def utility_processor():
    def fix_url(endpoint, **kwargs):
        if os.environ.get('TIMEWEBCLOUD_DOMAIN'):
            return url_for(endpoint, **kwargs).replace('/passenger_wsgi.py/passenger_wsgi.py', '/passenger_wsgi.py')
        return url_for(endpoint, **kwargs)
    return dict(url_for=fix_url)

# После создания app
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Добавьте маршруты для управления контентом

@app.route('/admin/add_news', methods=['POST'])
@admin_required
def add_news():
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        
        # Обработка фото, если оно есть
        photo_path = None
        if 'news_photo' in request.files:
            photo = request.files['news_photo']
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_path = filename

        news = News(
            title=title, 
            content=content, 
            photo_path=photo_path,
            date_posted=datetime.utcnow()
        )
        db.session.add(news)
        db.session.commit()
        flash('Новость успешно добавлена', 'success')
        log_action('add', 'news', f'Добавлена новость: {title}')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при добавлении новости', 'error')
        log_action('error', 'news', f'Ошибка добавления новости: {str(e)}')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_object', methods=['POST'])
@admin_required
def add_object():
    try:
        address = request.form.get('object_address')
        description = request.form.get('object_description')
        square_meters = float(request.form.get('square_meters'))
        
        obj = ServicedObject(
            address=address,
            characteristics=description,
            square_meters=square_meters,
            date_added=datetime.utcnow()
        )
        db.session.add(obj)
        db.session.commit()
        flash('Объект успешно добавлен', 'success')
        log_action('add', 'object', f'Добавлен объект: {address}')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при добавлении объекта', 'error')
        log_action('error', 'object', f'Ошибка добавления объекта: {str(e)}')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_repair', methods=['POST'])
@admin_required
def add_repair():
    try:
        address = request.form.get('repair_address')
        work_type = request.form.get('work_type')
        description = request.form.get('repair_description')
        
        repair = RepairWork(
            address=address,
            work_type=work_type,
            description=description,
            date_added=datetime.utcnow()
        )
        db.session.add(repair)
        db.session.commit()
        flash('Ремонтные работы успешно добавлены', 'success')
        log_action('add', 'repair', f'Добавлены работы: {work_type} по адресу {address}')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при добавлении ремонтных работ', 'error')
        log_action('error', 'repair', f'Ошибка добавления работ: {str(e)}')
    return redirect(url_for('admin_dashboard'))

# Обработка ошибок базы данных
@app.errorhandler(SQLAlchemyError)
def handle_db_error(error):
    logging.error(f"Database error: {str(error)}")
    flash('Ошибка базы данных', 'error')
    return redirect(url_for('admin_login'))

# Создание админа только если его нет
with app.app_context():
    db.create_all()
    
    # Создание админа только если его нет
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
    except Exception as e:
        print(f"Ошибка при проверке/создании админа: {e}")

