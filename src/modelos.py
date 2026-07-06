import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
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
