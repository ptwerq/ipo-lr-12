from typing import List
from transport.vehicle import Vehicle
from transport.client import Client

# Класс транспортной компании
class TransportCompany:
    def __init__(self, name: str):
        self.name = name
        self.vehicles: List[Vehicle] = []  # Список транспорта
        self.clients: List[Client] = []    # Список клиентов

    # Добавление транспортного средства
    def add_vehicle(self, vehicle: Vehicle):
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Можно добавлять только Vehicle")
        self.vehicles.append(vehicle)
        print(f"Добавлен транспорт: {vehicle}")

    # Вывод списка всех транспортных средств
    def list_vehicles(self):
        return [str(v) for v in self.vehicles]

    # Добавление клиента
    def add_client(self, client: Client):
        if not isinstance(client, Client):
            raise TypeError("Можно добавлять только Client")
        self.clients.append(client)
        print(f"Добавлен клиент: {client}")

    # Оптимизация распределения грузов
    def optimize_cargo_distribution(self):
        # Сначала VIP клиенты
        sorted_clients = sorted(self.clients, key=lambda c: not c.is_vip)
        for client in sorted_clients:
            loaded = False
            # Ищем транспорт с доступным местом
            for vehicle in self.vehicles:
                if vehicle.load_cargo(client):
                    loaded = True
                    break
            if not loaded:
                print(f"Не удалось загрузить клиента {client.name}, не хватает места")