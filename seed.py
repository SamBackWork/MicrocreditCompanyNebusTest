from app.database import SessionLocal
from app import models, schemas
from sqlalchemy.orm import Session


def seed_data(db: Session):
    # Добавляем активности
    activity_data = [
        {"name": "Еда", "parent_id": None},
        {"name": "Мясная продукция", "parent_id": 1},
        {"name": "Молочная продукция", "parent_id": 1},
        {"name": "Автомобили", "parent_id": None},
        {"name": "Грузовые", "parent_id": 4},
        {"name": "Легковые", "parent_id": 4},
        {"name": "Запчасти", "parent_id": 4},
        {"name": "Аксессуары", "parent_id": 7},
        {"name": "Электроника", "parent_id": None},
        {"name": "Компьютеры", "parent_id": 9},
        {"name": "Смартфоны", "parent_id": 9},
        {"name": "Бытовая техника", "parent_id": 9},
    ]

    activities_by_name = {}
    for act_data in activity_data:
        db_activity = models.Activity(name=act_data["name"])
        db.add(db_activity)
        db.flush()
        activities_by_name[act_data["name"]] = db_activity

    db.commit()

    for act_data in activity_data:
        if act_data["parent_id"] is not None:
            parent_name = None
            for a in activity_data:
                if a["parent_id"] is None:
                    continue
                if a["parent_id"] == 1 and act_data["parent_id"] == 1:
                    parent_name = "Еда"
                    break
                elif a["parent_id"] == 4 and act_data["parent_id"] == 4:
                    parent_name = "Автомобили"
                    break
                elif a["parent_id"] == 7 and act_data["parent_id"] == 4:
                    parent_name = "Запчасти"
                    break
                elif a["parent_id"] == 7 and act_data["parent_id"] == 7:
                    parent_name = "Аксессуары"
                    break
                elif a["parent_id"] == 9 and act_data["parent_id"] == 9:
                    parent_name = "Электроника"
                    break

            if parent_name is None:
                continue
            parent = activities_by_name[parent_name]
            current = activities_by_name[act_data["name"]]
            current.parent_id = parent.id
    db.commit()

    # Добавляем здания
    buildings = [
        {"address": "г. Москва, ул. Ленина 1, офис 3", "latitude": 55.7558, "longitude": 37.6176},
        {"address": "г. Санкт-Петербург, Невский пр., 28", "latitude": 59.9343, "longitude": 30.3351},
        {"address": "г. Новосибирск, ул. Советская, 15", "latitude": 55.0302, "longitude": 82.9204},
        {"address": "г. Екатеринбург, ул. Малышева, 51", "latitude": 56.8389, "longitude": 60.6057},
    ]

    buildings_by_address = {}
    for building_data in buildings:
        db_building = models.Building(**building_data)
        db.add(db_building)
        db.flush()
        buildings_by_address[building_data["address"]] = db_building

    db.commit()

    # Добавляем организации
    organizations = [
        {"name": "ООО 'Рога и Копыта'", "building_id": buildings_by_address["г. Москва, ул. Ленина 1, офис 3"].id,
         "phones": ["2-222-222", "3-333-333"], "activities": ["Мясная продукция", "Молочная продукция"]},
        {"name": "АвтоВАЗ", "building_id": buildings_by_address["г. Санкт-Петербург, Невский пр., 28"].id,
         "phones": ["8-800-555-35-35"], "activities": ["Легковые"]},
        {"name": "Молочный комбинат 'Буренка'",
         "building_id": buildings_by_address["г. Москва, ул. Ленина 1, офис 3"].id, "phones": ["4-444-444"],
         "activities": ["Молочная продукция"]},
        {"name": "Эльдорадо", "building_id": buildings_by_address["г. Новосибирск, ул. Советская, 15"].id,
         "phones": ["5-555-555"], "activities": ["Бытовая техника"]},
        {"name": "М.Видео", "building_id": buildings_by_address["г. Екатеринбург, ул. Малышева, 51"].id,
         "phones": ["6-666-666"], "activities": ["Компьютеры", "Смартфоны"]},
    ]

    for org_data in organizations:
        db_org = models.Organization(name=org_data["name"], building_id=org_data["building_id"])
        db.add(db_org)
        db.flush()

        for phone in org_data["phones"]:
            db_phone = models.OrganizationPhone(organization_id=db_org.id, phone_number=phone)
            db.add(db_phone)

        for activity_name in org_data["activities"]:
            activity = activities_by_name[activity_name]
            db_activity = models.OrganizationActivity(organization_id=db_org.id, activity_id=activity.id)
            db.add(db_activity)

    db.commit()


if __name__ == "__main__":
    db = SessionLocal()
    seed_data(db)
    db.close()
    print("Данные успешно добавлены!")
