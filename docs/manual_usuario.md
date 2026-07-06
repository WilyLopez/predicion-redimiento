# Manual de Usuario del Tablero Web

Este manual proporciona las instrucciones para operar la aplicacion web interactiva de analisis y prediccion de riesgo estudiantil.

---

## 1. Inicio rapido

Para arrancar el tablero web interactivo desde la terminal:
```powershell
streamlit run app/tablero.py
```
Esto iniciara un servidor local y abrira la interfaz en la direccion de tu navegador: `http://localhost:8501`.

---

## 2. Descripcion de Pestañas (Tablas de Navegacion)

La interfaz se divide en tres secciones principales:

### Pestaña A: Estadisticas Institucionales
*   **Tarjetas de Resumen:** Visualizacion de la matricula analizada, tasa de desercion historica y tasa de graduados.
*   **Graficas Descriptivas:** Distribucion de alumnos por estado y desglose de desercion segun la situacion financiera.
*   **Segmentacion Socioeconomica:** Muestra el reporte de los perfiles de estudiantes identificados por K-Means, detallando su edad de ingreso, porcentaje de deudores y porcentaje de becarios por perfil.

### Pestaña B: Calculadora de Riesgo Individual
Permite evaluar la probabilidad de desercion de un alumno especifico ingresando sus atributos en el formulario interactivo:
1.  **Ingresar datos:** Diligencie los campos (Edad, Genero, Deudas, Calificaciones previas y del primer año).
2.  **Calcular:** Presione el boton "Calcular Riesgo del Estudiante".
3.  **Visualizar:**
    *   **Score de Riesgo:** Porcentaje dinamico de probabilidad de desercion.
    *   **Nivel:** Categorizado en Alto (rojo), Medio (amarillo) o Bajo (verde).
    *   **Explicacion SHAP:** Grafica interactiva que muestra que variables aumentan el riesgo del alumno (barras rojas) y cuales actuan como factores protectores reduciendolo (barras azules).

### Pestaña C: Prediccion Masiva (Lotes)
Diseñado para la evaluacion simultanea de cohortes enteras de estudiantes:
1.  **Subir Archivo:** Suba un archivo en formato CSV con el mismo encabezado que el dataset original.
2.  **Ver Predicciones:** La herramienta calculara de inmediato el estado predicho y el score de riesgo para todos los alumnos.
3.  **Filtrar:** Los registros se ordenaran automaticamente priorizando a los alumnos con riesgo de desercion mas alto.
4.  **Descargar Reporte:** Permite exportar un archivo CSV con las predicciones y asignaciones de perfiles socioeconomicos añadidas.
