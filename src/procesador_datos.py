import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from src.excepciones import ErrorValidacionDatos
from src.decoradores import medir_tiempo, capturar_errores

# Mapeo oficial de la variable objetivo
MAPEO_OBJETIVO = {
    "Dropout": 0,
    "Enrolled": 1,
    "Graduate": 2
}

MAPEO_INVERSO = {
    0: "Desercion",
    1: "Matriculado",
    2: "Graduado"
}

class ProcesadorDatos:
    """Clase para cargar, limpiar y preparar los datos de los estudiantes."""
    
    def __init__(self, ruta_archivo=None):
        self.ruta_archivo = ruta_archivo
        self.datos = None
        self.X_entrenamiento = None
        self.X_prueba = None
        self.y_entrenamiento = None
        self.y_prueba = None
        self.normalizador = StandardScaler()
        self.columnas_numericas = []
        self.columnas_caracteristicas = []

    @capturar_errores
    @medir_tiempo
    def cargar_datos(self):
        """Carga los datos desde un archivo CSV detectando el delimitador."""
        if not self.ruta_archivo or not os.path.exists(self.ruta_archivo):
            raise ErrorValidacionDatos(f"La ruta del archivo no es valida o no existe: {self.ruta_archivo}")
        
        # Intentar con punto y coma primero (delimitador estandar de UCI)
        try:
            self.datos = pd.read_csv(self.ruta_archivo, sep=';')
            if len(self.datos.columns) <= 1:
                # Si falla, intentar con coma
                self.datos = pd.read_csv(self.ruta_archivo, sep=',')
        except Exception as error:
            raise ErrorValidacionDatos(f"Error al leer el archivo CSV: {str(error)}")
        
        if "Target" not in self.datos.columns:
            raise ErrorValidacionDatos("El dataset no contiene la columna objetivo 'Target'.")
            
        return self.datos

    @capturar_errores
    @medir_tiempo
    def preparar_datos(self, fraccion_prueba=0.2, semilla_aleatoria=42):
        """Prepara los datos para el entrenamiento de los modelos."""
        if self.datos is None:
            self.cargar_datos()

        # Copiar datos para evitar efectos secundarios
        datos_procesados = self.datos.copy()

        # Codificar la variable objetivo
        datos_procesados['Target'] = datos_procesados['Target'].map(MAPEO_OBJETIVO)
        
        # Si hay valores nulos en el Target despues del mapeo, lanzar error
        if datos_procesados['Target'].isnull().any():
            raise ErrorValidacionDatos("Existen valores desconocidos o nulos en la columna 'Target'.")

        # Separar caracteristicas y variable objetivo
        X = datos_procesados.drop(columns=['Target'])
        y = datos_procesados['Target']

        self.columnas_caracteristicas = list(X.columns)

        # Identificar columnas numericas para normalizacion (calificaciones, edades, tasas)
        self.columnas_numericas = [
            col for col in X.columns 
            if "grade" in col.lower() or "rate" in col.lower() or "age" in col.lower() or col.lower() == "gdp"
        ]

        # Division en entrenamiento y prueba
        (self.X_entrenamiento, self.X_prueba, 
         self.y_entrenamiento, self.y_prueba) = train_test_split(
            X, y, test_size=fraccion_prueba, random_state=semilla_aleatoria, stratify=y
        )

        # Normalizar las columnas numericas seleccionadas
        if self.columnas_numericas:
            # Ajustar normalizador en entrenamiento y transformar ambos
            self.X_entrenamiento = self.X_entrenamiento.copy()
            self.X_prueba = self.X_prueba.copy()
            
            self.X_entrenamiento[self.columnas_numericas] = self.normalizador.fit_transform(
                self.X_entrenamiento[self.columnas_numericas]
            )
            self.X_prueba[self.columnas_numericas] = self.normalizador.transform(
                self.X_prueba[self.columnas_numericas]
            )

        return self.X_entrenamiento, self.X_prueba, self.y_entrenamiento, self.y_prueba

    def obtener_datos_procesados(self):
        """Retorna las particiones de datos de entrenamiento y prueba."""
        return self.X_entrenamiento, self.X_prueba, self.y_entrenamiento, self.y_prueba
        
    def normalizar_instancia(self, datos_instancia):
        """Normaliza una unica instancia en formato DataFrame para predicciones individuales."""
        instancia_procesada = datos_instancia.copy()
        if self.columnas_numericas:
            instancia_procesada[self.columnas_numericas] = self.normalizador.transform(
                instancia_procesada[self.columnas_numericas]
            )
        return instancia_procesada
