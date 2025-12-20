import re
from typing import Optional, List

import dearpygui.dearpygui as dpg

from transport.client import Client
from transport.truck import Truck
from transport.train import Train
from transport.company import TransportCompany


# --- Глобальные данные приложения --- #

company: Optional[TransportCompany] = None  # текущая транспортная компания

# Список клиентов и транспортных средств храним отдельно,
# чтобы удобно синхронизировать с таблицами.
clients: List[Client] = []
vehicles: List[object] = []  # Truck или Train

# Теги элементов интерфейса
CLIENT_TABLE_TAG = "clients_table"
VEHICLE_TABLE_TAG = "vehicles_table"
STATUS_TAG = "status_text"
LOG_TAG = "log_text"

# Для диалогов
CURRENT_CLIENT_INDEX: Optional[int] = None
CURRENT_VEHICLE_INDEX: Optional[int] = None

# Для экспорта результата
last_distribution_lines: List[str] = []


# --- Вспомогательные функции (лог, статус, сообщения) --- #

def set_status(msg: str) -> None:
    """Установить текст в статусной строке."""
    dpg.set_value(STATUS_TAG, msg)


def log(msg: str) -> None:
    """Добавить строку в текстовый лог внизу окна."""
    prev = dpg.get_value(LOG_TAG)
    dpg.set_value(LOG_TAG, prev + msg + "\n")


def clear_log() -> None:
    """Очистить лог."""
    dpg.set_value(LOG_TAG, "")


def show_error(message: str) -> None:
    """
    Показать модальное окно с ошибкой.
    Используется при нарушении правил валидации.
    """
    with dpg.window(label="Error", modal=True, no_title_bar=False,
                    no_resize=True, width=350, height=120, tag="error_dialog"):
        dpg.add_text(message)
        dpg.add_spacing(count=1)
        dpg.add_button(
            label="OK",
            width=60,
            callback=lambda s, a: dpg.delete_item("error_dialog")
        )
    set_status(message)


def show_about(sender, app_data) -> None:
    """Показать окно 'О программе'."""
    with dpg.window(label="About", modal=True, no_resize=True,
                    width=300, height=160, tag="about_dialog"):
        dpg.add_text("Laboratory work 11/13")
        dpg.add_text("Variant: 1")
        dpg.add_text("Developer: ФИО студента")
        dpg.add_spacing(count=1)
        dpg.add_button(
            label="OK",
            width=60,
            callback=lambda s, a: dpg.delete_item("about_dialog")
        )


# --- Валидация данных --- #

def validate_client_name(name: str) -> bool:
    """
    Имя клиента:
    - минимум 2 символа;
    - только буквы (русские или латинские).
    """
    name = name.strip()
    if len(name) < 2:
        show_error("Client name must have at least 2 letters.")
        return False
    if not re.fullmatch(r"[A-Za-zА-Яа-яЁё]+", name):
        show_error("Client name must contain only letters.")
        return False
    return True


def validate_client_weight(weight: float) -> bool:
    """
    Вес груза:
    - положительное число;
    - не более 10000 кг.
    """
    if weight <= 0:
        show_error("Cargo weight must be > 0.")
        return False
    if weight > 10000:
        show_error("Cargo weight must be <= 10000 kg.")
        return False
    return True


def validate_vehicle_capacity(capacity: float) -> bool:
    """Простая проверка грузоподъёмности транспорта."""
    if capacity <= 0:
        show_error("Vehicle capacity must be > 0.")
        return False
    return True


def validate_number_of_cars(cars: int) -> bool:
    """Количество вагонов поезда."""
    if cars <= 0:
        show_error("Number of cars must be > 0.")
        return False
    return True


# --- Обновление таблиц --- #

def refresh_clients_table() -> None:
    """Перерисовать таблицу клиентов по списку clients."""
    # Удаляем прошлые строки (child items)
    dpg.delete_item(CLIENT_TABLE_TAG, children_only=True)

    # Заново создаём заголовки
    with dpg.table_row(parent=CLIENT_TABLE_TAG):
        dpg.add_text("Name")
        dpg.add_text("Weight (kg)")
        dpg.add_text("VIP")

    # Строки с данными
    for c in clients:
        with dpg.table_row(parent=CLIENT_TABLE_TAG):
            dpg.add_text(c.name)
            dpg.add_text(f"{c.cargo_weight:.1f}")
            dpg.add_text("Yes" if c.is_vip else "No")


