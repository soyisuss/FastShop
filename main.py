from camera.capture import get_image
from classifier.model import classify_product
from utils.mapping import get_product_info
from ticketing.ticket_generator import generate_ticket_pdf

if __name__ == "__main__":
    carrito = {}

    while True:
        image_paths = get_image()

        if not image_paths:
            print("No se capturaron imágenes. Saliendo...")
            break

        print(f"📸 Se capturaron {len(image_paths)} imágenes. Procesando...")

        for i, path in enumerate(image_paths, 1):
            print(f"\n🔍 Procesando imagen {i}/{len(image_paths)}: {path}")

            try:
                class_name = classify_product(path)
                product = get_product_info(class_name)

                print(
                    f"✅ Producto detectado: {product['name']} - ${product['price']}")

                key = product["name"]
                if key in carrito:
                    carrito[key]["qty"] += 1
                    print(f"   Cantidad actualizada: {carrito[key]['qty']}")
                else:
                    carrito[key] = {
                        "name": product["name"],
                        "price": product["price"],
                        "qty": 1
                    }
                    print(f"   Producto agregado al carrito")

            except Exception as e:
                print(f"❌ Error procesando imagen {i}: {e}")
                continue

        print(f"\n🛒 Carrito actual ({len(carrito)} productos diferentes):")
        for item in carrito.values():
            print(
                f"   - {item['name']}: {item['qty']} x ${item['price']} = ${item['qty'] * item['price']}")

        continuar = input("\n¿Capturar más productos? (s/n): ").strip().lower()
        if continuar != "s":
            break

    if carrito:
        print("\n🎫 Generando ticket...")
        generate_ticket_pdf(list(carrito.values()))
    else:
        print("🛒 Carrito vacío. No se generará ticket.")
