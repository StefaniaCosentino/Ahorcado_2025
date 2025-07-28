import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import string # Para obtener el abecedario

# Diccionario de categorías y palabras
PALABRAS_POR_CATEGORIA = {
    "Geología": [
        "Mineral", "Roca", "Falla", "Volcán", "Terremoto",
        "Erosión", "Glaciar", "Sedimento", "Fósil", "Magma",
        "Lava", "Corteza", "Manto", "Núcleo", "Geólogo"
    ],
    "Estados de Animo": [
        "Alegría", "Tristeza", "Enojo", "Miedo", "Sorpresa",
        "Calma", "Ansiedad", "Felicidad", "Melancolía", "Optimismo",
        "Pesimismo", "Aburrimiento", "Entusiasmo", "Frustración", "Esperanza"
    ],
    "Nombres de Personas": [
        "Sofía", "Martín", "Valentina", "Mateo", "Camila",
        "Santiago", "Lucía", "Benjamín", "Isabella", "Lucas",
        "Emma", "Julián", "Agustina", "Nicolás", "Catalina"
    ]
}

# --- CONFIGURACIÓN DE RECURSOS ---
IMAGEN_FONDO_INICIO_PATH = "imagen_first_time.png.jpg"  # Imagen para la pantalla de inicio
MUSICA_INICIO_PATH = "musica_inicio.mp3"        # Música para la pantalla de inicio

IMAGEN_FONDO_INSTRUCCIONES_PATH = "instrucciones_fondo.png" # Nueva imagen para instrucciones
MUSICA_INSTRUCCIONES_PATH = "musica_instrucciones.mp3"   # Nueva música para instrucciones

# ¡NUEVOS RECURSOS PARA LA PANTALLA "LISTO PARA JUGAR"!
IMAGEN_FONDO_LISTO_PATH = "listo_para_jugar_fondo.png" # Ruta de la nueva imagen para "Listo para Jugar"
MUSICA_LISTO_PATH = "musica_listo.mp3"               # Ruta de la nueva música para "Listo para Jugar"

pygame.mixer.init()

def reproducir_musica(ruta_musica):
    """Reproduce la música de fondo en bucle desde una ruta específica."""
    try:
        pygame.mixer.music.load(ruta_musica)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Error al cargar o reproducir música: {e}")
        messagebox.showerror("Error de Sonido", f"No se pudo cargar o reproducir la música de fondo: {ruta_musica}. Asegúrate de que el archivo existe y es compatible.")

def detener_musica():
    """Detiene la música de fondo."""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

# Variables globales para las ventanas
ventana_inicio = None
ventana_instrucciones = None
ventana_listo_para_jugar = None
ventana_juego_real = None

# --- Variables globales para el estado del juego ---
palabra_secreta = ""
letras_adivinadas = []
letras_incorrectas = []
vidas_restantes = 7
botones_letras = {} # Diccionario para almacenar los botones de letras
canvas_ahorcado = None # Variable global para el canvas del ahorcado

# --- Labels para actualizar en el juego ---
label_palabra = None
label_vidas = None
label_letras_incorrectas = None
label_feedback = None # Nuevo label para mensajes de feedback

def dibujar_ahorcado(canvas, etapa_actual):
    """
    Dibuja la base del ahorcado y partes del cuerpo según la etapa_actual (vidas_restantes).
    0 vidas = ahorcado completo. 7 vidas = solo la base.
    """
    canvas.delete("all") # Limpia el canvas antes de redibujar

    # Dimensiones del Canvas
    ancho_canvas = canvas.winfo_width() # Obtener el ancho actual del canvas
    alto_canvas = canvas.winfo_height() # Obtener el alto actual del canvas

    # Puntos de referencia para el dibujo (ajustados para ser proporcionales)
    base_x1 = ancho_canvas * 0.1
    base_y = alto_canvas * 0.9
    base_x2 = ancho_canvas * 0.5

    poste_x = base_x1 + (base_x2 - base_x1) / 2 # Centro de la base para el poste
    poste_y = alto_canvas * 0.1

    viga_x = ancho_canvas * 0.7 # Extremo derecho de la viga
    viga_y = poste_y

    cuerda_x = viga_x - ancho_canvas * 0.1 # Donde baja la cuerda (ajuste)
    cuerda_y = poste_y + 30 # Largo inicial de la cuerda

    # Base (suelo)
    canvas.create_line(base_x1, base_y, base_x2, base_y, width=4)

    # Poste vertical
    canvas.create_line(poste_x, base_y, poste_x, poste_y, width=4)

    # Viga horizontal
    canvas.create_line(poste_x, poste_y, viga_x, viga_y, width=4)

    # Soporte diagonal
    canvas.create_line(poste_x, poste_y + 20, poste_x + 20, poste_y, width=4)

    # Cuerda
    canvas.create_line(cuerda_x, viga_y, cuerda_x, cuerda_y, width=3)

    # Aquí iría la lógica para dibujar el cuerpo si la etapa_actual lo requiere,
    # pero el usuario pidió solo la base al inicio.
    # Por ejemplo:
    # if etapa_actual <= 6: # Cabeza
    #     canvas.create_oval(cuerda_x - 20, cuerda_y, cuerda_x + 20, cuerda_y + 40, width=2)
    # ... y así sucesivamente para el resto del cuerpo
    
