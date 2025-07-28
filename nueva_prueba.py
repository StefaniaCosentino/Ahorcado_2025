import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import string # Para obtener el abecedario
import time # Para pausar la ejecución y mostrar el GIF

# Diccionario de categorías y palabras
PALABRAS_POR_CATEGORIA = {
    "Geología": [
        "Mineral", "Roca", "Falla", "Volcan", "Terremoto",
        "Erosion", "Glaciar", "Sedimento", "Fosil", "Magma",
        "Lava", "Corteza", "Manto", "Nucleo", "Geologo"
    ],
    "Estados de Animo": [
        "Alegria", "Tristeza", "Enojo", "Miedo", "Sorpresa",
        "Calma", "Ansiedad", "Felicidad", "Melancolia", "Optimismo",
        "Pesimismo", "Aburrimiento", "Entusiasmo", "Frustracion", "Esperanza"
    ],
    "Nombres de Personas": [
        "Sofia", "Martin", "Valentina", "Mateo", "Camila",
        "Santiago", "Lucía", "Benjamin", "Isabella", "Lucas",
        "Emma", "Julian", "Agustina", "Nicolas", "Catalina"
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

# NUEVO RECURSO: GIF para cuando se gana
GIF_VICTORIA_PATH = "image_1a7ba3.png" # Asegúrate de que este GIF exista en tu carpeta

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
    etapa_actual: 0 = solo la horca, 1 = cabeza, ..., 7 = ahorcado completo.
    """
    canvas.delete("all") # Limpia el canvas antes de redibujar

    # Es crucial que el canvas tenga sus dimensiones finales antes de dibujar
    canvas.update_idletasks()
    ancho_canvas = canvas.winfo_width()
    alto_canvas = canvas.winfo_height()

    # --- Dibujo de la horca ---
    margin_x = ancho_canvas * 0.05
    margin_y = alto_canvas * 0.05

    # Base (suelo)
    base_y = alto_canvas - margin_y
    canvas.create_line(margin_x, base_y, ancho_canvas - margin_x, base_y, width=4)

    # Poste vertical (izquierda)
    poste_x = margin_x + (ancho_canvas * 0.1)
    poste_top_y = margin_y
    canvas.create_line(poste_x, base_y, poste_x, poste_top_y, width=4)

    # Viga horizontal (superior)
    viga_right_x = ancho_canvas * 0.75
    canvas.create_line(poste_x, poste_top_y, viga_right_x, poste_top_y, width=4)

    # Soporte diagonal
    canvas.create_line(poste_x, poste_top_y + 20, poste_x + 20, poste_top_y, width=4)

    # Cuerda del ahorcado (donde se colgará la cabeza)
    cuerda_x = viga_right_x - (ancho_canvas * 0.08)
    cuerda_inicio_y = poste_top_y
    cuerda_fin_y = poste_top_y + (alto_canvas * 0.1) # Longitud de la cuerda para colgar
    canvas.create_line(cuerda_x, cuerda_inicio_y, cuerda_x, cuerda_fin_y, width=3)

    cabeza_radio = (ancho_canvas * 0.07) # Radio de la cabeza proporcional al ancho
    cabeza_y_centro = cuerda_fin_y + cabeza_radio
    cabeza_x_centro = cuerda_x

    # Cabeza
    if etapa_actual >= 1:
        canvas.create_oval(cabeza_x_centro - cabeza_radio, cabeza_y_centro - cabeza_radio,
                           cabeza_x_centro + cabeza_radio, cabeza_y_centro + cabeza_radio,
                           width=2)
    
    cuerpo_inicio_y = cabeza_y_centro + cabeza_radio
    cuerpo_fin_y = cuerpo_inicio_y + (alto_canvas * 0.2) # Largo del cuerpo

    # Cuerpo
    if etapa_actual >= 2:
        canvas.create_line(cabeza_x_centro, cuerpo_inicio_y, cabeza_x_centro, cuerpo_fin_y, width=2)

    # Brazos
    brazo_largo = (ancho_canvas * 0.1)
    brazo_y = cuerpo_inicio_y + (alto_canvas * 0.05) # Los brazos salen un poco más abajo de la cabeza

    # Brazo izquierdo
    if etapa_actual >= 3:
        canvas.create_line(cabeza_x_centro, brazo_y, cabeza_x_centro - brazo_largo, brazo_y + brazo_largo, width=2)

    # Brazo derecho
    if etapa_actual >= 4:
        canvas.create_line(cabeza_x_centro, brazo_y, cabeza_x_centro + brazo_largo, brazo_y + brazo_largo, width=2)

    # Piernas
    pierna_largo = (ancho_canvas * 0.12)
    pierna_y = cuerpo_fin_y

    # Pierna izquierda
    if etapa_actual >= 5:
        canvas.create_line(cabeza_x_centro, pierna_y, cabeza_x_centro - pierna_largo, pierna_y + pierna_largo, width=2)

    # Pierna derecha
    if etapa_actual >= 6:
        canvas.create_line(cabeza_x_centro, pierna_y, cabeza_x_centro + pierna_largo, pierna_y + pierna_largo, width=2)

    # Ojos y boca (solo cuando ha perdido totalmente)
    if etapa_actual >= 7:
        # Ojo izquierdo (X)
        canvas.create_line(cabeza_x_centro - cabeza_radio * 0.4, cabeza_y_centro - cabeza_radio * 0.3,
                           cabeza_x_centro - cabeza_radio * 0.2, cabeza_y_centro - cabeza_radio * 0.1,
                           width=2)
        canvas.create_line(cabeza_x_centro - cabeza_radio * 0.4, cabeza_y_centro - cabeza_radio * 0.1,
                           cabeza_x_centro - cabeza_radio * 0.2, cabeza_y_centro - cabeza_radio * 0.3,
                           width=2)
        # Ojo derecho (X)
        canvas.create_line(cabeza_x_centro + cabeza_radio * 0.2, cabeza_y_centro - cabeza_radio * 0.3,
                           cabeza_x_centro + cabeza_radio * 0.4, cabeza_y_centro - cabeza_radio * 0.1,
                           width=2)
        canvas.create_line(cabeza_x_centro + cabeza_radio * 0.2, cabeza_y_centro - cabeza_radio * 0.1,
                           cabeza_x_centro + cabeza_radio * 0.4, cabeza_y_centro - cabeza_radio * 0.3,
                           width=2)
        # Boca recta
        canvas.create_line(cabeza_x_centro - cabeza_radio * 0.3, cabeza_y_centro + cabeza_radio * 0.4,
                           cabeza_x_centro + cabeza_radio * 0.3, cabeza_y_centro + cabeza_radio * 0.4,
                           width=2)


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
    
    # La etapa actual de dibujo es 7 - vidas_restantes (0 errores = etapa 0, 7 errores = etapa 7)
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
            label_feedback.config(text="¡Vamos! Elegiste la letra correcta!!!", fg="green")
    else:
        if letra_elegida not in letras_incorrectas:
            vidas_restantes -= 1
            letras_incorrectas.append(letra_elegida)
            label_feedback.config(text=f"No te desanimes, todavía tenés {vidas_restantes} vidas. ¡A seguir intentando!", fg="red")

            if vidas_restantes == 1:
                messagebox.showwarning("¡Alerta!", "¡Te queda UNA SOLA VIDA! Pensá muy bien tu próximo movimiento.")

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
        if ventana_juego_real:
            ventana_juego_real.destroy() # Cierra la ventana del juego
        mostrar_gif_victoria() # Muestra el GIF de victoria
        return

    # Verificar si perdió
    if vidas_restantes <= 0:
        messagebox.showinfo("FIN DEL JUEGO!", f"PERDISTE! La palabra secreta era: {palabra_secreta}")
        reiniciar_o_salir()
        return

def reiniciar_o_salir():
    """Pregunta al usuario si quiere jugar de nuevo o salir."""
    global ventana_juego_real
    # No destruir ventana_juego_real aquí, ya se destruye en verificar_fin_juego si se gana o pierde.
    
    respuesta = messagebox.askyesno("Fin del Juego", "¿Querés jugar de nuevo?")
    if respuesta:
        iniciar_juego_ahorcado_real() # Reinicia el juego
    else:
        # Si el usuario elige no jugar de nuevo, cierra todas las ventanas pendientes
        if ventana_inicio: ventana_inicio.destroy()
        if ventana_instrucciones: ventana_instrucciones.destroy()
        if ventana_listo_para_jugar: ventana_listo_para_jugar.destroy()
        pygame.quit() # Cierra pygame mixer
        exit() # Sale del programa de forma limpia

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
    ventana_juego_real.geometry("1400x900")
    ventana_juego_real.resizable(False, False)
    ventana_juego_real.configure(bg="#F0F0F0") 

    # Frame principal para organizar los elementos en dos columnas (horca y juego)
    main_game_frame = tk.Frame(ventana_juego_real, bg="#F0F0F0")
    main_game_frame.pack(expand=True, fill="both", padx=15, pady=15) 

    # Columna izquierda para el Canvas del ahorcado
    ahorcado_frame = tk.Frame(main_game_frame, bg="#F0F0F0")
    ahorcado_frame.pack(side="left", padx=15, pady=15, fill="both", expand=True) 

    canvas_ahorcado = tk.Canvas(ahorcado_frame, width=400, height=500, bg="white", highlightbackground="black", highlightthickness=1)
    canvas_ahorcado.pack(expand=True, fill="both") 

    # Columna derecha para la información del juego y botones de letras
    game_info_frame = tk.Frame(main_game_frame, bg="#F0F0F0")
    game_info_frame.pack(side="right", padx=15, pady=15, expand=True, fill="both")

    tk.Label(game_info_frame, text=f"Categoría: {categoria_elegida}", font=("Arial", 22, "bold"), bg="#F0F0F0").pack(pady=7)

    label_palabra = tk.Label(game_info_frame, text="_ " * len(palabra_secreta), font=("Arial", 40, "bold"), bg="#F0F0F0", fg="blue")
    label_palabra.pack(pady=7)

    label_vidas = tk.Label(game_info_frame, text=f"Vidas: {'🏆 ' * vidas_restantes}", font=("Arial", 28), bg="#F0F0F0", fg="darkgreen")
    label_vidas.pack(pady=7)

    label_letras_incorrectas = tk.Label(game_info_frame, text="Letras incorrectas: ", font=("Arial", 18), bg="#F0F0F0", fg="red")
    label_letras_incorrectas.pack(pady=7)

    label_feedback = tk.Label(game_info_frame, text="", font=("Arial", 20, "italic"), bg="#F0F0F0")
    label_feedback.pack(pady=15)

    letras_frame = tk.Frame(game_info_frame, bg="#F0F0F0")
    letras_frame.pack(pady=10, fill="x", expand=True) 

    # Crear botones para cada letra del abecedario
    fila = 0
    columna = 0
    num_columnas = 10 

    for letra in string.ascii_uppercase:
        btn = tk.Button(letras_frame, text=letra, font=("Arial", 16, "bold"),
                        width=4, height=2, bg="#ADD8E6", fg="black",
                        command=lambda l=letra: verificar_letra(l))
        btn.grid(row=fila, column=columna, padx=3, pady=3)
        botones_letras[letra] = btn 
        columna += 1
        if columna >= num_columnas:
            columna = 0
            fila += 1
    
    ventana_juego_real.update_idletasks()
    actualizar_pantalla_juego() # Llamada inicial para mostrar el estado del juego y dibujar la horca

    ventana_juego_real.mainloop()

def mostrar_gif_victoria():
    """Muestra un GIF de celebración con el texto "¡GANASTE!!!" en una nueva ventana."""
    detener_musica() # Opcional: detener la música del juego si aún suena

    gif_window = tk.Toplevel()
    gif_window.title("¡VICTORIA!")
    gif_window.geometry("600x400") # Tamaño aproximado para el GIF
    gif_window.resizable(False, False)
    gif_window.grab_set() # Hace que esta ventana sea modal
    gif_window.transient(ventana_inicio) # La asocia con la ventana principal (si existe)

    label_gif = tk.Label(gif_window)
    label_gif.pack(expand=True, fill="both")

    # Label para el texto "¡GANASTE!!!"
    label_ganaste = tk.Label(gif_window, text="¡GANASTE!!!", font=("Arial", 48, "bold"), fg="gold", bg="black")
    label_ganaste.place(relx=0.5, rely=0.15, anchor="center") # Centrado en la parte superior

    try:
        # Cargar el GIF y todos sus fotogramas
        info = Image.open(GIF_VICTORIA_PATH)
        frames = []
        try:
            while True:
                # Redimensionar cada fotograma para que se ajuste a la ventana
                frame = info.copy()
                frame = frame.resize((600, 400), Image.LANCZOS) # Ajustar al tamaño de la ventana del GIF
                frames.append(ImageTk.PhotoImage(frame))
                info.seek(len(frames)) # Moverse al siguiente fotograma
        except EOFError:
            pass # Se llega al final del GIF

        # Función para animar el GIF
        def animate_gif(index):
            if not gif_window.winfo_exists(): # Si la ventana ya fue cerrada, detiene la animación
                return
            frame = frames[index]
            label_gif.config(image=frame)
            label_gif.image = frame # Importante para evitar que el garbage collector borre la imagen
            index = (index + 1) % len(frames) # Siguiente fotograma, bucle al inicio
            gif_window.after(info.info['duration'] if 'duration' in info.info else 100, animate_gif, index) # Duración del fotograma

        animate_gif(0) # Inicia la animación desde el primer fotograma

        # Reproducir un sonido de victoria si lo deseas
        # pygame.mixer.Sound("sonido_victoria.mp3").play()

    except FileNotFoundError:
        messagebox.showerror("Error de GIF", f"No se encontró el archivo GIF: {GIF_VICTORIA_PATH}")
        label_gif.config(text="GIF no encontrado", font=("Arial", 20), fg="red")
    except Exception as e:
        messagebox.showerror("Error de GIF", f"Error al cargar o animar el GIF: {e}")
        label_gif.config(text="Error al cargar GIF", font=("Arial", 20), fg="red")

    # Función que se llama al cerrar la ventana del GIF (ya sea por el usuario o por after)
    def on_gif_close():
        if gif_window.winfo_exists():
            gif_window.destroy()
        reiniciar_o_salir() # Después de cerrar el GIF, pregunta si quiere jugar de nuevo

    # Asegúrate de que la función on_gif_close se llame cuando la ventana del GIF se cierre
    gif_window.protocol("WM_DELETE_WINDOW", on_gif_close)
    
    # Cierra automáticamente la ventana del GIF después de 5 segundos y luego pregunta si desea jugar de nuevo
    gif_window.after(5000, on_gif_close) # Cierra después de 5 segundos (5000 ms)

    gif_window.mainloop()

def mostrar_pantalla_listo_para_jugar():
    """
    Muestra una pantalla intermedia con una imagen y un botón para comenzar el juego real.
    """
    detener_musica() 

    global ventana_instrucciones
    if ventana_instrucciones:
        ventana_instrucciones.destroy()
        ventana_instrucciones = None

    global ventana_listo_para_jugar
    ventana_listo_para_jugar = tk.Tk()
    ventana_listo_para_jugar.title("Listo para Jugar!🎲🍀")
    ventana_listo_para_jugar.geometry("900x600")
    ventana_listo_para_jugar.resizable(False, False)
    ventana_listo_para_jugar.configure(bg="black") 

    try:
        img = Image.open(IMAGEN_FONDO_LISTO_PATH) 
        img = img.resize((900, 600), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        label_fondo = tk.Label(ventana_listo_para_jugar, image=img_tk)
        label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        label_fondo.image = img_tk 
    except FileNotFoundError:
        messagebox.showerror("Error de Imagen", f"No se encontró el archivo de imagen: {IMAGEN_FONDO_LISTO_PATH}")
        label_fondo = tk.Label(ventana_listo_para_jugar, text="Fondo no encontrado", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")
    except Exception as e:
        messagebox.showerror("Error de Imagen", f"Error al cargar la imagen: {e}")
        label_fondo = tk.Label(ventana_listo_para_jugar, text="Error al cargar el fondo", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")

    reproducir_musica(MUSICA_LISTO_PATH) 

    tk.Label(ventana_listo_para_jugar, text="¡Ya estás a nada de empezar!",
             font=("Arial", 36, "bold"), fg="white", bg="black").pack(pady=100)

    btn_comenzar = tk.Button(ventana_listo_para_jugar, text="COMENZAR🐌",
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
    detener_musica() 

    global ventana_inicio
    if ventana_inicio:
        ventana_inicio.destroy()
        ventana_inicio = None

    global ventana_instrucciones
    ventana_instrucciones = tk.Tk()
    ventana_instrucciones.title("Instrucciones del Ahorcado")
    ventana_instrucciones.geometry("900x600")
    ventana_instrucciones.resizable(False, False)
    ventana_instrucciones.configure(bg="black") 

    try:
        img = Image.open(IMAGEN_FONDO_INSTRUCCIONES_PATH)
        img = img.resize((900, 600), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        label_fondo = tk.Label(ventana_instrucciones, image=img_tk)
        label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        label_fondo.image = img_tk 
    except FileNotFoundError:
        messagebox.showerror("Error de Imagen", f"No se encontró el archivo de imagen: {IMAGEN_FONDO_INSTRUCCIONES_PATH}")
        label_fondo = tk.Label(ventana_instrucciones, text="Fondo no encontrado", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")
    except Exception as e:
        messagebox.showerror("Error de Imagen", f"Error al cargar la imagen: {e}")
        label_fondo = tk.Label(ventana_instrucciones, text="Error al cargar el fondo", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")

    reproducir_musica(MUSICA_INSTRUCCIONES_PATH)

    tk.Label(ventana_instrucciones, text="Recordá que tenés solo 7 🏆 para jugar!",
             font=("Arial", 28, "bold"), fg="white", bg="black").pack(pady=30)

    vidas_str = "🏆 " * 7
    tk.Label(ventana_instrucciones, text=vidas_str,
             font=("Arial", 36), fg="gold", bg="black").pack(pady=10)

    tk.Label(ventana_instrucciones, text="Ahora bien... ¿Cómo jugamos?🧐",
             font=("Arial", 24, "italic"), fg="white", bg="black").pack(pady=20)

    tk.Label(ventana_instrucciones, text="Tenés que elegir una letra.",
             font=("Arial", 20), fg="white", bg="black").pack(pady=5)
    tk.Label(ventana_instrucciones, text="No podes seleccionar ni números ni caracteres especiales!❌",
             font=("Arial", 20, "bold"), fg="red", bg="black").pack(pady=5)

    btn_continuar = tk.Button(ventana_instrucciones, text="¿CONTINUAMOS?🆗",
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
    ventana_inicio.configure(bg="black") 

    try:
        img = Image.open(IMAGEN_FONDO_INICIO_PATH)
        img = img.resize((900, 600), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        label_fondo = tk.Label(ventana_inicio, image=img_tk)
        label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        label_fondo.image = img_tk 
    except FileNotFoundError:
        messagebox.showerror("Error de Imagen", f"No se encontró el archivo de imagen: {IMAGEN_FONDO_INICIO_PATH}")
        label_fondo = tk.Label(ventana_inicio, text="Fondo no encontrado", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")
    except Exception as e:
        messagebox.showerror("Error de Imagen", f"Error al cargar la imagen: {e}")
        label_fondo = tk.Label(ventana_inicio, text="Error al cargar el fondo", font=("Arial", 20), bg="black", fg="white")
        label_fondo.pack(expand=True, fill="both")

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