def refresh_vehicles_table() -> None:
    """Перерисовать таблицу транспортных средств по списку vehicles."""
    dpg.delete_item(VEHICLE_TABLE_TAG, children_only=True)

    with dpg.table_row(parent=VEHICLE_TABLE_TAG):
        dpg.add_text("ID")
        dpg.add_text("Type")
        dpg.add_text("Capacity (t)")
        dpg.add_text("Current load (t)")

    for v in vehicles:
        with dpg.table_row(parent=VEHICLE_TABLE_TAG):
            dpg.add_text(getattr(v, "vehicle_id", ""))
            v_type = "Truck" if isinstance(v, Truck) else "Train"
            dpg.add_text(v_type)
            dpg.add_text(f"{v.capacity:.1f}")
            dpg.add_text(f"{v.current_load:.1f}")


# --- Диалог клиента --- #

def open_client_dialog(sender=None, app_data=None, index: Optional[int] = None) -> None:
    """
    Открыть окно добавления/редактирования клиента.
    index = None -> новый клиент, иначе редактирование существующего.
    """
    global CURRENT_CLIENT_INDEX
    CURRENT_CLIENT_INDEX = index

    # Если редактирование — подставляем значения
    default_name = ""
    default_weight = 100.0
    default_vip = False
    if index is not None and 0 <= index < len(clients):
        c = clients[index]
        default_name = c.name
        default_weight = c.cargo_weight
        default_vip = c.is_vip

    if dpg.does_item_exist("client_dialog"):
        dpg.delete_item("client_dialog")

    with dpg.window(label="Client", modal=True, no_resize=True,
                    width=320, height=220, tag="client_dialog"):
        dpg.add_input_text(label="Client name", tag="dlg_client_name", default_value=default_name)
        dpg.add_input_float(label="Cargo weight (kg)", tag="dlg_client_weight",
                            default_value=float(default_weight), min_value=0, step=1)
        dpg.add_checkbox(label="VIP client", tag="dlg_client_vip", default_value=default_vip)

        dpg.add_spacing(count=1)
        dpg.add_button(label="Save", callback=save_client_from_dialog)
        dpg.add_same_line()
        dpg.add_button(label="Cancel", callback=lambda s, a: dpg.delete_item("client_dialog"))

def save_client_from_dialog(sender, app_data) -> None:
    """Считать поля диалога клиента, проверить и сохранить."""
    global company, clients

    name = dpg.get_value("dlg_client_name")
    weight = dpg.get_value("dlg_client_weight")
    is_vip = dpg.get_value("dlg_client_vip")

    # Валидация
    if not validate_client_name(name):
        dpg.set_value("dlg_client_name", "")
        return
    if not validate_client_weight(weight):
        dpg.set_value("dlg_client_weight", 0.0)
        return

    try:
        client_obj = Client(name=name, cargo_weight=weight, is_vip=is_vip)
    except Exception as e:
        show_error(f"Client creation error: {e}")
        return

    if CURRENT_CLIENT_INDEX is None:
        # Новый клиент
        clients.append(client_obj)
        if company:
            company.add_client(client_obj)
        log(f"Client added: {client_obj}")
    else:
        # Редактирование существующего
        idx = CURRENT_CLIENT_INDEX
        old = clients[idx]
        clients[idx] = client_obj
        if company:
            # Обновляем объект и в списке компании
            company.clients[idx] = client_obj
        log(f"Client updated: {old} -> {client_obj}")

    refresh_clients_table()
    dpg.delete_item("client_dialog")
    set_status("Client saved.")


# --- Диалог транспорта --- #

