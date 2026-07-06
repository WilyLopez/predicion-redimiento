import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from src.excepciones import ErrorValidacionDatos
from src.decoradores import medir_tiempo, capturar_errores

class AgrupadorEstudiantes:
    """Clase para agrupar estudiantes según factores socioeconómicos y demográficos."""

    def __init__(self, n_clusters=3, semilla_aleatoria=42):
        self.n_clusters = n_clusters
        self.semilla_aleatoria = semilla_aleatoria
        self.modelo_kmeans = KMeans(n_clusters=n_clusters, random_state=semilla_aleatoria, n_init=10)
        self.normalizador = StandardScaler()
        self.columnas_socioeconomicas = [
            "Marital status", "Nationality", "Displaced", "Educational special needs",
            "Debtor", "Tuition fees up to date", "Gender", "Scholarship holder",
            "Age at enrollment", "International", "Mother's qualification",
            "Father's qualification", "Mother's occupation", "Father's occupation"
        ]

    @capturar_errores
    @medir_tiempo
    def entrenar_agrupamiento(self, datos_estudiantes):
        """Entrena el modelo de clustering K-Means usando variables socioeconomicas."""
        # Verificar que las columnas requeridas existen
        columnas_disponibles = [col for col in self.columnas_socioeconomicas if col in datos_estudiantes.columns]
        if not columnas_disponibles:
            raise ErrorValidacionDatos("No se encontraron columnas socioeconomicas en el dataset para el agrupamiento.")

        # Extraer variables socioeconomicas
        datos_clustering = datos_estudiantes[columnas_disponibles].copy()
        
        # Llenar nulos si existieran
        datos_clustering = datos_clustering.fillna(datos_clustering.median())

        # Normalizar datos para clustering
        datos_normalizados = self.normalizador.fit_transform(datos_clustering)

        # Entrenar K-Means
        self.modelo_kmeans.fit(datos_normalizados)
        return self

    @capturar_errores
    def asignar_perfil(self, datos_estudiantes):
        """Asigna una etiqueta de grupo (cluster) a los estudiantes."""
        if not hasattr(self.modelo_kmeans, "labels_"):
            raise ErrorValidacionDatos("El modelo KMeans no ha sido entrenado aun.")

        columnas_disponibles = [col for col in self.columnas_socioeconomicas if col in datos_estudiantes.columns]
        datos_clustering = datos_estudiantes[columnas_disponibles].copy()
        datos_clustering = datos_clustering.fillna(datos_clustering.median())
        
        datos_normalizados = self.normalizador.transform(datos_clustering)
        return self.modelo_kmeans.predict(datos_normalizados)

    @capturar_errores
    def obtener_descripcion_perfiles(self, datos_estudiantes):
        """Genera estadisticas resumen para cada perfil (cluster) de estudiantes."""
        datos_con_grupos = datos_estudiantes.copy()
        etiquetas_grupos = self.asignar_perfil(datos_estudiantes)
        datos_con_grupos["Perfil_Socioeconomico"] = etiquetas_grupos

        resumen_perfiles = []
        for grupo in range(self.n_clusters):
            sub_grupo = datos_con_grupos[datos_con_grupos["Perfil_Socioeconomico"] == grupo]
            
            # Calcular promedios y porcentajes clave
            edad_promedio = sub_grupo["Age at enrollment"].mean() if "Age at enrollment" in sub_grupo.columns else 0
            porcentaje_becarios = (sub_grupo["Scholarship holder"].mean() * 100) if "Scholarship holder" in sub_grupo.columns else 0
            porcentaje_deudores = (sub_grupo["Debtor"].mean() * 100) if "Debtor" in sub_grupo.columns else 0
            tasa_al_dia = (sub_grupo["Tuition fees up to date"].mean() * 100) if "Tuition fees up to date" in sub_grupo.columns else 0
            
            resumen_perfiles.append({
                "Perfil": grupo,
                "Cantidad_Alumnos": len(sub_grupo),
                "Edad_Promedio": round(edad_promedio, 1),
                "Porcentaje_Becarios_Pct": round(porcentaje_becarios, 1),
                "Porcentaje_Deudores_Pct": round(porcentaje_deudores, 1),
                "Matricula_Al_Dia_Pct": round(tasa_al_dia, 1)
            })

        return pd.DataFrame(resumen_perfiles)
