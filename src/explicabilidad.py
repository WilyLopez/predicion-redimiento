import shap
import pandas as pd
import numpy as np
from src.excepciones import ErrorModeloNoEntrenado, ErrorValidacionDatos
from src.decoradores import medir_tiempo, capturar_errores

class ExplicadorRiesgo:
    """Clase para explicar las predicciones de riesgo individual e institucional usando SHAP."""

    def __init__(self, clasificador_entrenado, datos_referencia):
        if clasificador_entrenado.modelo is None:
            raise ErrorModeloNoEntrenado("El clasificador provisto no ha sido entrenado.")
        
        self.clasificador = clasificador_entrenado
        self.modelo_subyacente = clasificador_entrenado.modelo
        self.datos_referencia = datos_referencia
        self.explicador = None
        self.inicializar_explicador()

    @capturar_errores
    def inicializar_explicador(self):
        """Inicializa el explicador SHAP adecuado segun el tipo de modelo."""
        # Para modelos de arboles (Bosque Aleatorio, XGBoost) usamos TreeExplainer
        if self.clasificador.tipo_modelo in ["bosque_aleatorio", "xgboost"]:
            try:
                # Intentar con explicador interventional (usa datos de referencia para valores base reales)
                muestra_referencia = self.datos_referencia.head(100) if len(self.datos_referencia) > 100 else self.datos_referencia
                self.explicador = shap.TreeExplainer(self.modelo_subyacente, data=muestra_referencia)
            except Exception:
                # Si falla (ej. por incompatibilidad en splits categoricos de XGBoost), usar perturbacion por caminos
                self.explicador = shap.TreeExplainer(self.modelo_subyacente, feature_perturbation="tree_path_dependent")
        else:
            # Para Regresion Logistica usamos el explicador lineal o generalizado
            muestra_referencia = self.datos_referencia.head(100) if len(self.datos_referencia) > 100 else self.datos_referencia
            self.explicador = shap.Explainer(self.modelo_subyacente, muestra_referencia)

    @capturar_errores
    def explicar_instancia(self, instancia_estudiante):
        """Calcula los valores SHAP para una unica instancia de estudiante."""
        if self.explicador is None:
            raise ErrorValidacionDatos("El explicador SHAP no esta inicializado.")
        
        try:
            # Calcular valores SHAP
            valores_shap = self.explicador(instancia_estudiante)
        except (NotImplementedError, Exception):
            # Si hay un error (ej. por divisiones categoricas en XGBoost), usar perturbacion por caminos
            if self.clasificador.tipo_modelo in ["bosque_aleatorio", "xgboost"]:
                self.explicador = shap.TreeExplainer(self.modelo_subyacente, feature_perturbation="tree_path_dependent")
                valores_shap = self.explicador(instancia_estudiante)
            else:
                raise
        
        # En clasificacion multiclase (Desercion, Matriculado, Graduado),
        # SHAP devuelve un array de 3 dimensiones para cada clase.
        # Nos interesa explicar la probabilidad de desercion (indice 0 en MAPEO_OBJETIVO).
        if len(valores_shap.shape) == 3:
            # Estructura: (instancias, caracteristicas, clases)
            valores_instancia = valores_shap[0, :, 0]
        else:
            valores_instancia = valores_shap[0]
            
        return valores_instancia

    @capturar_errores
    @medir_tiempo
    def calcular_importancia_global(self, X_muestra, max_muestra=200):
        """Calcula los valores SHAP globales sobre una muestra de datos para generar un resumen de importancia de variables.
        
        Retorna un DataFrame con el impacto medio absoluto de cada variable (mean |SHAP|),
        ordenado de mayor a menor importancia. Util para el summary plot institucional.
        """
        if self.explicador is None:
            raise ErrorValidacionDatos("El explicador SHAP no esta inicializado.")
        
        # Limitar la muestra para eficiencia computacional
        muestra = X_muestra.head(max_muestra) if len(X_muestra) > max_muestra else X_muestra
        
        try:
            valores_shap_global = self.explicador(muestra)
        except Exception:
            if self.clasificador.tipo_modelo in ["bosque_aleatorio", "xgboost"]:
                explicador_temp = shap.TreeExplainer(
                    self.modelo_subyacente, feature_perturbation="tree_path_dependent"
                )
                valores_shap_global = explicador_temp(muestra)
            else:
                raise
        
        # Para multiclase, extraer la clase Desercion (indice 0)
        if len(valores_shap_global.shape) == 3:
            shap_matrix = valores_shap_global.values[:, :, 0]
        else:
            shap_matrix = valores_shap_global.values
        
        importancia_media = np.mean(np.abs(shap_matrix), axis=0)
        
        df_importancia = pd.DataFrame({
            "Caracteristica": muestra.columns.tolist(),
            "Importancia_Media_SHAP": importancia_media
        }).sort_values(by="Importancia_Media_SHAP", ascending=False).reset_index(drop=True)
        
        return df_importancia
