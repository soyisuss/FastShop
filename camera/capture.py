import cv2
import os
from datetime import datetime


def get_image(save_dir="captured", show_preview=True):
    # Crear carpeta si no existe
    os.makedirs(save_dir, exist_ok=True)

    # Inicializa la cámara (0 es la webcam por defecto)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("No se pudo acceder a la cámara.")

    print("Presiona 'c' para capturar o 'q' para salir.")

    captured_img_path = None
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        if show_preview:
            cv2.imshow("Vista previa - Cámara", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):
            # Guardar imagen con timestamp
            filename = datetime.now().strftime("img_%Y%m%d_%H%M%S.jpg")
            path = os.path.join(save_dir, filename)
            cv2.imwrite(path, frame)
            print(f"Imagen guardada: {path}")
            captured_img_path = path
            break
        elif key == ord("q"):
            print("Captura cancelada.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured_img_path
