from datetime import datetime
import os


def generate_ticket(products, output_dir="tickets"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticket_name = f"ticket_{timestamp}.txt"
    ticket_path = os.path.join(output_dir, ticket_name)

    total = 0
    lines = [
        "=== TICKET DE COMPRA ===\n",
        f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
        "Productos:\n"
    ]

    for product in products:
        name = product["name"]
        price = product["price"]
        qty = product["qty"]
        subtotal = price * qty
        total += subtotal
        lines.append(f"- {name} x{qty} @ ${price:.2f} = ${subtotal:.2f}\n")

    lines.append(f"\nTOTAL: ${total:.2f}\n")
    lines.append("=========================\n")

    with open(ticket_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Ticket generado: {ticket_path}")
    return ticket_path
