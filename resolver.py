import json
import os
from fpdf import FPDF
from typing import List, Tuple, Dict

# Definición de excepciones personalizadas para manejar errores específicos de la búsqueda de palabras
class WordSearchError(Exception):
    pass

class MatrixSizeError(WordSearchError):
    pass

class WordCountError(WordSearchError):
    pass

class WordNotFoundError(WordSearchError):
    pass

class WordSearch:
    def __init__(self, matrix: List[List[str]], words: List[str]):
        self.matrix = matrix
        self.words = words
        self.found_words: Dict[str, List[Tuple[int, int]]] = {}
        self._validate()

    def _validate(self):
        # Verifica que la matriz sea de tamaño 15x15
        if not (len(self.matrix) == 15 and all(len(row) == 15 for row in self.matrix)):
            raise MatrixSizeError("Matrix must be 15x15 in size.")
        # Verifica que haya exactamente 9 palabras a buscar
        if len(self.words) != 9:
            raise WordCountError("There must be exactly 9 words to search for.")

    def _search(self, word: str, row: int, col: int, direction: Tuple[int, int]) -> bool:
        # Genera la ruta de coordenadas para la palabra en una dirección específica
        path = [(row + i * direction[0], col + i * direction[1]) for i in range(len(word))]
        # Verifica que todas las coordenadas estén dentro de los límites de la matriz y que las letras coincidan
        if all(0 <= r < 15 and 0 <= c < 15 and self.matrix[r][c] == word[i] for i, (r, c) in enumerate(path)):
            self.found_words[word] = path
            return True
        return False

    def search_word(self, word: str):
        # Direcciones posibles para buscar las palabras en la matriz
        directions = [(1, 0), (0, 1), (1, 1), (1, -1), (-1, 0), (0, -1), (-1, -1), (-1, 1)]
        # Busca la palabra en todas las direcciones desde cada posición de la matriz
        for row in range(15):
            for col in range(15):
                for direction in directions:
                    if self._search(word, row, col, direction):
                        return
        raise WordNotFoundError(f"Word '{word}' not found in the matrix.")

    def solve(self):
        # Busca todas las palabras en la lista de palabras
        for word in self.words:
            self.search_word(word)

class PDFGenerator:
    def __init__(self, matrix: List[List[str]], found_words: Dict[str, List[Tuple[int, int]]]):
        self.matrix = matrix
        self.found_words = found_words

    def generate(self, output_path: str):
        # Inicializa un nuevo documento PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        cell_size = 10
        # Genera la representación de la matriz en el PDF
        for row in range(15):
            for col in range(15):
                pdf.set_xy(col * cell_size, row * cell_size)
                # Colorea las celdas que contienen partes de las palabras encontradas
                if any((row, col) in pos for pos in self.found_words.values()):
                    pdf.set_text_color(49, 128, 243)  # Azul para letras encontradas
                else:
                    pdf.set_text_color(0, 0, 0)  # Negro para letras no encontradas
                pdf.cell(cell_size, cell_size, self.matrix[row][col], border=1, align='C')
        pdf.output(output_path)

def load_json_data(filepath: str) -> Tuple[List[List[str]], List[str]]:
    # Verifica que el archivo JSON exista
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"{filepath} does not exist.")
    
    with open(filepath, 'r') as file:
        data = json.load(file)

    # Verifica que la estructura del JSON sea correcta
    if isinstance(data, list) and all(isinstance(item, list) for item in data):
        if len(data) == 2:
            return data[0], data[1]
        if all(len(item) == 15 for item in data):
            return data, ["ARGENTINA", "HONDURAS", "VENEZUELA", "MORTYSMITH", "SUMMERSMITH", "AMISHCYBORG", "APOCALYMON", "CHUUMON", "ZHUQIAOMON"]
    
    raise ValueError("Invalid JSON structure.")

def main(json_path: str, output_pdf: str):
    # Carga los datos desde el archivo JSON
    matrix, words = load_json_data(json_path)
    # Crea una instancia de WordSearch y resuelve el puzzle
    word_search = WordSearch(matrix, words)
    word_search.solve()
    # Genera un PDF con la solución del puzzle
    pdf_generator = PDFGenerator(matrix, word_search.found_words)
    pdf_generator.generate(output_pdf)

if __name__ == "__main__":
    # Define la ruta del archivo JSON de entrada y el archivo PDF de salida
    main("palabras.json", "solucionpalabras.pdf")