def open_vehicle_dialog(sender=None, app_data=None, index: Optional[int] = None) -> None:
    """
    Окно добавления/редактирования транспортного средства.
    Тип выбирается из списка: Truck / Train.
    """
    global CURRENT_VEHICLE_INDEX
    CURRENT_VEHICLE_INDEX = index

    default_type = "Truck"
    default_capacity = 10.0
    default_cars = 10

    if index is not None and 0 <= index < len(vehicles):
        v = vehicles[index]
        default_capacity = v.capacity
        if isinstance(v, Truck):
            default_type = "Truck"
        else:
            default_type = "Train"
        if isinstance(v, Train):
            default_cars = v.number_of_cars

    if dpg.does_item_exist("vehicle_dialog"):
        dpg.delete_item("vehicle_dialog")

    with dpg.window(label="Vehicle", modal=True, no_resize=True,
                    width=340, height=240, tag="vehicle_dialog"):
        dpg.add_combo(["Truck", "Train"], label="Vehicle type",
                      tag="dlg_vehicle_type", default_value=default_type)
        dpg.add_input_float(label="Capacity (t)", tag="dlg_vehicle_capacity",
                            default_value=float(default_capacity), min_value=0, step=1)
        dpg.add_input_int(label="Number of cars (for Train)",
                          tag="dlg_vehicle_cars", default_value=int(default_cars), min_value=1)

        dpg.add_spacing(count=1)
        dpg.add_button(label="Save", callback=save_vehicle_from_dialog)
        dpg.add_same_line()
        dpg.add_button(label="Cancel", callback=lambda s, a: dpg.delete_item("vehicle_dialog"))


def save_vehicle_from_dialog(sender, app_data) -> None:
    """Считать поля диалога транспорта, проверить и сохранить."""
    global company, vehicles

    v_type = dpg.get_value("dlg_vehicle_type")
    capacity = dpg.get_value("dlg_vehicle_capacity")
    cars = dpg.get_value("dlg_vehicle_cars")

    if not validate_vehicle_capacity(capacity):
        dpg.set_value("dlg_vehicle_capacity", 0.0)
        return

    if v_type == "Train":
        if not validate_number_of_cars(cars):
            dpg.set_value("dlg_vehicle_cars", 1)
            return

    # Создаём объект нужного типа
    try:
        if v_type == "Truck":
            vehicle_obj = Truck(capacity=capacity, color="White")
        else:
            vehicle_obj = Train(capacity=capacity, number_of_cars=cars)
    except Exception as e:
        show_error(f"Vehicle creation error: {e}")
        return

    if CURRENT_VEHICLE_INDEX is None:
        vehicles.append(vehicle_obj)
        if company:
            company.add_vehicle(vehicle_obj)
        log(f"Vehicle added: {vehicle_obj}")
    else:
        idx = CURRENT_VEHICLE_INDEX
        old = vehicles[idx]
        vehicles[idx] = vehicle_obj
        if company:
            company.vehicles[idx] = vehicle_obj
        log(f"Vehicle updated: {old} -> {vehicle_obj}")

    refresh_vehicles_table()
    dpg.delete_item("vehicle_dialog")
    set_status("Vehicle saved.")


# --- Удаление объектов --- #

def delete_selected_client(sender, app_data) -> None:
    """Удалить последнего клиента в списке (упрощённый вариант)."""
    global clients, company
    if not clients:
        set_status("No clients to delete.")
        return
    removed = clients.pop()
    if company and removed in company.clients:
        company.clients.remove(removed)
    refresh_clients_table()
    log(f"Client deleted: {removed}")
    set_status("Client deleted.")


def delete_selected_vehicle(sender, app_data) -> None:
    """Удалить последнее транспортное средство (упрощённый вариант)."""
    global vehicles, company
    if not vehicles:
        set_status("No vehicles to delete.")
        return
    removed = vehicles.pop()
    if company and removed in company.vehicles:
        company.vehicles.remove(removed)
    refresh_vehicles_table()
    log(f"Vehicle deleted: {removed}")
    set_status("Vehicle deleted.")


# --- Создание компании, оптимизация и экспорт --- #

