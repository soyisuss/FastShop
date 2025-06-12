import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import threading
import os
import subprocess
import platform
from camera.capture import get_image
from classifier.model import classify_product
from utils.mapping import get_product_info
from ticketing.ticket_generator import generate_ticket_pdf as generate_ticket


class FastShopGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FastShop - Sistema de Compra Automático")
        self.root.geometry("1200x800")

        # Variables
        self.cap = None
        self.is_running = False
        self.carrito = {}
        self.captured_images = []

        self.setup_ui()
        self.start_camera()

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Título
        title_label = ttk.Label(main_frame, text="FastShop Market",
                                font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Frame izquierdo - Cámara
        camera_frame = ttk.LabelFrame(
            main_frame, text="Vista de Cámara", padding="10")
        camera_frame.grid(row=1, column=0, sticky=(
            tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        self.camera_label = ttk.Label(camera_frame)
        self.camera_label.grid(row=0, column=0, pady=(0, 10))

        # Botones de control
        control_frame = ttk.Frame(camera_frame)
        control_frame.grid(row=1, column=0, pady=10)

        self.capture_btn = ttk.Button(control_frame, text="📷 Capturar Producto",
                                      command=self.capture_product, style="Accent.TButton")
        self.capture_btn.grid(row=0, column=0, padx=5)

        self.clear_btn = ttk.Button(control_frame, text="🗑️ Limpiar Carrito",
                                    command=self.clear_cart)
        self.clear_btn.grid(row=0, column=1, padx=5)

        # Frame derecho - Carrito y controles
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # Carrito
        cart_frame = ttk.LabelFrame(
            right_frame, text="Carrito de Compras", padding="10")
        cart_frame.grid(row=0, column=0, sticky=(
            tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        cart_frame.columnconfigure(0, weight=1)
        cart_frame.rowconfigure(0, weight=1)

        # Treeview para mostrar productos
        columns = ("Producto", "Cantidad", "Precio", "Subtotal")
        self.cart_tree = ttk.Treeview(
            cart_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=120, anchor=tk.CENTER)

        # Scrollbar para el treeview
        cart_scrollbar = ttk.Scrollbar(
            cart_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)

        self.cart_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        cart_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Total
        self.total_label = ttk.Label(cart_frame, text="Total: $0.00",
                                     font=("Arial", 14, "bold"))
        self.total_label.grid(row=1, column=0, columnspan=2, pady=10)

        # Status bar
        self.status_var = tk.StringVar(value="Listo para capturar productos")
        status_bar = ttk.Label(right_frame, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        # Frame inferior - Ticket
        ticket_frame = ttk.LabelFrame(
            main_frame, text="Ticket Generado", padding="10")
        ticket_frame.grid(row=2, column=0, columnspan=2,
                          sticky=(tk.W, tk.E), pady=(10, 0))

        ticket_control_frame = ttk.Frame(ticket_frame)
        ticket_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.generate_ticket_btn = ttk.Button(ticket_control_frame, text="🎫 Generar Ticket",
                                              command=self.generate_ticket, state=tk.DISABLED)
        self.generate_ticket_btn.grid(row=0, column=0, padx=5)

        self.open_ticket_btn = ttk.Button(ticket_control_frame, text="📄 Abrir Ticket",
                                          command=self.open_ticket, state=tk.DISABLED)
        self.open_ticket_btn.grid(row=0, column=1, padx=5)

        self.ticket_path_var = tk.StringVar()
        self.ticket_path_label = ttk.Label(ticket_control_frame, textvariable=self.ticket_path_var,
                                           foreground="blue")
        self.ticket_path_label.grid(row=0, column=2, padx=10, sticky=tk.W)

    def start_camera(self):
        """Iniciar la cámara"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara")
            return

        self.is_running = True
        self.update_camera()

    def update_camera(self):
        """Actualizar la vista de la cámara"""
        if self.is_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convertir de BGR a RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Redimensionar para la interfaz
                frame_rgb = cv2.resize(frame_rgb, (640, 480))

                # Agregar información en el frame
                cv2.putText(frame_rgb, f"Productos: {len(self.captured_images)}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame_rgb, "Presiona 'Capturar Producto'",
                            (10, frame_rgb.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Convertir a ImageTk
                image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image)

                self.camera_label.configure(image=photo)
                self.camera_label.image = photo

        # Programar la siguiente actualización
        if self.is_running:
            self.root.after(30, self.update_camera)

    def capture_product(self):
        """Capturar producto de la cámara"""
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cámara no disponible")
            return

        ret, frame = self.cap.read()
        if ret:
            # Guardar imagen
            os.makedirs("captured", exist_ok=True)
            from datetime import datetime
            filename = datetime.now().strftime("img_%Y%m%d_%H%M%S.jpg")
            path = os.path.join("captured", filename)
            cv2.imwrite(path, frame)

            self.captured_images.append(path)
            self.status_var.set(f"Imagen capturada: {filename}")

            # Procesar inmediatamente
            self.process_single_image(path)

    def process_single_image(self, image_path):
        """Procesar una sola imagen"""
        try:
            self.status_var.set("Clasificando producto...")

            # Ejecutar en hilo separado para no bloquear la UI
            threading.Thread(target=self._classify_image,
                             args=(image_path,), daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", f"Error procesando imagen: {e}")
            self.status_var.set("Error en clasificación")

    def _classify_image(self, image_path):
        """Clasificar imagen en hilo separado"""
        try:
            class_name = classify_product(image_path)
            product = get_product_info(class_name)

            # Actualizar carrito en el hilo principal
            self.root.after(0, self.add_to_cart, product)

        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))

    def add_to_cart(self, product):
        """Agregar producto al carrito"""
        key = product["name"]
        if key in self.carrito:
            self.carrito[key]["qty"] += 1
        else:
            self.carrito[key] = {
                "name": product["name"],
                "price": product["price"],
                "qty": 1
            }

        self.update_cart_display()
        self.status_var.set(f"Producto agregado: {product['name']}")

        # Habilitar botón de generar ticket
        if self.carrito:
            self.generate_ticket_btn.configure(state=tk.NORMAL)

    def update_cart_display(self):
        """Actualizar la visualización del carrito"""
        # Limpiar treeview
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        # Agregar productos
        total = 0
        for product in self.carrito.values():
            subtotal = product["price"] * product["qty"]
            total += subtotal

            self.cart_tree.insert("", tk.END, values=(
                product["name"],
                product["qty"],
                f"${product['price']:.2f}",
                f"${subtotal:.2f}"
            ))

        # Actualizar total
        self.total_label.configure(text=f"Total: ${total:.2f}")

    def clear_cart(self):
        """Limpiar el carrito"""
        self.carrito.clear()
        self.captured_images.clear()
        self.update_cart_display()
        self.status_var.set("Carrito limpiado")

        # Deshabilitar botones
        self.generate_ticket_btn.configure(state=tk.DISABLED)
        self.open_ticket_btn.configure(state=tk.DISABLED)
        self.ticket_path_var.set("")

    def generate_ticket(self):
        """Generar ticket PDF"""
        if not self.carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return

        try:
            self.status_var.set("Generando ticket...")

            # Generar ticket
            ticket_path = generate_ticket(list(self.carrito.values()))

            self.ticket_path_var.set(
                f"Ticket: {os.path.basename(ticket_path)}")
            self.open_ticket_btn.configure(state=tk.NORMAL)
            self.ticket_path = ticket_path

            self.status_var.set("Ticket generado exitosamente")
            messagebox.showinfo("Éxito", f"Ticket generado: {ticket_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Error generando ticket: {e}")
            self.status_var.set("Error generando ticket")

    def open_ticket(self):
        """Abrir el ticket PDF generado"""
        if hasattr(self, 'ticket_path') and os.path.exists(self.ticket_path):
            try:
                # Abrir PDF según el sistema operativo
                if platform.system() == "Darwin":  # macOS
                    subprocess.call(["open", self.ticket_path])
                elif platform.system() == "Windows":  # Windows
                    os.startfile(self.ticket_path)
                else:  # Linux
                    subprocess.call(["xdg-open", self.ticket_path])
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo abrir el ticket: {e}")
        else:
            messagebox.showerror("Error", "No hay ticket generado")

    def on_closing(self):
        """Manejar el cierre de la aplicación"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = FastShopGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
