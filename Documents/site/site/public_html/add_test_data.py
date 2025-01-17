from main import app, db
from models import ServicedObject, RepairWork
from datetime import datetime

def add_test_objects():
    with app.app_context():
        # Тестовые объекты
        objects = [
            ServicedObject(
                address="ул. Ленина, 1",
                characteristics="5-этажный жилой дом, 4 подъезда",
                square_meters=3000.0,
                date_added=datetime.now()
            ),
            ServicedObject(
                address="ул. Пушкина, 15",
                characteristics="9-этажный жилой дом, 2 подъезда",
                square_meters=4500.0,
                date_added=datetime.now()
            )
        ]
        
        # Тестовые ремонтные работы
        repairs = [
            RepairWork(
                address="ул. Ленина, 1",
                work_type="Капитальный ремонт крыши",
                description="Полная замена кровельного покрытия",
                date_added=datetime.now()
            ),
            RepairWork(
                address="ул. Пушкина, 15",
                work_type="Ремонт подъезда",
                description="Косметический ремонт первого подъезда",
                date_added=datetime.now()
            )
        ]
        
        try:
            # Добавляем объекты
            for obj in objects:
                db.session.add(obj)
            
            # Добавляем ремонтные работы
            for repair in repairs:
                db.session.add(repair)
            
            db.session.commit()
            print("Тестовые данные успешно добавлены!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при добавлении данных: {e}")

if __name__ == "__main__":
    add_test_objects() 