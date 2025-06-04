from camera.capture import get_image
from classifier.model import classify_product
from utils.mapping import get_product_info
from ticketing.ticket_generator import generate_ticket

if __name__ == "__main__":
    carrito = {}

    while True:
        path = get_image()
        if not path:
            break

        class_name = classify_product(path)
        product = get_product_info(class_name)

        key = product["name"]
        if key in carrito:
            carrito[key]["qty"] += 1
        else:
            carrito[key] = {
                "name": product["name"],
                "price": product["price"],
                "qty": 1
            }

        continuar = input("¿Capturar otro producto? (s/n): ").strip().lower()
        if continuar != "s":
            break

    generate_ticket(list(carrito.values()))
