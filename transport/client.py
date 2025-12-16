# Импортируем стандартные типы для аннотации
from typing import Union

# Класс для представления клиента
class Client:
    def __init__(self, name: str, cargo_weight: Union[int, float], is_vip: bool = False):
        # Проверяем, что имя — строка
        if not isinstance(name, str):
            raise TypeError("Имя клиента должно быть строкой")
        self.name = name

        # Проверяем, что вес груза — положительное число
        if not isinstance(cargo_weight, (int, float)) or cargo_weight < 0:
            raise ValueError("Вес груза должен быть положительным числом")
        self.cargo_weight = cargo_weight

        # Проверяем, что is_vip — булево значение
        if not isinstance(is_vip, bool):
            raise TypeError("is_vip должен быть булевым значением")
        self.is_vip = is_vip

    # Строковое представление клиента
    def __str__(self):
        vip_status = "VIP" if self.is_vip else "обычный"
        return f"Клиент {self.name}, вес груза: {self.cargo_weight} т, статус: {vip_status}"