import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from src.excepciones import ErrorModeloNoEntrenado, ErrorValidacionDatos
from src.decoradores import medir_tiempo, capturar_errores

class ClasificadorRendimiento:
    """Clase para entrenar y evaluar modelos de predicción de rendimiento estudiantil."""

    def __init__(self, tipo_modelo="bosque_aleatorio", semilla_aleatoria=42):
        self.tipo_modelo = tipo_modelo
        self.semilla_aleatoria = semilla_aleatoria
        self.modelo = None
        self.inicializar_modelo()

    def inicializar_modelo(self):
        """Inicializa el modelo seleccionado con parametros balanceados."""
        if self.tipo_modelo == "bosque_aleatorio":
            self.modelo = RandomForestClassifier(
                n_estimators=150,
                max_depth=12,
                class_weight="balanced",
                random_state=self.semilla_aleatoria
            )
        elif self.tipo_modelo == "regresion_logistica":
            self.modelo = LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=self.semilla_aleatoria
            )
        elif self.tipo_modelo == "xgboost":
            self.modelo = XGBClassifier(
                n_estimators=150,
                max_depth=6,
                learning_rate=0.1,
                random_state=self.semilla_aleatoria,
                eval_metric="mlogloss"
            )
        else:
            raise ErrorValidacionDatos(
                f"El tipo de modelo '{self.tipo_modelo}' no esta soportado. "
                "Use 'bosque_aleatorio', 'regresion_logistica' o 'xgboost'."
            )

    @capturar_errores
    @medir_tiempo
    def entrenar(self, X_entrenamiento, y_entrenamiento):
        """Entrena el modelo de machine learning en las particiones provistas."""
        self.modelo.fit(X_entrenamiento, y_entrenamiento)
        return self

    @capturar_errores
    def predecir(self, X_prueba):
        """Predice la clase final para una o mas instancias."""
        if self.modelo is None:
            raise ErrorModeloNoEntrenado("El modelo no ha sido entrenado todavia.")
        return self.modelo.predict(X_prueba)

    @capturar_errores
    def predecir_probabilidad(self, X_prueba):
        """Predice la probabilidad de cada clase."""
        if self.modelo is None:
            raise ErrorModeloNoEntrenado("El modelo no ha sido entrenado todavia.")
        return self.modelo.predict_proba(X_prueba)

    @capturar_errores
    @medir_tiempo
    def evaluar(self, X_prueba, y_prueba):
        """Evalua el rendimiento del modelo y retorna un diccionario de metricas."""
        if self.modelo is None:
            raise ErrorModeloNoEntrenado("El modelo no ha sido entrenado todavia.")
        
        predicciones = self.predecir(X_prueba)
        precision = accuracy_score(y_prueba, predicciones)
        reporte = classification_report(y_prueba, predicciones, output_dict=True)
        matriz = confusion_matrix(y_prueba, predicciones)

        metricas = {
            "precision_global": precision,
            "reporte_clasificacion": reporte,
            "matriz_confusion": matriz
        }
        return metricas

    @capturar_errores
    @medir_tiempo
    def validar_cruzado(self, X, y, n_splits=5):
        """Ejecuta validacion cruzada estratificada (K-Fold) para verificar la estabilidad del modelo.
        
        Retorna un diccionario con la precision media, la desviacion estandar y los scores por fold.
        Esto confirma que el accuracy reportado no es producto de sobreajuste.
        """
        if self.modelo is None:
            raise ErrorModeloNoEntrenado("El modelo no ha sido entrenado todavia.")
        
        cv_estratificado = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=self.semilla_aleatoria)
        scores = cross_val_score(
            self.modelo, X, y, cv=cv_estratificado, scoring="accuracy", n_jobs=-1
        )
        
        return {
            "scores_por_fold": scores,
            "precision_media": round(float(scores.mean()), 4),
            "desviacion_estandar": round(float(scores.std()), 4),
            "n_splits": n_splits
        }

    @capturar_errores
    def guardar_modelo(self, ruta_archivo):
        """Persiste el modelo entrenado en disco usando joblib para evitar re-entrenamientos."""
        if self.modelo is None:
            raise ErrorModeloNoEntrenado("No hay modelo entrenado para guardar.")
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        joblib.dump(self.modelo, ruta_archivo)

    @capturar_errores
    def cargar_modelo(self, ruta_archivo):
        """Carga un modelo previamente guardado desde disco, omitiendo el re-entrenamiento."""
        if not os.path.exists(ruta_archivo):
            raise ErrorValidacionDatos(f"No se encontro el modelo guardado en: {ruta_archivo}")
        self.modelo = joblib.load(ruta_archivo)
        return self
