from transport.client import Client
from transport.truck import Truck
from transport.train import Train
from transport.company import TransportCompany

# Создаем компанию
company = TransportCompany("MegaTrans")

# Добавляем клиентов
company.add_client(Client("Иван", 5.0))
company.add_client(Client("Мария", 7.0, True))
company.add_client(Client("Пётр", 3.0))

# Добавляем транспорт
company.add_vehicle(Truck(10.0, "Красный"))
company.add_vehicle(Train(15.0, 3))

# Оптимизируем распределение грузов
company.optimize_cargo_distribution()

# Выводим все транспортные средства
for v in company.list_vehicles():
    print(v)