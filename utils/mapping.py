PRODUCT_CATALOG = {
    "crema":     {"name": "Crema Lala",     "price": 12.0},
    "jalapenos": {"name": "Jalapeños",      "price": 15.0},
    "leche":     {"name": "Leche Entera",   "price": 17.5},
    "maizena":   {"name": "Maizena",        "price": 8.0},
    "pelon":     {"name": "Pelón Pelo Rico", "price": 6.0}
}


def get_product_info(class_name):
    return PRODUCT_CATALOG.get(class_name, {"name": class_name, "price": 0.0})
