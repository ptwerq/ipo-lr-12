from transport.vehicle import Vehicle
from transport.client import Client

# Создаём транспорт
v = Vehicle(10.0)

# Создаём клиента
c = Client("Пётр", 4.5)

# Загружаем клиента
v.load_cargo(c)

# Печатаем текущее состояние транспорта
print(v)