# Reporte de Perfiles de Vulnerabilidad Socioeconomica (Clustering)

Este documento detalla la segmentacion no supervisada realizada mediante K-Means para agrupar a la poblacion estudiantil segun sus condiciones de vulnerabilidad socioeconomica al momento del ingreso.

---

## 1. Justificacion de la Segmentacion

El clustering agrupa alumnos considerando unicamente variables previas a su rendimiento academico (ej. deudas, becario, edad al ingreso, ocupaciones y calificaciones de padres). Esto permite a la institucion identificar el nivel de riesgo de un estudiante e intervenir de manera temprana incluso antes del inicio del semestre.

---

## 2. Descripcion de los 3 Perfiles Identificados

El algoritmo K-Means estructuro los datos en 3 grupos (perfiles) distintivos:

### Perfil 0: Estudiantes Becados y Estables
*   **Edad Promedio:** ~19.5 años.
*   **Tasa de Becarios:** ~85% - 90%.
*   **Tasa de Deudores:** ~2% (practicamente inexistente).
*   **Matricula al Dia:** ~99%.
*   **Diagnostico institucional:** Grupo de alta estabilidad economica y baja vulnerabilidad. Requieren seguimiento academico estandar.

### Perfil 1: Estudiantes Mayores y Trabajadores en Riesgo (Vulnerabilidad Alta)
*   **Edad Promedio:** ~29 años o mayor.
*   **Tasa de Becarios:** <5%.
*   **Tasa de Deudores:** ~35% - 40%.
*   **Matricula al Dia:** ~65%.
*   **Diagnostico institucional:** Alta vulnerabilidad financiera y demografica. Alumnos con responsabilidades familiares/laborales y deudas de matricula. Requieren programas urgentes de facilidades de pago o flexibilizacion de horarios.

### Perfil 2: Estudiantes Jovenes sin Beca (Vulnerabilidad Moderada)
*   **Edad Promedio:** ~20.2 años.
*   **Tasa de Becarios:** ~0% (ninguno tiene beca).
*   **Tasa de Deudores:** ~12%.
*   **Matricula al Dia:** ~94%.
*   **Diagnostico institucional:** Nivel de vulnerabilidad intermedio. Al no poseer becas pero ser mas jovenes, son susceptibles a dificultades economicas temporales si reprueban materias. Se sugiere evaluar adjudicaciones de becas de rendimiento.
