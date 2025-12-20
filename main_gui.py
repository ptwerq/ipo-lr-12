import dearpygui.dearpygui as dpg

from transport.client import Client
from transport.truck import Truck
from transport.train import Train
from transport.company import TransportCompany


_company = None
LOG_TAG = "log_text"


def log(message: str):
    prev = dpg.get_value(LOG_TAG)
    dpg.set_value(LOG_TAG, prev + message + "\n")


def clear_log():
    dpg.set_value(LOG_TAG, "")


def create_company_callback(sender, app_data):
    global _company
    name = dpg.get_value("company_name").strip()
    if not name:
        log("Error: company name cannot be empty.")
        return
    try:
        _company = TransportCompany(name)
        clear_log()
        log(f"Company '{_company.name}' created.")
    except Exception as e:
        log(f"Error while creating company: {e}")


def add_truck_callback(sender, app_data):
    if _company is None:
        log("Error: create company first.")
        return
    capacity = dpg.get_value("truck_capacity")
    color = dpg.get_value("truck_color").strip()
    try:
        truck = Truck(capacity=capacity, color=color)
        _company.add_vehicle(truck)
        log(f"Truck added: {truck}")
    except Exception as e:
        log(f"Error while adding truck: {e}")


def add_train_callback(sender, app_data):
    if _company is None:
        log("Error: create company first.")
        return
    capacity = dpg.get_value("train_capacity")
    cars = dpg.get_value("train_cars")
    try:
        train = Train(capacity=capacity, number_of_cars=cars)
        _company.add_vehicle(train)
        log(f"Train added: {train}")
    except Exception as e:
        log(f"Error while adding train: {e}")


def add_client_callback(sender, app_data):
    if _company is None:
        log("Error: create company first.")
        return
    name = dpg.get_value("client_name").strip()
    weight = dpg.get_value("client_weight")
    is_vip = dpg.get_value("client_vip")
    try:
        client = Client(name=name, cargo_weight=weight, is_vip=is_vip)
        _company.add_client(client)
        log(f"Client added: {client}")
    except Exception as e:
        log(f"Error while adding client: {e}")


def optimize_callback(sender, app_data):
    if _company is None:
        log("Error: create company first.")
        return
    if not _company.clients:
        log("Warning: no clients.")
        return
    if not _company.vehicles:
        log("Warning: no vehicles.")
        return
    try:
        _company.optimize_cargo_distribution()
    except Exception as e:
        log(f"Error while optimizing: {e}")
        return

    clear_log()
    log(f"Cargo distribution for company '{_company.name}':")
    for vehicle in _company.vehicles:
        log(str(vehicle))
        if not getattr(vehicle, "clients_list", None):
            log("  No clients loaded.")
            continue
        for client in vehicle.clients_list:
            log(f"  - {client}")


def main():
    dpg.create_context()
    dpg.create_viewport(title="LR11 - GUI version", width=800, height=600)

    with dpg.window(label="Transport company", width=780, height=580):
        # Company
        dpg.add_text("Create transport company")
        dpg.add_input_text(label="Company name", tag="company_name")
        dpg.add_button(label="Create company", callback=create_company_callback)
        dpg.add_separator()

        # Vehicles
        dpg.add_text("Add vehicles")

        dpg.add_text("Truck")
        dpg.add_input_float(label="Truck capacity (tons)", tag="truck_capacity", default_value=10.0)
        dpg.add_input_text(label="Truck color", tag="truck_color", default_value="White")
        dpg.add_button(label="Add truck", callback=add_truck_callback)
        dpg.add_separator()

        dpg.add_text("Train")
        dpg.add_input_float(label="Train capacity (tons)", tag="train_capacity", default_value=100.0)
        dpg.add_input_int(label="Number of cars", tag="train_cars", default_value=10)
        dpg.add_button(label="Add train", callback=add_train_callback)
        dpg.add_separator()

        # Clients
        dpg.add_text("Add clients")
        dpg.add_input_text(label="Client name", tag="client_name")
        dpg.add_input_float(label="Cargo weight (tons)", tag="client_weight", default_value=1.0)
        dpg.add_checkbox(label="VIP client", tag="client_vip", default_value=False)
        dpg.add_button(label="Add client", callback=add_client_callback)
        dpg.add_separator()

        # Optimize
        dpg.add_button(label="Distribute cargo", callback=optimize_callback)
        dpg.add_separator()

        # Log
        dpg.add_input_text(label="Log", tag=LOG_TAG, multiline=True, readonly=True, width=750, height=150)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()