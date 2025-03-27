import cv2             # Biblioteca para processamento de imagens
import numpy as np     # Biblioteca para manipulação de arrays
import tkinter as tk   # Biblioteca para criar interfaces gráficas
from tkinter import filedialog, ttk  # Módulos específicos para abrir arquivos e widgets avançados
from PIL import Image, ImageTk       # Módulos para manipulação de imagens no Tkinter

def apply_filter(image, filter_type, value):
    """Aplica filtros básicos como brilho, contraste, desfoque, etc."""
    if filter_type == "Preto e branco":
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)     # Converte para escala de cinza
    elif filter_type == "Desfoque":
        value = max(1, value // 2 * 2 + 1)  # Garante que seja ímpar
        return cv2.GaussianBlur(image, (value, value), 0)  # Aplica desfoque gaussiano
    elif filter_type == "Brilho":
        return cv2.convertScaleAbs(image, alpha=1, beta=value)  # Ajusta brilho
    elif filter_type == "Contraste":
        return cv2.convertScaleAbs(image, alpha=value, beta=0)  # Ajusta contraste
    elif filter_type == "Nitidez":
        kernel = np.array([[0, -1, 0], [-1, value, -1], [0, -1, 0]])  # Kernel para nitidez
        return cv2.filter2D(image, -1, kernel)
    elif filter_type == "Saturação":
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)        # Converte para HSV
        hsv[..., 1] = np.clip(hsv[..., 1] + value, 0, 255)  # Ajusta a saturação
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)          # Converte de volta para BGR
    return image

def open_image():
    global img, img_display, img_previous
    file_path = filedialog.askopenfilename()
    if file_path:
        img = cv2.imread(file_path)                # Lê a imagem
        img_display = cv2.resize(img, (400, 400))  # Redimensiona para exibição
        img_previous = img_display.copy()
        show_original()

def show_original():
    """Exibe apenas a imagem original no painel antes."""
    img1 = cv2.cvtColor(img_previous, cv2.COLOR_BGR2RGB)
    im1 = Image.fromarray(img1)
    imgtk1 = ImageTk.PhotoImage(image=im1)
    panel_original.configure(image=imgtk1)
    panel_original.image = imgtk1
    panel_processed.configure(image="")  # Apaga a imagem processada
    panel_processed.image = None

def show_processed():
    """Exibe apenas a imagem processada no painel depois."""
    img2 = cv2.cvtColor(img_display, cv2.COLOR_BGR2RGB)
    im2 = Image.fromarray(img2)
    imgtk2 = ImageTk.PhotoImage(image=im2)
    panel_processed.configure(image=imgtk2)
    panel_processed.image = imgtk2

def apply_selected_filters():
    global img_display
    img_display = cv2.resize(img, (400, 400))
    for filter_type, var in filters.items():
        if var.get():
            value = sliders[filter_type].get()
            img_display = apply_filter(img_display, filter_type, value)
    show_processed()

def show_advanced_options():
    """Abre a janela de opções avançadas."""
    advanced_window = tk.Toplevel(root)
    advanced_window.title("Opções Avançadas")
    for process in ["Contorno", "Color Tools", "Ajustamento de posição", "Width", "Diâmetro", "Edge", "Pitch", "OCR", "EdgePixels", "Blob Count"]:
        tk.Button(advanced_window, text=process, command=lambda p=process: apply_advanced_processing(p)).pack()

def apply_advanced_processing(process_type):
    global img_display
    if process_type == "Contorno":
        gray = cv2.cvtColor(img_display, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        img_display = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    elif process_type == "Color Tools":
        img_display = cv2.applyColorMap(img_display, cv2.COLORMAP_JET)
    elif process_type == "Ajustamento de posição":
        img_display = cv2.flip(img_display, 1)
    show_processed()

# Criar janela principal
root = tk.Tk()
root.title("Processamento de Imagem")
root.geometry("1200x600")  # Aumentei a largura para acomodar as duas imagens

# Criar espaço para exibição de imagens antes/depois
panel_original = tk.Label(root, text="Antes")
panel_original.grid(row=0, column=1, padx=10, pady=10)

panel_processed = tk.Label(root, text="Depois")
panel_processed.grid(row=0, column=2, padx=10, pady=10)

# Frame para os controles
frame_controls = tk.Frame(root)
frame_controls.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

# Botão de abrir imagem
btn_open = tk.Button(frame_controls, text="Abrir Imagem", command=open_image)
btn_open.grid(row=0, column=0, pady=5)

# Filtros
filters = {"Preto e branco": tk.BooleanVar(), "Desfoque": tk.BooleanVar(), "Brilho": tk.BooleanVar(), "Contraste": tk.BooleanVar(), "Nitidez": tk.BooleanVar(), "Saturação": tk.BooleanVar()}
sliders = {}

row_index = 1
for filter_type in filters:
    tk.Checkbutton(frame_controls, text=filter_type, variable=filters[filter_type]).grid(row=row_index, column=0, sticky="w")
    slider = tk.Scale(frame_controls, from_=1, to=10, orient=tk.HORIZONTAL)
    slider.grid(row=row_index, column=1, padx=5)
    sliders[filter_type] = slider
    row_index += 1

# Botão para aplicar filtros
btn_apply_filters = tk.Button(frame_controls, text="Aplicar", command=apply_selected_filters)
btn_apply_filters.grid(row=row_index, column=0, columnspan=2, pady=5)

# Botão para restaurar a imagem original
btn_restore = tk.Button(frame_controls, text="Reverter para original", command=show_original)
btn_restore.grid(row=row_index + 1, column=0, columnspan=2, pady=5)

# Botão de opções avançadas
btn_advanced = tk.Button(frame_controls, text="Opções Avançadas", command=show_advanced_options)
btn_advanced.grid(row=row_index + 2, column=0, columnspan=2, pady=5)

root.mainloop()







