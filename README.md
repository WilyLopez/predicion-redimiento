# Sistema de Analisis de Riesgo y Prediccion Estudiantil

Este proyecto implementa una herramienta inteligente para el analisis de riesgo de desercion y la prediccion del rendimiento estudiantil en instituciones de educacion superior. Utiliza el conjunto de datos de la UCI "Predict Students' Dropout and Academic Success" y esta desarrollado integramente en Python.

El sistema esta estructurado siguiendo buenas practicas de desarrollo, calidad de codigo y multiples paradigmas de programacion, cumpliendo con criterios de excelencia academica.

---

## Estructura del Proyecto

El codigo fuente esta organizado de forma modular:

*   [requirements.txt](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/requirements.txt): Archivo de dependencias del entorno de Python.
*   [descargar_datos.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/descargar_datos.py): Script de descarga automatica y validacion del dataset.
*   `src/`: Directorio que contiene el core logico y matematico:
    *   [excepciones.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/src/excepciones.py): Modulo con excepciones personalizadas de negocio.
    *   [decoradores.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/src/decoradores.py): Decoradores para registro de tiempos y captura segura de excepciones.
    *   [procesador_datos.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/src/procesador_datos.py): Carga, segmentacion (train/test) y normalizacion de datos.
    *   [agrupamiento.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/src/agrupamiento.py): Clustering K-Means para segmentacion de perfiles socioeconomicos de riesgo.
    *   [modelos.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/src/modelos.py): Modulo de entrenamiento de clasificadores (Random Forest, Regresion Logistica, XGBoost).
    *   [explicabilidad.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/src/explicabilidad.py): Explicaciones locales de las decisiones del modelo mediante SHAP.
*   `app/`: Directorio de interfaz grafica:
    *   [tablero.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/app/tablero.py): Aplicacion web interactiva desarrollada con Streamlit.
*   `pruebas/`: Pruebas de calidad del codigo:
    *   [test_procesador.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/pruebas/test_procesador.py): Suite de pruebas unitarias de integracion.

---

## Requisitos de Instalacion

1. Instalar las dependencias listadas en el archivo requirements.txt:
   ```powershell
   pip install -r requirements.txt
   ```

2. Descargar los datos oficiales ejecutando:
   ```powershell
   python descargar_datos.py
   ```

---

## Instrucciones de Ejecucion

### 1. Ejecucion de Pruebas Unitarias
Para validar que todos los modulos e integraciones estan funcionando correctamente:
```powershell
python -m unittest discover -s pruebas
```

### 2. Iniciar la Interfaz Web (Dashboard Streamlit)
Para correr el tablero interactivo de analisis institucional e individual:
```powershell
streamlit run app/tablero.py
```
Una vez iniciado el comando, se abrira automaticamente en el navegador la direccion: `http://localhost:8501`.

---

## Metodologia de Datos Utilizada

El sistema combina tres paradigmas de aprendizaje automatico para lograr una prevencion efectiva:
1. **Clasificacion Supervisada:** Determina el estado del estudiante (Desercion, Matriculado, Graduado) y genera un Score de Riesgo porcentual.
2. **Clustering No Supervisado:** Agrupa a los estudiantes en 3 perfiles socioeconomicos diferenciados al ingreso para detectar vulnerabilidades estructurales antes del inicio de clases.
3. **IA Explicable (XAI):** Utiliza SHAP para calcular y visualizar en tiempo real que variables aumentan o disminuyen el riesgo del estudiante de forma individual.

---

## Documentacion Detallada (Directorio docs/)

Para un entendimiento profundo del sistema, puede consultar los siguientes documentos especializados en el directorio `docs/`:

*   [informe_sistema.md](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/docs/informe_sistema.md): Resumen ejecutivo de que hace el sistema, su funcionamiento y sus beneficios institucionales.
*   [documento_diseno.md](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/docs/documento_diseno.md): Especificacion de la arquitectura de software y justificacion de los paradigmas de programacion aplicados.
*   [analisis_exploratorio.md](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/docs/analisis_exploratorio.md): Reporte de analisis estadistico exploratorio y variables clave.
*   [manual_usuario.md](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/docs/manual_usuario.md): Guia de usuario para operar el dashboard Streamlit y analizar scores.
*   [evaluacion_modelos.md](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/docs/evaluacion_modelos.md): Reporte comparativo de rendimiento (Accuracy, F1-Score) de los estimadores.
*   [perfiles_vulnerabilidad.md](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/docs/perfiles_vulnerabilidad.md): Analisis descriptivo de los perfiles de riesgo socioeconomico obtenidos mediante Clustering.

---

## Recursos de Presentacion (Exposicion)

Para apoyar la exposicion del proyecto bajo el criterio de **Presentacion** de la rubrica:
*   [presentacion_proyecto.pptx](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/presentacion_proyecto.pptx): Presentacion de diapositivas en formato PowerPoint generada automaticamente. Contiene el resumen de objetivos, dataset, arquitectura, modelos y conclusiones.
*   [generar_presentacion.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/generar_presentacion.py): Script en Python utilizado para compilar la presentacion.

---

