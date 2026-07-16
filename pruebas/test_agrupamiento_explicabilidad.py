import unittest
import pandas as pd
import numpy as np
import tempfile
import os
import sys

# Asegurar que src/ sea encontrable desde el directorio raiz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.procesador_datos import ProcesadorDatos
from src.modelos import ClasificadorRendimiento
from src.agrupamiento import AgrupadorEstudiantes
from src.explicabilidad import ExplicadorRiesgo


# ---------- Datos ficticios compartidos ----------
COLUMNAS_BASE = [
    "Marital status", "Nationality", "Displaced", "Educational special needs",
    "Debtor", "Tuition fees up to date", "Gender", "Scholarship holder",
    "Age at enrollment", "International", "Mother's qualification",
    "Father's qualification", "Mother's occupation", "Father's occupation",
    "Admission grade", "Unemployment rate", "Inflation rate", "GDP", "Target"
]


def generar_df_ficticio(n=60, seed=42):
    """Genera un DataFrame de prueba con datos aleatorios."""
    np.random.seed(seed)
    clases = ["Dropout", "Graduate", "Enrolled"]
    filas = []
    for _ in range(n):
        fila = [
            np.random.randint(1, 4),         # Marital status
            1,                               # Nationality
            np.random.randint(0, 2),         # Displaced
            0,                               # Educational special needs
            np.random.randint(0, 2),         # Debtor
            np.random.randint(0, 2),         # Tuition fees up to date
            np.random.randint(0, 2),         # Gender
            np.random.randint(0, 2),         # Scholarship holder
            np.random.randint(18, 50),       # Age at enrollment
            0,                               # International
            1, 1, 1, 1,                      # Parents qualification/occupation
            np.random.uniform(95.0, 200.0),  # Admission grade
            np.random.uniform(7.0, 16.0),    # Unemployment rate
            np.random.uniform(0.5, 3.0),     # Inflation rate
            np.random.uniform(-2.0, 2.0),    # GDP
            np.random.choice(clases)         # Target
        ]
        filas.append(fila)
    return pd.DataFrame(filas, columns=COLUMNAS_BASE)


# =========================================================================
# TEST SUITE 1: Agrupamiento (K-Means + Silhouette)
# =========================================================================
class PruebasAgrupamiento(unittest.TestCase):
    """Pruebas unitarias para el modulo agrupamiento.py."""

    def setUp(self):
        self.df = generar_df_ficticio(n=60)

    def test_entrenamiento_kmeans(self):
        """Verifica que el agrupador entrena sin errores con K=3."""
        agrupador = AgrupadorEstudiantes(n_clusters=3)
        resultado = agrupador.entrenar_agrupamiento(self.df)
        self.assertIsNotNone(resultado)
        self.assertTrue(
            hasattr(agrupador.modelo_kmeans, "labels_"),
            "El modelo K-Means debe tener atributo 'labels_' tras el entrenamiento."
        )

    def test_silhouette_score_calculado(self):
        """Verifica que el Silhouette Score se calcula y esta en el rango valido [-1, 1]."""
        agrupador = AgrupadorEstudiantes(n_clusters=3)
        agrupador.entrenar_agrupamiento(self.df)
        score = agrupador.obtener_silhouette()
        self.assertIsInstance(score, float, "El Silhouette Score debe ser float.")
        self.assertGreater(score, -1.0, "El Silhouette Score debe ser mayor que -1.")
        self.assertLessEqual(score, 1.0, "El Silhouette Score debe ser <= 1.")

    def test_silhouette_por_k_rango(self):
        """Verifica que calcular_silhouette_por_k retorna scores para cada K del rango."""
        agrupador = AgrupadorEstudiantes(n_clusters=3)
        agrupador.entrenar_agrupamiento(self.df)
        resultados = agrupador.calcular_silhouette_por_k(self.df, rango_k=(2, 4))
        self.assertEqual(len(resultados), 3, "Debe retornar un score para K=2, K=3 y K=4.")
        for k, score in resultados.items():
            self.assertIsInstance(score, float)

    def test_asignar_perfil_dimensiones(self):
        """Verifica que asignar_perfil retorna una etiqueta por cada fila de entrada."""
        agrupador = AgrupadorEstudiantes(n_clusters=3)
        agrupador.entrenar_agrupamiento(self.df)
        etiquetas = agrupador.asignar_perfil(self.df)
        self.assertEqual(len(etiquetas), len(self.df))
        self.assertTrue(all(e in [0, 1, 2] for e in etiquetas))

    def test_descripcion_perfiles_columnas(self):
        """Verifica que el resumen de perfiles contiene las columnas estadisticas esperadas."""
        agrupador = AgrupadorEstudiantes(n_clusters=3)
        agrupador.entrenar_agrupamiento(self.df)
        resumen = agrupador.obtener_descripcion_perfiles(self.df)
        self.assertEqual(len(resumen), 3)
        for col in ["Perfil", "Cantidad_Alumnos", "Edad_Promedio",
                    "Porcentaje_Becarios_Pct", "Porcentaje_Deudores_Pct", "Matricula_Al_Dia_Pct"]:
            self.assertIn(col, resumen.columns, f"Falta la columna '{col}' en el resumen.")


