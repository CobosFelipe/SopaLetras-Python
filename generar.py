import urllib3
import random
import re
from fpdf import FPDF
import json

# Inicializa el administrador de conexiones de urllib3
http = urllib3.PoolManager()

# Función para obtener palabras de la Dog API
def get_words_from_dog_api(word_count=3):
    url = "https://api.thedogapi.com/v1/breeds"
    try:
        response = http.request('GET', url)  # Realiza la solicitud GET a la API
        if response.status != 200:
            raise Exception(f"HTTP error: {response.status}")
        data = json.loads(response.data.decode('utf-8'))  # Parsea la respuesta JSON

        words = set()
        descriptions = {}
        
        # Extrae palabras de las descripciones de las razas de perro
        for breed in data:
            description = breed['name']
            words_found = re.findall(r'\b[a-zA-Z]{4,}\b', description)
            for word in words_found:
                words.add(word.upper())
                descriptions[word.upper()] = description
        
        # Selecciona un número aleatorio de palabras
        words = list(words)
        random_words = random.sample(words, min(word_count, len(words)))
        random_descriptions = [descriptions[word] for word in random_words]
        
        return list(zip(random_words, random_descriptions))
    
    except Exception as e:
        print(f"HTTP error: {e}")
        return []

# Función para obtener palabras de la Chuck Norris API
def get_words_from_chuck_api(word_count=3):
    url = "https://api.chucknorris.io/jokes/random"
    try:
        words = set()
        descriptions = {}
        
        # Realiza varias solicitudes para obtener diferentes chistes
        for _ in range(word_count):
            response = http.request('GET', url)
            if response.status != 200:
                raise Exception(f"HTTP error: {response.status}")
            data = json.loads(response.data.decode('utf-8'))
            description = data['value']
            words_found = re.findall(r'\b[a-zA-Z]{4,}\b', description)
            for word in words_found:
                words.add(word.upper())
                descriptions[word.upper()] = description
        
        # Selecciona un número aleatorio de palabras
        words = list(words)
        random_words = random.sample(words, min(word_count, len(words)))
        random_descriptions = [descriptions[word] for word in random_words]
        
        return list(zip(random_words, random_descriptions))
    
    except Exception as e:
        print(f"HTTP error: {e}")
        return []

# Función para obtener palabras de la PokeAPI
def get_words_from_pokeapi(word_count=3):
    url = "https://pokeapi.co/api/v2/pokemon/"
    try:
        response = http.request('GET', url)  # Realiza la solicitud GET a la API
        if response.status != 200:
            raise Exception(f"HTTP error: {response.status}")
        data = json.loads(response.data.decode('utf-8'))
        results = data['results']  # Obtiene los resultados de la respuesta JSON

        words = set()
        descriptions = {}
        
        # Extrae palabras de los nombres de los Pokémon
        for pokemon in results:
            description = pokemon['name']
            words_found = re.findall(r'\b[a-zA-Z]{4,}\b', description)
            for word in words_found:
                words.add(word.upper())
                descriptions[word.upper()] = description
        
        # Selecciona un número aleatorio de palabras
        words = list(words)
        random_words = random.sample(words, min(word_count, len(words)))
        random_descriptions = [descriptions[word] for word in random_words]
        
        return list(zip(random_words, random_descriptions))
    
    except Exception as e:
        print(f"HTTP error: {e}")
        return []

