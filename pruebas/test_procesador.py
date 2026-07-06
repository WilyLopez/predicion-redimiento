import unittest
import pandas as pd
import numpy as np
import tempfile
import os
from src.procesador_datos import ProcesadorDatos
from src.modelos import ClasificadorRendimiento
from src.agrupamiento import AgrupadorEstudiantes

class PruebasProcesadorYModelos(unittest.TestCase):
    """Clase de pruebas unitarias para validar el pipeline de datos y modelos."""

    def setUp(self):
        # Crear un dataset ficticio con las columnas principales para las pruebas
        self.columnas = [
            "Marital status", "Nationality", "Displaced", "Educational special needs",
            "Debtor", "Tuition fees up to date", "Gender", "Scholarship holder",
            "Age at enrollment", "International", "Mother's qualification",
            "Father's qualification", "Mother's occupation", "Father's occupation",
            "Admission grade", "Unemployment rate", "Inflation rate", "GDP", "Target"
        ]
        
        # Generar 20 filas de datos ficticios
        np.random.seed(42)
        filas = []
        clases_objetivo = ["Dropout", "Graduate", "Enrolled"]
        
        for _ in range(30):
            fila = [
                np.random.randint(1, 4),      # Marital status
                1,                            # Nationality
                np.random.randint(0, 2),      # Displaced
                0,                            # Educational special needs
                np.random.randint(0, 2),      # Debtor
                np.random.randint(0, 2),      # Tuition fees up to date
                np.random.randint(0, 2),      # Gender
                np.random.randint(0, 2),      # Scholarship holder
                np.random.randint(18, 50),    # Age at enrollment
                0,                            # International
                1, 1, 1, 1,                   # Parents qualification/occupation
                np.random.uniform(95.0, 200.0),# Admission grade
                np.random.uniform(7.0, 16.0),  # Unemployment rate
                np.random.uniform(0.5, 3.0),   # Inflation rate
                np.random.uniform(-2.0, 2.0),  # GDP
                np.random.choice(clases_objetivo) # Target
            ]
            filas.append(fila)

        self.df_ficticio = pd.DataFrame(filas, columns=self.columnas)
        
        # Guardar en un archivo temporal
        self.archivo_temporal = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        self.df_ficticio.to_csv(self.archivo_temporal.name, sep=';', index=False)
        self.archivo_temporal.close()

    def tearDown(self):
        # Eliminar el archivo temporal despues de la prueba
        if os.path.exists(self.archivo_temporal.name):
            os.remove(self.archivo_temporal.name)

    def test_carga_y_preparacion_datos(self):
        """Prueba que el ProcesadorDatos pueda cargar y preparar los datos ficticios."""
        procesador = ProcesadorDatos(self.archivo_temporal.name)
        datos = procesador.cargar_datos()
        
        self.assertEqual(len(datos), 30)
        self.assertIn("Target", datos.columns)

        X_entrenar, X_prueba, y_entrenar, y_prueba = procesador.preparar_datos(fraccion_prueba=0.3)
        
        # Verificar la separacion
        self.assertEqual(len(X_entrenar), 21)
        self.assertEqual(len(X_prueba), 9)
        self.assertEqual(len(y_entrenar), 21)
        self.assertEqual(len(y_prueba), 9)

    def test_entrenamiento_clasificadores(self):
        """Prueba que el ClasificadorRendimiento se entrene y prediga con exito."""
        procesador = ProcesadorDatos(self.archivo_temporal.name)
        X_entrenar, X_prueba, y_entrenar, y_prueba = procesador.preparar_datos(fraccion_prueba=0.3)

        for tipo_modelo in ["bosque_aleatorio", "regresion_logistica"]:
            with self.subTest(modelo=tipo_modelo):
                clasificador = ClasificadorRendimiento(tipo_modelo=tipo_modelo)
                clasificador.entrenar(X_entrenar, y_entrenar)
                
                predicciones = clasificador.predecir(X_prueba)
                probabilidades = clasificador.predecir_probabilidad(X_prueba)
                
                self.assertEqual(len(predicciones), 9)
                self.assertEqual(probabilidades.shape, (9, 3))
                
                evaluacion = clasificador.evaluar(X_prueba, y_prueba)
                self.assertIn("precision_global", evaluacion)
                self.assertIn("reporte_clasificacion", evaluacion)

    def test_agrupador_estudiantes(self):
        """Prueba que el AgrupadorEstudiantes pueda entrenarse y generar perfiles."""
        agrupador = AgrupadorEstudiantes(n_clusters=2)
        agrupador.entrenar_agrupamiento(self.df_ficticio)
        
        etiquetas = agrupador.asignar_perfil(self.df_ficticio)
        self.assertEqual(len(etiquetas), 30)
        self.assertTrue(all(e in [0, 1] for e in etiquetas))

        resumen = agrupador.obtener_descripcion_perfiles(self.df_ficticio)
        self.assertEqual(len(resumen), 2)
        self.assertIn("Perfil", resumen.columns)
        self.assertIn("Cantidad_Alumnos", resumen.columns)

if __name__ == "__main__":
    unittest.main()