def actualizar_pantalla_juego():
    """Actualiza la visualización de la palabra, vidas y letras incorrectas."""
    global label_palabra, label_vidas, label_letras_incorrectas, canvas_ahorcado

    palabra_mostrada = ""
    for letra in palabra_secreta:
        if letra in letras_adivinadas:
            palabra_mostrada += letra + " "
        else:
            palabra_mostrada += "_ "

    label_palabra.config(text=palabra_mostrada.strip())
    label_vidas.config(text=f"Vidas: {'🏆 ' * vidas_restantes}")
    label_letras_incorrectas.config(text=f"Letras incorrectas: {', '.join(sorted(letras_incorrectas))}")
    
    # Actualiza el dibujo del ahorcado
    # La etapa_actual para dibujar el ahorcado se puede calcular a partir de vidas_restantes
    # Por ejemplo, 7 vidas restantes = etapa 0 (solo la horca), 0 vidas restantes = etapa 7 (ahorcado completo)
    # Si tienes 7 vidas, significa que se han perdido 0. Si tienes 0 vidas, se han perdido 7.
    # Etapa de dibujo = 7 - vidas_restantes
    dibujar_ahorcado(canvas_ahorcado, 7 - vidas_restantes)


def verificar_letra(letra_elegida):
    """Verifica la letra elegida por el usuario."""
    global vidas_restantes, letras_adivinadas, letras_incorrectas, label_feedback

    # Desactivar el botón de la letra elegida
    if letra_elegida in botones_letras:
        botones_letras[letra_elegida].config(state=tk.DISABLED, bg="gray")

    if letra_elegida in palabra_secreta:
        if letra_elegida not in letras_adivinadas:
            letras_adivinadas.append(letra_elegida)
            label_feedback.config(text="¡Vamos! Tu letra está dentro de la palabra secreta!", fg="green")
        else:
            label_feedback.config(text="¡Ya habías adivinado esa letra!", fg="orange")
    else:
        if letra_elegida not in letras_incorrectas:
            vidas_restantes -= 1
            letras_incorrectas.append(letra_elegida)
            label_feedback.config(text=f"No te desanimes, todavía tenés {vidas_restantes} vidas. ¡A seguir intentando!", fg="red")

            if vidas_restantes == 1:
                messagebox.showwarning("¡Alerta!", "¡Te queda UNA SOLA VIDA! Pensá muy bien tu próximo movimiento.")
        else:
            label_feedback.config(text="Ya habías probado esa letra y no está.", fg="orange")

    actualizar_pantalla_juego()
    verificar_fin_juego()

def verificar_fin_juego():
    """Verifica si el juego ha terminado (ganado o perdido)."""
    global palabra_secreta, letras_adivinadas, vidas_restantes, ventana_juego_real

    # Verificar si ganó
    palabra_completa = True
    for letra in palabra_secreta:
        if letra not in letras_adivinadas:
            palabra_completa = False
            break
    
    if palabra_completa:
        messagebox.showinfo("¡Felicidades!", f"¡GANASTE! La palabra era: {palabra_secreta}")
        reiniciar_o_salir()
        return

    # Verificar si perdió
    if vidas_restantes <= 0:
        messagebox.showinfo("¡Game Over!", f"¡PERDISTE! La palabra secreta era: {palabra_secreta}")
        reiniciar_o_salir()
        return

