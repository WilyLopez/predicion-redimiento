# Informe del Sistema: Analisis de Riesgo y Prediccion Estudiantil

Este documento proporciona una descripcion completa de la funcionalidad, operacion y beneficios de la aplicacion de Analisis de Riesgo y Prediccion del Rendimiento Estudiantil.

---

## 1. ¿Que hace el sistema?

El sistema es una solucion de inteligencia institucional orientada a la **retencion de estudiantes y la prevencion de la desercion**. Su proposito principal es procesar informacion socioeconomica y academica para:

*   **Predecir el estado final del estudiante:** Clasifica si un alumno terminara como Graduado, Matriculado (activo) o Desercion (deserto).
*   **Calcular un Score de Riesgo:** Devuelve un valor porcentual exacto de probabilidad de abandono.
*   **Identificar perfiles de vulnerabilidad:** Agrupa a la poblacion estudiantil en grupos socioeconomicos diferenciados al ingreso para detectar riesgos de forma anticipada.
*   **Auditar predicciones con IA Explicable (XAI):** Abre la "caja negra" del modelo, listando las razones especificas que incrementan o disminuyen el riesgo de cada alumno en particular.

---

## 2. ¿Como funciona? (Proceso Tecnico)

El core del sistema opera a traves de una secuencia automatizada en Python:

```text
[Datos del Estudiante] 
       │
       ▼
1. Preprocesamiento (Escalamiento de notas y codificacion en procesador_datos.py)
       │
       ▼
2. Clasificacion (Inferencia con XGBoost/Random Forest en modelos.py)
       ├─► Genera Prediccion (Desercion, Matriculado, Graduado)
       └─► Calcula Score de Riesgo (Probabilidad de desercion)
       │
       ▼
3. Clustering (K-Means en agrupamiento.py)
       └─► Asigna el perfil socioeconomico (0, 1 o 2)
       │
       ▼
4. Explicabilidad (Calculo de impacto SHAP en explicabilidad.py)
       └─► Identifica las variables determinantes (ej. deudor, notas bajas)
       │
       ▼
[Visualizacion en app/tablero.py (Streamlit)]
```

---

## 3. ¿Que se puede hacer en el sistema? (Funcionalidades del Tablero)

A traves del [tablero.py](file:///c:/Users/Lenovo/OneDrive/Escritorio/rendimiento-estudiantil/app/tablero.py), los usuarios (directores academicos, tutores y personal administrativo) pueden realizar:

### A. Calculo Individual en Tiempo Real
*   Diligenciar un formulario interactivo con los datos demograficos, situacion de beca/deudas y rendimiento academico de un alumno.
*   Ver de inmediato su nivel de riesgo categorizado en **Bajo (verde)**, **Medio (amarillo)** o **Alto (rojo)**.
*   Visualizar la grafica SHAP para ver el peso de cada variable en ese resultado particular (ej. saber si el riesgo es puramente academico o economico).

### B. Prediccion Masiva por Carga de Archivos
*   Subir un archivo CSV con la nomina de alumnos inscritos.
*   Obtener instantaneamente el listado ordenado de mayor a menor riesgo.
*   Descargar el reporte completo enriquecido con las predicciones para su integracion en hojas de calculo.

### C. Monitoreo Institucional
*   Revisar graficas generales del estado actual de la universidad (tasas globales).
*   Visualizar perfiles socioeconomicos grupales para ver cuales son los grupos mas vulnerables antes de que inicien clases.

---

## 4. ¿En que ayuda a la institucion educativa? (Impacto y Beneficios)

*   **Intervencion Temprana:** Permite actuar en el primer mes de clases (gracias al modulo de clustering socioeconomico) en lugar de esperar al final de semestre cuando el alumno ya ha reprobado o abandonado.
*   **Asignacion Inteligente de Recursos:** Facilita la identificacion de estudiantes que necesitan apoyo financiero (becas) o apoyo academico (tutorias dirigidas), canalizando los recursos a los estudiantes con riesgo alto prioritario.
*   **Explicabilidad Clinica Academica:** En lugar de dar una alerta vacia, el sistema le dice al tutor *por que* el alumno esta en riesgo (ej. 'Tiene deudas y reprobo 2 materias'), permitiendo una conversacion de asesoria mucho mas focalizada y empatica.
*   **Reduccion de la Desercion:** Al automatizar y sistematizar las alertas, la institucion puede mejorar sus tasas de retencion y exito estudiantil.
