from transport.client import Client
from transport.truck import Truck
from transport.train import Train
from transport.company import TransportCompany

# Создаём объект компании
company = TransportCompany("SuperTrans")

# Меню программы
while True:
    print("\nМеню:")
    print("1. Добавить клиента")
    print("2. Добавить транспорт")
    print("3. Показать все транспортные средства")
    print("4. Распределить грузы")
    print("5. Выход")

    choice = input("Выберите действие: ")

    # Добавление клиента
    if choice == "1":
        name = input("Имя клиента: ")
        weight = float(input("Вес груза: "))
        vip_input = input("VIP клиент? (y/n): ").lower()
        is_vip = vip_input == 'y'
        company.add_client(Client(name, weight, is_vip))

    # Добавление транспорта
    elif choice == "2":
        t_type = input("Тип транспорта (truck/train): ").lower()
        capacity = float(input("Грузоподъемность: "))
        if t_type == "truck":
            color = input("Цвет грузовика: ")
            company.add_vehicle(Truck(capacity, color))
        elif t_type == "train":
            cars = int(input("Количество вагонов: "))
            company.add_vehicle(Train(capacity, cars))

    # Показ всех транспортных средств
    elif choice == "3":
        for v in company.list_vehicles():
            print(v)

    # Оптимизация распределения грузов
    elif choice == "4":
        company.optimize_cargo_distribution()

    # Выход
    elif choice == "5":
        break