# Función para generar la matriz de la sopa de letras
def generate_word_search(words, size=15):
    # Crea una matriz vacía
    matrix = [[' ' for _ in range(size)] for _ in range(size)]
    
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1)]  # Direcciones posibles
    word_positions = []
    
    # Intenta colocar cada palabra en la matriz
    for word, _ in words:
        word_len = len(word)
        placed = False
        
        while not placed:
            dir_x, dir_y = random.choice(directions)
            start_x = random.randint(0, size - 1)
            start_y = random.randint(0, size - 1)
            
            end_x = start_x + dir_x * (word_len - 1)
            end_y = start_y + dir_y * (word_len - 1)
            
            if 0 <= end_x < size and 0 <= end_y < size:
                valid_placement = True
                for i in range(word_len):
                    if matrix[start_x + dir_x * i][start_y + dir_y * i] not in (' ', word[i]):
                        valid_placement = False
                        break
                
                if valid_placement:
                    word_position = []
                    for i in range(word_len):
                        x, y = start_x + dir_x * i, start_y + dir_y * i
                        matrix[x][y] = word[i]
                        word_position.append((x, y))
                    word_positions.append((word_position, word))
                    placed = True
    
    # Rellena los espacios vacíos con letras aleatorias
    for i in range(size):
        for j in range(size):
            if matrix[i][j] == ' ':
                matrix[i][j] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    return matrix, word_positions

# Función para imprimir la matriz en la consola
def print_matrix(matrix):
    for row in matrix:
        print(' '.join(row))

# Función para guardar la matriz en un archivo JSON
def save_matrix_to_json(matrix, filename="palabras.json"):
    with open(filename, 'w') as f:
        json.dump(matrix, f)

# Clase para generar el PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'palabras', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

# Función para generar el PDF
def generate_pdf(matrix, words, word_positions, filename="palabras.pdf"):
    try:
        pdf = PDF()
        pdf.add_page()
        
        pdf.set_font("Arial", size=12)
        
        cell_size = 10
        color_map = {
            'dog': (21, 135, 185),
            'chuck': (255, 99, 41),
            'pokeapi': (56, 48, 103)
        }
        
        word_color_map = {}
        for idx, (word, _) in enumerate(words):
            if idx < 3:
                word_color_map[word] = color_map['dog']
            elif idx < 6:
                word_color_map[word] = color_map['chuck']
            else:
                word_color_map[word] = color_map['pokeapi']
        
        # Coloca las palabras en la matriz y colorea las celdas correspondientes
        for i, row in enumerate(matrix):
            for j, letter in enumerate(row):
                if any((i, j) in pos for pos, word in word_positions):
                    word = next(word for pos, word in word_positions if (i, j) in pos)
                    pdf.set_fill_color(*word_color_map[word])
                    pdf.cell(cell_size, cell_size, letter, 1, 0, 'C', 1)
                else:
                    pdf.cell(cell_size, cell_size, letter, 1, 0, 'C')
            pdf.ln(cell_size)
        
        pdf.ln(10)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, "Palabras:", ln=True, align='L')
        
        # Agrega la lista de palabras al PDF
        for word, description in words:
            pdf.cell(200, 10, f"{word}: {description.upper()}", ln=True, align='L')
        
        pdf.output(filename)
        print(f"PDF generado exitosamente: {filename}")
    
    except Exception as e:
        print(f"Error generando el PDF: {e}")

# Función para imprimir palabras en formato JSON
def print_words_as_json(words):
    words_dict = {word: description.upper() for word, description in words}
    json_output = json.dumps(words_dict, indent=4)
    print(json_output)

# Obtener palabras de las APIs
dog_words = get_words_from_dog_api(3)
chuck_words = get_words_from_chuck_api(3)
pokeapi_words = get_words_from_pokeapi(3)

# Combina todas las palabras obtenidas de las APIs
all_words = dog_words + chuck_words + pokeapi_words

# Imprime las palabras en formato JSON
print("Words in JSON format:")
print_words_as_json(all_words)

# Genera la matriz de la sopa de letras y obtiene las posiciones de las palabras
matrix, word_positions = generate_word_search(all_words)

# Imprime la matriz generada en la consola
print("Generated Word Search Matrix:")
print_matrix(matrix)

# Imprime las palabras a buscar
print("\nWords to find:")
words = []
for word, description in all_words:
    print(f"{word}: {description}")
    words.append(word)

print(words)

# Guarda la matriz en un archivo JSON
save_matrix_to_json(matrix)

# Genera el PDF
generate_pdf(matrix, all_words, word_positions)