def create_company() -> None:
    """Создать объект транспортной компании (один на всё приложение)."""
    global company
    if company is None:
        company = TransportCompany("My transport company")
        # Переносим уже введённые объекты в компанию
        for c in clients:
            company.add_client(c)
        for v in vehicles:
            company.add_vehicle(v)


def distribute_cargo(sender, app_data) -> None:
    """Запустить оптимизацию распределения грузов и показать результат."""
    global last_distribution_lines

    if not clients:
        show_error("No clients to distribute.")
        return
    if not vehicles:
        show_error("No vehicles to distribute.")
        return

    create_company()

    try:
        company.optimize_cargo_distribution()
    except Exception as e:
        show_error(f"Optimization error: {e}")
        return

    clear_log()
    last_distribution_lines = []
    log(f"Cargo distribution for company '{company.name}':")
    last_distribution_lines.append(f"Cargo distribution for company '{company.name}':")

    for v in company.vehicles:
        v_type = "Truck" if isinstance(v, Truck) else "Train"
        line = f"{v_type} {v.vehicle_id} | capacity={v.capacity} t, load={v.current_load} t"
        log(line)
        last_distribution_lines.append(line)
        if not v.clients_list:
            log("  No clients loaded.")
            last_distribution_lines.append("  No clients loaded.")
        else:
            for c in v.clients_list:
                c_line = f"  - {c.name}, {c.cargo_weight} t, VIP={c.is_vip}"
                log(c_line)
                last_distribution_lines.append(c_line)

    refresh_vehicles_table()
    set_status("Cargo distribution completed.")


def export_result(sender, app_data) -> None:
    """Сохранить результат распределения в файл."""
    if not last_distribution_lines:
        show_error("No distribution result to export.")
        return

    filename = "distribution_result.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for line in last_distribution_lines:
                f.write(line + "\n")
    except Exception as e:
        show_error(f"File save error: {e}")
        return

    set_status(f"Result exported to {filename}.")
    log(f"Result exported to {filename}.")


# --- Точка входа: построение интерфейса --- #

def main() -> None:
    dpg.create_context()
    dpg.create_viewport(title="LR11 / LR13 - GUI version", width=950, height=700)

    with dpg.window(label="Transport company", width=920, height=660):

        # Меню
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Export result", callback=export_result)
            with dpg.menu(label="Help"):
                dpg.add_menu_item(label="About", callback=show_about)

        # Панель управления объектами
        dpg.add_text("Control panel")
        dpg.add_button(label="Add client", callback=open_client_dialog)
        dpg.add_same_line()
        dpg.add_button(label="Add vehicle", callback=open_vehicle_dialog)
        dpg.add_same_line()
        dpg.add_button(label="Distribute cargo", callback=distribute_cargo)
        dpg.add_same_line()
        dpg.add_button(label="Delete client", callback=delete_selected_client)
        dpg.add_same_line()
        dpg.add_button(label="Delete vehicle", callback=delete_selected_vehicle)

        dpg.add_separator()

        # Таблица клиентов
        dpg.add_text("Clients")
        with dpg.table(tag=CLIENT_TABLE_TAG, header_row=False,
                       borders_innerH=True, borders_innerV=True,
                       borders_outerH=True, borders_outerV=True,
                       resizable=True, row_background=True,
                       policy=dpg.mvTable_SizingFixedFit):
            pass  # наполним в refresh_clients_table

        dpg.add_spacing(count=1)

        # Таблица транспортных средств
        dpg.add_text("Vehicles")
        with dpg.table(tag=VEHICLE_TABLE_TAG, header_row=False,
                       borders_innerH=True, borders_innerV=True,
                       borders_outerH=True, borders_outerV=True,
                       resizable=True, row_background=True,
                       policy=dpg.mvTable_SizingFixedFit):
            pass

        dpg.add_separator()

        # Лог и статус
        dpg.add_input_text(label="Log", tag=LOG_TAG, multiline=True,
                           readonly=True, width=-1, height=150)
        dpg.add_separator()
        dpg.add_text("Ready", tag=STATUS_TAG)

    # начальное заполнение таблиц (пока пустые заголовки)
    refresh_clients_table()
    refresh_vehicles_table()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()