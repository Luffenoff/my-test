from main import app, db
from models import News, RepairWork, ServicedObject
from datetime import datetime

def init_data():
    with app.app_context():
        # Добавляем новости
        news_items = [
            News(
                title='Плановые работы по обслуживанию',
                content='В доме по адресу ул. Ленина, 10 будут проводиться плановые работы по обслуживанию системы отопления.',
                date_posted=datetime.now()
            ),
            News(
                title='Уборка придомовой территории',
                content='Выполнены работы по уборке придомовой территории на всех обслуживаемых объектах.',
                date_posted=datetime.now()
            ),
            News(
                title='Установка видеонаблюдения',
                content='Завершены работы по установке системы видеонаблюдения в доме по адресу Проспект Мира, 22.',
                date_posted=datetime.now()
            )
        ]

        # Добавляем ремонтные работы
        repair_works = [
            RepairWork(
                work_type='Сварочные работы',
                address='ул. Ленина, 10',
                description='Ремонт труб отопления'
            ),
            RepairWork(
                work_type='Ремонт помещений',
                address='ул. Пушкина, 15',
                description='Косметический ремонт подъезда'
            ),
            RepairWork(
                work_type='Ремонт электрооборудования',
                address='Проспект Мира, 22',
                description='Замена проводки'
            ),
            RepairWork(
                work_type='Кровельные работы',
                address='ул. Ленина, 10',
                description='Ремонт кровли'
            ),
            RepairWork(
                work_type='Установка и ремонт счётчиков',
                address='ул. Пушкина, 15',
                description='Установка общедомовых приборов учета'
            )
        ]

        # Добавляем обслуживаемые объекты
        serviced_objects = [
            ServicedObject(
                address='Улица Ленина, дом 10',
                characteristics='5-этажный жилой дом, 4 подъезда',
                square_meters=3500.0
            ),
            ServicedObject(
                address='Проспект Мира, дом 22',
                characteristics='9-этажный жилой дом, 2 подъезда',
                square_meters=4200.0
            ),
            ServicedObject(
                address='Улица Пушкина, дом 15',
                characteristics='5-этажный жилой дом, 3 подъезда',
                square_meters=2800.0
            )
        ]

        try:
            # Добавляем все данные в базу
            db.session.add_all(news_items)
            db.session.add_all(repair_works)
            db.session.add_all(serviced_objects)
            db.session.commit()
            print("Данные успешно добавлены в базу")
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при добавлении данных: {str(e)}")

if __name__ == "__main__":
    init_data() 