themes = {
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
def salir():
    root.quit()

def get_random_word_and_theme():
    theme = random.choice(list(themes.keys()))
    word = random.choice(themes[theme])
    return theme, word.lower()
