from transport.vehicle import Vehicle  # Импортируем базовый класс Vehicle

# Класс поезда
class Train(Vehicle):
    def __init__(self, capacity: float, number_of_cars: int):
        super().__init__(capacity)  # Вызываем конструктор базового класса
        # Проверяем, что число вагонов положительное целое
        if not isinstance(number_of_cars, int) or number_of_cars <= 0:
            raise ValueError("Количество вагонов должно быть положительным числом")
        self.number_of_cars = number_of_cars

    # Строковое представление поезда
    def __str__(self):
        return f"Поезд с {self.number_of_cars} вагонами, " + super().__str__()