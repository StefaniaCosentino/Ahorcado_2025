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

    # --- Dibujo del cuerpo según la etapa_actual ---
    # La etapa_actual va de 0 a 7
    # 0 = solo horca (ya dibujada)
    # 1 = cabeza
    # 2 = cuerpo
    # 3 = brazo izquierdo
    # 4 = brazo derecho
    # 5 = pierna izquierda
    # 6 = pierna derecha
    # 7 = ojos/boca (final)

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
        # CORRECCIÓN AQUÍ: Usar 'letra_elegida' como clave, no la cadena literal
        botones_letras[letra_elegida].config(state=tk.DISABLED, bg="gray")

    if letra_elegida in palabra_secreta:
        if letra_elegida not in letras_adivinadas:
            letras_adivinadas.append(letra_elegida)
            label_feedback.config(text="¡Vamos! Elegiste la letra correcta!!!", fg="green")
        else: # Si ya la adivinó pero la vuelve a intentar (botón deshabilitado lo evita, pero buena práctica)
            label_feedback.config(text="¡Ya habías adivinado esa letra!", fg="orange")
    else:
        if letra_elegida not in letras_incorrectas:
            vidas_restantes -= 1
            letras_incorrectas.append(letra_elegida)
            label_feedback.config(text=f"No te desanimes, todavía tenés {vidas_restantes} vidas. ¡A seguir intentando!", fg="red")

            if vidas_restantes == 1:
                messagebox.showwarning("¡Alerta!", "¡Te queda UNA SOLA VIDA! Pensá muy bien tu próximo movimiento.")
        else: # Si ya la había intentado y era incorrecta (botón deshabilitado lo evita)
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
        messagebox.showinfo("FIN DEL JUEGO!", f"PERDISTE! La palabra secreta era: {palabra_secreta}")
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
    # No es necesario 'else: pass' ya que la función simplemente termina si no se reinicia

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
    # CORRECCIÓN AQUÍ: Usar 'categoria_elegida' como clave, no la cadena literal
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
    # Aumenta el número de columnas por fila para que quepan todos los botones en el ancho
    # 9 o 10 botones por fila deberían ser suficientes para el abecedario español
    # 27 letras (A-Z + Ñ)
    num_columnas = 10 # Se ajusta a 10 columnas para que las letras no se amontonen

    for letra in string.ascii_uppercase:
        btn = tk.Button(letras_frame, text=letra, font=("Arial", 16, "bold"),
                        width=4, height=2, bg="#ADD8E6", fg="black",
                        command=lambda l=letra: verificar_letra(l))
        btn.grid(row=fila, column=columna, padx=3, pady=3)
        botones_letras[letra] = btn # Aquí se guarda la referencia del botón correctamente
        columna += 1
        if columna >= num_columnas: # Cuando la columna llega al límite, pasa a la siguiente fila
            columna = 0
            fila += 1
    
    ventana_juego_real.update_idletasks()
    actualizar_pantalla_juego() # Llamada inicial para mostrar el estado del juego y dibujar la horca

    ventana_juego_real.mainloop()

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