def reiniciar_o_salir():
    """Pregunta al usuario si quiere jugar de nuevo o salir."""
    global ventana_juego_real
    if ventana_juego_real: # Asegurarse de que la ventana existe antes de intentar destruirla
        ventana_juego_real.destroy()
    respuesta = messagebox.askyesno("Fin del Juego", "¿Querés jugar de nuevo?")
    if respuesta:
        iniciar_juego_ahorcado_real() # Reinicia el juego
    else:
        # Aquí puedes agregar cualquier limpieza final o simplemente permitir que el programa termine
        pass # La ventana ya se cerró con destroy si estaba abierta

def iniciar_juego_ahorcado_real():
    """
    Esta función contiene la lógica principal del juego del ahorcado:
    selección de palabra, mostrar guiones, entrada de usuario, etc.
    """
    detener_musica()

    global ventana_listo_para_jugar
    if ventana_listo_para_jugar:
        ventana_listo_para_jugar.destroy()
        ventana_listo_para_jugar = None

    global ventana_juego_real, palabra_secreta, letras_adivinadas, letras_incorrectas, vidas_restantes
    global label_palabra, label_vidas, label_letras_incorrectas, label_feedback, botones_letras, canvas_ahorcado

    # Reiniciar variables de juego
    categoria_elegida = random.choice(list(PALABRAS_POR_CATEGORIA.keys()))
    palabras_de_categoria = PALABRAS_POR_CATEGORIA[categoria_elegida]
    palabra_secreta = random.choice(palabras_de_categoria).upper()
    letras_adivinadas = []
    letras_incorrectas = []
    vidas_restantes = 7
    botones_letras = {} # Asegurarse de limpiar los botones de una partida anterior

    ventana_juego_real = tk.Tk()
    ventana_juego_real.title("El Juego del Ahorcado - ¡A Jugar!")
    ventana_juego_real.geometry("900x700") # Aumentamos el tamaño para acomodar todo
    ventana_juego_real.resizable(False, False)
    ventana_juego_real.configure(bg="#F0F0F0") # Un color de fondo claro para el juego

    # Frame principal para organizar los elementos en dos columnas (horca y juego)
    main_game_frame = tk.Frame(ventana_juego_real, bg="#F0F0F0")
    main_game_frame.pack(expand=True, fill="both")

    # Columna izquierda para el Canvas del ahorcado
    ahorcado_frame = tk.Frame(main_game_frame, bg="#F0F0F0")
    ahorcado_frame.pack(side="left", padx=20, pady=20, fill="y")

    canvas_ahorcado = tk.Canvas(ahorcado_frame, width=250, height=350, bg="white", highlightbackground="black", highlightthickness=1)
    canvas_ahorcado.pack()

    # Columna derecha para la información del juego y botones de letras
    game_info_frame = tk.Frame(main_game_frame, bg="#F0F0F0")
    game_info_frame.pack(side="right", padx=20, pady=20, expand=True, fill="both")

    tk.Label(game_info_frame, text=f"Categoría: {categoria_elegida}", font=("Arial", 20, "bold"), bg="#F0F0F0").pack(pady=10)

    label_palabra = tk.Label(game_info_frame, text="_ " * len(palabra_secreta), font=("Arial", 36, "bold"), bg="#F0F0F0", fg="blue")
    label_palabra.pack(pady=10)

    label_vidas = tk.Label(game_info_frame, text=f"Vidas: {'🏆 ' * vidas_restantes}", font=("Arial", 24), bg="#F0F0F0", fg="darkgreen")
    label_vidas.pack(pady=10)

    label_letras_incorrectas = tk.Label(game_info_frame, text="Letras incorrectas: ", font=("Arial", 16), bg="#F0F0F0", fg="red")
    label_letras_incorrectas.pack(pady=10)

    # Label para mensajes de feedback
    label_feedback = tk.Label(game_info_frame, text="", font=("Arial", 18, "italic"), bg="#F0F0F0")
    label_feedback.pack(pady=10)

    # Frame para los botones de letras
    letras_frame = tk.Frame(game_info_frame, bg="#F0F0F0")
    letras_frame.pack(pady=20)

    # Crear botones para cada letra del abecedario
    fila = 0
    columna = 0
    for letra in string.ascii_uppercase: # Obtiene A, B, C, ... Z
        btn = tk.Button(letras_frame, text=letra, font=("Arial", 16, "bold"),
                        width=4, height=2, bg="#ADD8E6", fg="black", # Color azul claro para los botones
                        command=lambda l=letra: verificar_letra(l))
        btn.grid(row=fila, column=columna, padx=3, pady=3) # Ajuste de padx/pady
        botones_letras[letra] = btn # Guardar referencia al botón
        columna += 1
        if columna > 8: # 9 botones por fila para una buena distribución
            columna = 0
            fila += 1

    actualizar_pantalla_juego() # Llamada inicial para mostrar el estado del juego y dibujar la horca

    ventana_juego_real.mainloop()

