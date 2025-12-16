# Импортируем uuid для уникального ID транспорта
import uuid
from typing import List
from transport.client import Client  # Импорт класса Client

# Класс базового транспортного средства
class Vehicle:
    def __init__(self, capacity: float):
        # Генерация уникального идентификатора транспорта
        self.vehicle_id = str(uuid.uuid4())

        # Проверяем, что capacity — положительное число
        if not isinstance(capacity, (int, float)) or capacity <= 0:
            raise ValueError("Грузоподъемность должна быть положительным числом")
        self.capacity = capacity

        # Текущая загрузка (по умолчанию 0)
        self.current_load = 0.0

        # Список клиентов, чьи грузы загружены
        self.clients_list: List[Client] = []

    # Метод загрузки клиента
    def load_cargo(self, client: Client):
        # Проверяем, что передан объект Client
        if not isinstance(client, Client):
            raise TypeError("Можно загружать только объекты Client")
        
        # Проверяем, хватит ли места для груза
        if self.current_load + client.cargo_weight > self.capacity:
            print(f"Не хватает места для клиента {client.name}")
            return False

        # Добавляем клиента и увеличиваем текущую загрузку
        self.clients_list.append(client)
        self.current_load += client.cargo_weight
        print(f"Загружен клиент {client.name}, текущая загрузка: {self.current_load} т")
        return True

    # Строковое представление транспорта
    def __str__(self):
        return f"ID: {self.vehicle_id}, грузоподъемность: {self.capacity} т, текущая загрузка: {self.current_load} т"