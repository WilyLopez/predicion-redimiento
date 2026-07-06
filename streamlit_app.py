import sys
import os

# Asegurar que el directorio raiz este en el path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Importar y ejecutar la funcion principal del tablero
from app.tablero import main

if __name__ == "__main__":
    main()
