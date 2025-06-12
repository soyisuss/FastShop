import cv2
import os
from datetime import datetime


def get_image(save_dir="captured", show_preview=True):
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("No se pudo acceder a la cámara.")

    print("Presiona 'c' para capturar, 'q' para salir.")
    print("Puedes capturar múltiples imágenes.")
    captured_images = []

    if show_preview:
        cv2.namedWindow("Vista previa - Cámara", cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("❌ Error leyendo el frame.")
                continue

            if show_preview:
                # Mostrar contador de imágenes capturadas
                cv2.putText(frame, f"Imagenes: {len(captured_images)}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "C: Capturar | Q: Salir",
                            (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.imshow("Vista previa - Cámara", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("c"):
                filename = datetime.now().strftime("img_%Y%m%d_%H%M%S.jpg")
                path = os.path.join(save_dir, filename)
                cv2.imwrite(path, frame)
                print(f"✅ Imagen {len(captured_images) + 1} guardada: {path}")
                captured_images.append(path)
                # NO hacer break aquí para continuar capturando
            elif key == ord("q"):
                print(
                    f"📷 Total de imágenes capturadas: {len(captured_images)}")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

    # Retornar la última imagen capturada o None si no se capturó ninguna
    return captured_images