def mostrar_pantalla_listo_para_jugar():
    """
    Muestra una pantalla intermedia con una imagen y un botón para comenzar el juego real.
    """
    detener_musica() # Detener la música de la pantalla de instrucciones

    global ventana_instrucciones
    if ventana_instrucciones:
        ventana_instrucciones.destroy()
        ventana_instrucciones = None

    global ventana_listo_para_jugar
    ventana_listo_para_jugar = tk.Tk()
    ventana_listo_para_jugar.title("¡Listo para Jugar!")
    ventana_listo_para_jugar.geometry("900x600")
    ventana_listo_para_jugar.resizable(False, False)
    ventana_listo_para_jugar.configure(bg="black") # Establecer un color de fondo por si la imagen no carga

    # --- Cargar la NUEVA imagen de fondo para "LISTO PARA JUGAR" ---
    try:
        img = Image.open(IMAGEN_FONDO_LISTO_PATH) # Usa la nueva constante
        img = img.resize((900, 600), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        label_fondo = tk.Label(ventana_listo_para_jugar, image=img_tk)
        label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        label_fondo.image = img_tk # Importante para mantener la referencia de la imagen
    except FileNotFoundError:
        messagebox.showerror("Error de Imagen", f"No se encontró el archivo de imagen: {IMAGEN_FONDO_LISTO_PATH}")
        # Aseguramos que el label de error también tenga fondo negro y texto blanco
        label_fondo = tk.Label(ventana_listo_para_jugar, text="Fondo no encontrado", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")
    except Exception as e:
        messagebox.showerror("Error de Imagen", f"Error al cargar la imagen: {e}")
        # Aseguramos que el label de error también tenga fondo negro y texto blanco
        label_fondo = tk.Label(ventana_listo_para_jugar, text="Error al cargar el fondo", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")

    # --- Reproducir la NUEVA música para "LISTO PARA JUGAR" ---
    reproducir_musica(MUSICA_LISTO_PATH) 

    # Aseguramos que el color de fondo del label de texto sea negro y el texto blanco
    tk.Label(ventana_listo_para_jugar, text="¡Ya estás a nada de empezar!",
             font=("Arial", 36, "bold"), fg="white", bg="black").pack(pady=100)

    btn_comenzar = tk.Button(ventana_listo_para_jugar, text="COMENZAR",
                             command=iniciar_juego_ahorcado_real,
                             font=("Arial", 28, "bold"), bg="green", fg="white",
                             width=18, height=2)
    btn_comenzar.pack(pady=50)

    ventana_listo_para_jugar.mainloop()


def iniciar_pantalla_instrucciones():
    """
    Esta función muestra la pantalla de instrucciones del juego,
    ahora con su propia imagen y música.
    """
    detener_musica() # Detener la música de la pantalla de inicio

    global ventana_inicio
    if ventana_inicio:
        ventana_inicio.destroy()
        ventana_inicio = None

    global ventana_instrucciones
    ventana_instrucciones = tk.Tk()
    ventana_instrucciones.title("Instrucciones del Ahorcado")
    ventana_instrucciones.geometry("900x600")
    ventana_instrucciones.resizable(False, False)
    ventana_instrucciones.configure(bg="black") # Establecer un color de fondo por si la imagen no carga

    # --- Cargar la NUEVA imagen de fondo para INSTRUCCIONES ---
    try:
        img = Image.open(IMAGEN_FONDO_INSTRUCCIONES_PATH)
        img = img.resize((900, 600), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        label_fondo = tk.Label(ventana_instrucciones, image=img_tk)
        label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        label_fondo.image = img_tk # Importante para mantener la referencia de la imagen
    except FileNotFoundError:
        messagebox.showerror("Error de Imagen", f"No se encontró el archivo de imagen: {IMAGEN_FONDO_INSTRUCCIONES_PATH}")
        # Aseguramos que el label de error también tenga fondo negro y texto blanco
        label_fondo = tk.Label(ventana_instrucciones, text="Fondo no encontrado", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")
    except Exception as e:
        messagebox.showerror("Error de Imagen", f"Error al cargar la imagen: {e}")
        # Aseguramos que el label de error también tenga fondo negro y texto blanco
        label_fondo = tk.Label(ventana_instrucciones, text="Error al cargar el fondo", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")

    # --- Reproducir la NUEVA música para INSTRUCCIONES ---
    reproducir_musica(MUSICA_INSTRUCCIONES_PATH)

    tk.Label(ventana_instrucciones, text="Recordá que tenés solo 7 vidas para jugar!",
             font=("Arial", 28, "bold"), fg="white", bg="black").pack(pady=30)

    vidas_str = "🏆 " * 7
    tk.Label(ventana_instrucciones, text=vidas_str,
             font=("Arial", 36), fg="gold", bg="black").pack(pady=10)

    tk.Label(ventana_instrucciones, text="Ahora bien... ¿Cómo jugamos?",
             font=("Arial", 24, "italic"), fg="white", bg="black").pack(pady=20)

    tk.Label(ventana_instrucciones, text="Tenés que elegir una letra.",
             font=("Arial", 20), fg="white", bg="black").pack(pady=5)
    tk.Label(ventana_instrucciones, text="¡No podes seleccionar ni números ni caracteres especiales!",
             font=("Arial", 20, "bold"), fg="red", bg="black").pack(pady=5)

    btn_continuar = tk.Button(ventana_instrucciones, text="¿CONTINUAMOS?",
                              command=mostrar_pantalla_listo_para_jugar,
                              font=("Arial", 24, "bold"), bg="blue", fg="white",
                              width=20, height=2)
    btn_continuar.pack(pady=40)

    ventana_instrucciones.mainloop()


def mostrar_pantalla_inicio():
    """Crea y muestra la ventana de inicio del juego."""
    global ventana_inicio
    ventana_inicio = tk.Tk()
    ventana_inicio.title("Bienvenidos al Ahorcado ☠️")
    ventana_inicio.geometry("900x600")
    ventana_inicio.resizable(False, False)
    ventana_inicio.configure(bg="black") # Asegura un fondo negro por defecto para la ventana

    try:
        img = Image.open(IMAGEN_FONDO_INICIO_PATH)
        img = img.resize((900, 600), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        label_fondo = tk.Label(ventana_inicio, image=img_tk)
        label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        label_fondo.image = img_tk # Mantener una referencia para evitar que se recoja la basura
    except FileNotFoundError:
        messagebox.showerror("Error de Imagen", f"No se encontró el archivo de imagen: {IMAGEN_FONDO_INICIO_PATH}")
        # Mostrar un fondo negro y texto blanco si la imagen no carga
        label_fondo = tk.Label(ventana_inicio, text="Fondo no encontrado", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")
    except Exception as e:
        messagebox.showerror("Error de Imagen", f"Error al cargar la imagen: {e}")
        # Mostrar un fondo negro y texto blanco si la imagen no carga
        label_fondo = tk.Label(ventana_inicio, text="Error al cargar el fondo", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")

    # Asegura que el color de fondo del label de bienvenida sea negro y el texto blanco
    tk.Label(ventana_inicio, text="¡Bienvenidos al Ahorcado ☠️!",
             font=("Arial", 36, "bold"), fg="white", bg="black").pack(pady=100)

    btn_iniciar = tk.Button(ventana_inicio, text="INICIAR",
                            command=iniciar_pantalla_instrucciones,
                            font=("Arial", 24, "bold"), bg="green", fg="white",
                            width=15, height=2)
    btn_iniciar.pack(pady=50)

    reproducir_musica(MUSICA_INICIO_PATH)

    ventana_inicio.mainloop()

if __name__ == "__main__":
    mostrar_pantalla_inicio()