# =========================================================================
# TEST SUITE 2: Explicabilidad (SHAP) + K-Fold + Persistencia
# =========================================================================
class PruebasExplicabilidadYValidacion(unittest.TestCase):
    """Pruebas unitarias para explicabilidad.py, validacion cruzada y joblib en modelos.py."""

    def setUp(self):
        self.df = generar_df_ficticio(n=80)

        # Guardar en archivo temporal
        self.archivo_temporal = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        self.df.to_csv(self.archivo_temporal.name, sep=";", index=False)
        self.archivo_temporal.close()

        # Preparar pipeline
        self.procesador = ProcesadorDatos(self.archivo_temporal.name)
        self.procesador.cargar_datos()
        self.X_train, self.X_test, self.y_train, self.y_test = \
            self.procesador.preparar_datos(fraccion_prueba=0.25)

        # Entrenar Random Forest (mas rapido que XGBoost en pruebas unitarias)
        self.clasificador = ClasificadorRendimiento(tipo_modelo="bosque_aleatorio")
        self.clasificador.entrenar(self.X_train, self.y_train)

    def tearDown(self):
        if os.path.exists(self.archivo_temporal.name):
            os.remove(self.archivo_temporal.name)

    def test_inicializacion_explicador(self):
        """Verifica que ExplicadorRiesgo se inicializa correctamente con el modelo entrenado."""
        explicador = ExplicadorRiesgo(self.clasificador, self.X_train)
        self.assertIsNotNone(
            explicador.explicador,
            "El explicador SHAP debe estar inicializado tras la construccion."
        )

    def test_explicar_instancia_dimensiones(self):
        """Verifica que explicar_instancia retorna tantos valores SHAP como caracteristicas."""
        explicador = ExplicadorRiesgo(self.clasificador, self.X_train)
        instancia = self.X_test.head(1)
        valores = explicador.explicar_instancia(instancia)
        n_caracteristicas = len(self.X_train.columns)
        self.assertEqual(
            len(valores), n_caracteristicas,
            "El numero de valores SHAP debe coincidir con el numero de caracteristicas."
        )

    def test_importancia_global_shap(self):
        """Verifica que calcular_importancia_global retorna DataFrame con columnas correctas."""
        explicador = ExplicadorRiesgo(self.clasificador, self.X_train)
        df_imp = explicador.calcular_importancia_global(self.X_train, max_muestra=40)
        self.assertIsInstance(df_imp, pd.DataFrame)
        self.assertIn("Caracteristica", df_imp.columns)
        self.assertIn("Importancia_Media_SHAP", df_imp.columns)
        self.assertGreater(len(df_imp), 0, "El DataFrame de importancia no debe estar vacio.")
        # Mean |SHAP| siempre debe ser >= 0
        self.assertTrue(
            (df_imp["Importancia_Media_SHAP"] >= 0).all(),
            "Los valores de importancia media |SHAP| deben ser no negativos."
        )

    def test_validacion_cruzada_kfold(self):
        """Verifica que validar_cruzado retorna las claves esperadas con valores validos."""
        X_total = pd.concat([self.X_train, self.X_test])
        y_total = pd.concat([self.y_train, self.y_test])
        resultado = self.clasificador.validar_cruzado(X_total, y_total, n_splits=3)

        self.assertIn("scores_por_fold", resultado)
        self.assertIn("precision_media", resultado)
        self.assertIn("desviacion_estandar", resultado)
        self.assertEqual(len(resultado["scores_por_fold"]), 3)
        self.assertGreater(resultado["precision_media"], 0.0)
        self.assertLessEqual(resultado["precision_media"], 1.0)

    def test_persistencia_modelo_joblib(self):
        """Verifica que el modelo se guarda y carga correctamente con joblib."""
        directorio_temp = tempfile.mkdtemp()
        ruta_modelo = os.path.join(directorio_temp, "modelo_test.pkl")
        try:
            self.clasificador.guardar_modelo(ruta_modelo)
            self.assertTrue(os.path.exists(ruta_modelo), "El archivo guardado debe existir.")

            # Cargar en un nuevo clasificador
            nuevo_clf = ClasificadorRendimiento(tipo_modelo="bosque_aleatorio")
            nuevo_clf.cargar_modelo(ruta_modelo)
            self.assertIsNotNone(nuevo_clf.modelo)

            # Las predicciones deben ser identicas
            pred_original = self.clasificador.predecir(self.X_test)
            pred_cargado = nuevo_clf.predecir(self.X_test)
            np.testing.assert_array_equal(
                pred_original, pred_cargado,
                "Las predicciones del modelo cargado deben ser identicas al original."
            )
        finally:
            if os.path.exists(ruta_modelo):
                os.remove(ruta_modelo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
