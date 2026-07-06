# Reporte de Evaluacion de Modelos

Este reporte documenta los resultados de rendimiento y la comparativa entre los algoritmos de machine learning evaluados para la prediccion del rendimiento estudiantil.

---

## 1. Metricas de Rendimiento Obtenidas

Los modelos fueron entrenados y validados sobre una division estratificada del dataset (80% entrenamiento, 20% prueba). Los resultados de precision global (Accuracy) son:

| Algoritmo | Precision Global (Accuracy) | Ventajas Principales | Desventajas / Limitaciones |
| :--- | :--- | :--- | :--- |
| **XGBoost** | **76.61%** | Maxima capacidad predictiva; maneja interacciones complejas. | Requiere mayor costo computacional para SHAP. |
| **Random Forest** | **75.03%** | Estable, robusto ante sobreajuste, explicabilidad nativa rapida. | Menor precision marginal comparado con XGBoost. |
| **Regresion Logistica** | **74.01%** | Altamente interpretable, ejecucion instantanea. | No captura interacciones no lineales complejas. |

---

## 2. Detalle de Clasificacion por Clase (XGBoost)

El reporte de clasificacion detallado para XGBoost muestra:

*   **Desercion (Dropout):** F1-Score de ~0.77. El modelo presenta un excelente equilibrio entre Precision (evitar falsas alarmas) y Recall (capturar a la mayor cantidad de alumnos en riesgo).
*   **Graduado (Graduate):** F1-Score de ~0.84. Es la clase mas predecible debido a patrones de comportamiento muy consistentes (notas altas y matricula al dia).
*   **Matriculado (Enrolled):** F1-Score de ~0.49. Esta es la clase mas compleja debido a que representa una transicion inestable (alumnos que aun no desertan pero tampoco se graduan).

---

## 3. Justificacion de la Seleccion de Modelos

El tablero permite cambiar el modelo en tiempo real para adaptarse a las necesidades institucionales:
1.  **XGBoost:** Recomendado para la generacion automatica de alertas y toma de acciones de retencion debido a su alta tasa de deteccion (Recall).
2.  **Random Forest:** Recomendado para analisis rapidos de explicabilidad SHAP sin demoras en maquinas con recursos limitados.
3.  **Regresion Logistica:** Excelente linea base para validacion estadistica basica.
