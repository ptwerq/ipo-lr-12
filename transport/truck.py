from transport.vehicle import Vehicle  # Импортируем базовый класс Vehicle

# Класс грузовика, наследует Vehicle
class Truck(Vehicle):
    def __init__(self, capacity: float, color: str):
        super().__init__(capacity)  # Вызываем конструктор базового класса
        # Проверяем, что цвет — строка
        if not isinstance(color, str):
            raise TypeError("Цвет должен быть строкой")
        self.color = color

    # Строковое представление грузовика
    def __str__(self):
        return f"Грузовик {self.color}, " + super().__str__()