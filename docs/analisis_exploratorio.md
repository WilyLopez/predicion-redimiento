# Reporte de Analisis Exploratorio de Datos (EDA)

Este reporte detalla los hallazgos principales obtenidos al explorar el conjunto de datos de desercion y rendimiento de los estudiantes.

---

## 1. Distribucion de la Variable Objetivo (Target)

El dataset consta de **4,424 registros** con la siguiente distribucion de estados estudiantiles:
*   **Graduado (Graduate):** 2,209 estudiantes (~49.9%)
*   **Desercion (Dropout):** 1,421 estudiantes (~32.1%)
*   **Matriculado (Enrolled):** 794 estudiantes (~18.0%)

*Conclusion:* El problema presenta desbalance moderado. Por esta razon, el clasificador utiliza pesos balanceados (`class_weight="balanced"`) para evitar sesgos hacia la clase mayoritaria (Graduado).

---

## 2. Variables de Alto Impacto Identificadas

A traves de correlaciones y analisis cruzados, se identificaron factores determinantes para predecir la desercion:

### Factores Financieros (Deudores y Matricula)
*   **Matricula al dia (Tuition fees up to date):** Es el indicador individual mas fuerte de exito. El ~92% de los estudiantes que desertan tenian pagos atrasados o matriculas sin regularizar al momento del analisis.
*   **Estado de Deudor (Debtor):** Estudiantes registrados como deudores presentan una tasa de desercion 3 veces mayor comparado con estudiantes con finanzas al dia.

### Factores de Apoyo (Becarios)
*   **Beca (Scholarship holder):** Contar con una beca reduce la desercion en mas del ~60%. Representa un factor protector clave que el modelo pondera fuertemente como mitigante de riesgo.

### Factores Academicos (Desempeño en Semestres 1 y 2)
*   **Unidades Curriculares Aprobadas:** El numero de materias aprobadas en el primer y segundo semestre tiene una relacion lineal directa con la graduacion. Estudiantes que aprueban menos de 3 materias en su primer semestre caen en la zona de riesgo alto.
*   **Calificaciones:** La nota promedio de las unidades evaluadas en el segundo semestre tiene una correlacion de 0.61 con la persistencia academica.

---

## 3. Conclusiones del Analisis de Datos

Cualquier modelo predictivo eficaz debe integrar tanto la condicion financiera previa (deudor, beca) como la capacidad de adaptacion academica del primer año (notas y aprobaciones del 1er y 2do semestre) para generar un score de riesgo confiable.
