import sys
import os
# Agregar el directorio raiz del proyecto al path de Python para permitir importaciones de src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from src.procesador_datos import ProcesadorDatos, MAPEO_INVERSO
from src.modelos import ClasificadorRendimiento
from src.agrupamiento import AgrupadorEstudiantes
from src.explicabilidad import ExplicadorRiesgo
from src.excepciones import ErrorRendimientoEstudiantil

# Configuración de página premium
st.set_page_config(
    page_title="Analisis de Riesgo y Rendimiento Estudiantil",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Diccionario de traducción de características para el usuario
MAPEO_COLUMNAS_ESPANOL = {
    "Marital status": "Estado civil",
    "Application mode": "Modo de solicitud",
    "Application order": "Orden de solicitud",
    "Course": "Carrera / Curso",
    "Daytime/evening attendance": "Asistencia (1=Diurno, 0=Nocturno)",
    "Previous qualification": "Calificacion previa",
    "Previous qualification (grade)": "Nota de calificacion previa",
    "Nationality": "Nacionalidad",
    "Mother's qualification": "Calificacion de la madre",
    "Father's qualification": "Calificacion del padre",
    "Mother's occupation": "Ocupacion de la madre",
    "Father's occupation": "Ocupacion del padre",
    "Admission grade": "Nota de admision",
    "Displaced": "Desplazado (1=Si, 0=No)",
    "Educational special needs": "Necesidades especiales (1=Si, 0=No)",
    "Debtor": "Deudor (1=Si, 0=No)",
    "Tuition fees up to date": "Matricula al dia (1=Si, 0=No)",
    "Gender": "Genero (1=Masculino, 0=Femenino)",
    "Scholarship holder": "Becario (1=Si, 0=No)",
    "Age at enrollment": "Edad al inscribirse",
    "International": "Internacional (1=Si, 0=No)",
    "Curricular units 1st sem (credited)": "U. Curriculares acreditadas 1er sem",
    "Curricular units 1st sem (enrolled)": "U. Curriculares matriculadas 1er sem",
    "Curricular units 1st sem (evaluations)": "U. Curriculares evaluadas 1er sem",
    "Curricular units 1st sem (approved)": "U. Curriculares aprobadas 1er sem",
    "Curricular units 1st sem (grade)": "Nota promedio 1er sem",
    "Curricular units 1st sem (without evaluations)": "U. Curriculares sin evaluar 1er sem",
    "Curricular units 2nd sem (credited)": "U. Curriculares acreditadas 2do sem",
    "Curricular units 2nd sem (enrolled)": "U. Curriculares matriculadas 2do sem",
    "Curricular units 2nd sem (evaluations)": "U. Curriculares evaluadas 2do sem",
    "Curricular units 2nd sem (approved)": "U. Curriculares aprobadas 2do sem",
    "Curricular units 2nd sem (grade)": "Nota promedio 2do sem",
    "Curricular units 2nd sem (without evaluations)": "U. Curriculares sin evaluar 2do sem",
    "Unemployment rate": "Tasa de desempleo",
    "Inflation rate": "Tasa de inflacion",
    "GDP": "PIB"
}

# Estilos CSS personalizados para apariencia premium
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #334155;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-card h3 {
        color: #94a3b8;
        font-size: 14px;
        margin: 0;
    }
    .metric-card p {
        color: #f8fafc;
        font-size: 28px;
        font-weight: bold;
        margin: 5px 0 0 0;
    }
    .riesgo-alto {
        color: #ef4444 !important;
    }
    .riesgo-medio {
        color: #eab308 !important;
    }
    .riesgo-bajo {
        color: #22c55e !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_resource
def inicializar_sistema_completo(ruta_datos, tipo_modelo):
    """Inicializa el procesador, entrena el modelo y el agrupador."""
    procesador = ProcesadorDatos(ruta_datos)
    procesador.cargar_datos()
    X_entrenar, X_prueba, y_entrenar, y_prueba = procesador.preparar_datos()
    
    # Entrenar modelo predictivo
    clasificador = ClasificadorRendimiento(tipo_modelo=tipo_modelo)
    clasificador.entrenar(X_entrenar, y_entrenar)
    
    # Entrenar agrupador
    agrupador = AgrupadorEstudiantes(n_clusters=3)
    agrupador.entrenar_agrupamiento(procesador.datos)
    
    # Inicializar explicador
    explicador = ExplicadorRiesgo(clasificador, X_entrenar)
    
    return procesador, clasificador, agrupador, explicador

def main():
    st.title("Sistema de Analisis de Riesgo y Prediccion Estudiantil")
    st.subheader("Herramienta de gestion academica y prevencion de la desercion")
    
    # Barra lateral
    st.sidebar.title("Configuracion")
    
    ruta_datos = "datos/datos_estudiantes.csv"
    if not os.path.exists(ruta_datos):
        st.sidebar.error("Archivo de datos no encontrado. Ejecute descargar_datos.py primero.")
        st.stop()
        
    tipo_modelo = st.sidebar.selectbox(
        "Seleccione el Modelo Predictivo",
        ["bosque_aleatorio", "regresion_logistica", "xgboost"],
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    # Cargar y procesar
    try:
        procesador, clasificador, agrupador, explicador = inicializar_sistema_completo(ruta_datos, tipo_modelo)
    except Exception as e:
        st.error(f"Error al inicializar el sistema: {str(e)}")
        st.stop()
        
    # Pestañas
    pestana1, pestana2, pestana3 = st.tabs([
        "Estadisticas Institucionales",
        "Calculadora de Riesgo Individual",
        "Prediccion Masiva (CSV)"
    ])
    
    # --- PESTAÑA 1: ESTADÍSTICAS INSTITUCIONALES ---
    with pestana1:
        st.write("### Vista General de la Institucion")
        
        # Tarjetas de resumen
        datos_crudos = procesador.datos
        total_alumnos = len(datos_crudos)
        tasa_desercion = (datos_crudos["Target"] == "Dropout").mean() * 100
        tasa_graduados = (datos_crudos["Target"] == "Graduate").mean() * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><h3>Total Alumnos Analizados</h3><p>{total_alumnos:,}</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h3>Tasa de Desercion</h3><p class="riesgo-alto">{tasa_desercion:.1f}%</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><h3>Tasa de Graduacion</h3><p class="riesgo-bajo">{tasa_graduados:.1f}%</p></div>', unsafe_allow_html=True)
            
        st.write("---")
        
        # Division en dos columnas para graficas
        gcol1, gcol2 = st.columns(2)
        
        with gcol1:
            st.write("#### Distribucion de Alumnos por Estado Final")
            fig, ax = plt.subplots(figsize=(6, 4))
            # Colores sobrios
            colores = ["#ef4444", "#3b82f6", "#22c55e"]
            conteo_estados = datos_crudos["Target"].value_counts()
            conteo_estados = conteo_estados.rename(index={"Dropout": "Desercion", "Enrolled": "Matriculado", "Graduate": "Graduado"})
            
            sns.barplot(x=conteo_estados.index, y=conteo_estados.values, palette=colores, ax=ax)
            ax.set_ylabel("Numero de Estudiantes")
            ax.set_xlabel("Estado del Estudiante")
            st.pyplot(fig)
            
        with gcol2:
            st.write("#### Factores de Desercion Academica")
            fig, ax = plt.subplots(figsize=(6, 4))
            # Relacion entre matricula al dia y desercion
            tabla_cruzada = pd.crosstab(datos_crudos["Tuition fees up to date"], datos_crudos["Target"], normalize='index') * 100
            tabla_cruzada = tabla_cruzada.rename(
                index={0: "Con Deudas", 1: "Matricula al Dia"},
                columns={"Dropout": "Desercion", "Enrolled": "Matriculado", "Graduate": "Graduado"}
            )
            tabla_cruzada.plot(kind="bar", stacked=True, color=["#ef4444", "#eab308", "#22c55e"], ax=ax)
            ax.set_ylabel("Porcentaje (%)")
            ax.set_xlabel("Situacion de Matricula")
            plt.xticks(rotation=0)
            st.pyplot(fig)
            
        st.write("---")
        
        # Perfiles Socioeconomicos (Clustering)
        st.write("#### Segmentacion Socioeconomica de Vulnerabilidad (Clustering K-Means)")
        st.write("Los estudiantes se agrupan en 3 perfiles segun variables socioeconomicas (edad, beca, deudas, ocupaciones de padres) para detectar grupos de riesgo antes del inicio de clases:")
        
        resumen_perfiles = agrupador.obtener_descripcion_perfiles(datos_crudos)
        # Renombrar columnas para el usuario
        resumen_perfiles_interfaz = resumen_perfiles.rename(columns={
            "Perfil": "ID Perfil",
            "Cantidad_Alumnos": "Numero de Alumnos",
            "Edad_Promedio": "Edad Promedio al Ingreso",
            "Porcentaje_Becarios_Pct": "Becarios (%)",
            "Porcentaje_Deudores_Pct": "Deudores (%)",
            "Matricula_Al_Dia_Pct": "Matricula al Dia (%)"
        })
        st.dataframe(resumen_perfiles_interfaz, use_container_width=True)

    # --- PESTAÑA 2: CALCULADORA DE RIESGO INDIVIDUAL ---
    with pestana2:
        st.write("### Calculadora de Riesgo de Desercion Individual")
        st.write("Complete los datos del estudiante para evaluar el riesgo de desercion y obtener las explicaciones de sus factores de riesgo.")
        
        # Dividir formulario en tres secciones
        fcol1, fcol2, fcol3 = st.columns(3)
        
        with fcol1:
            st.write("##### Datos Personales y Demograficos")
            edad = st.number_input("Edad al inscribirse", min_value=15, max_value=80, value=20)
            genero = st.selectbox("Genero", ["Femenino", "Masculino"])
            genero_cod = 1 if genero == "Masculino" else 0
            desplazado = st.selectbox("Desplazado (Vive lejos de su hogar)", ["No", "Si"])
            desplazado_cod = 1 if desplazado == "Si" else 0
            estado_civil = st.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado / Separado / Otro"])
            estado_civil_cod = 1 if estado_civil == "Soltero" else (2 if estado_civil == "Casado" else 4)
            nacionalidad_cod = st.number_input("Nacionalidad (Codigo)", min_value=1, max_value=50, value=1)
            
        with fcol2:
            st.write("##### Factores Socioeconomicos")
            becario = st.selectbox("¿Cuenta con Beca?", ["No", "Si"])
            becario_cod = 1 if becario == "Si" else 0
            deudor = st.selectbox("¿Tiene deudas de Matricula?", ["No", "Si"])
            deudor_cod = 1 if deudor == "Si" else 0
            matricula_al_dia = st.selectbox("¿Matricula al dia?", ["Si", "No"])
            matricula_al_dia_cod = 1 if matricula_al_dia == "Si" else 0
            necesidades_especiales = st.selectbox("Necesidades educativas especiales", ["No", "Si"])
            necesidades_especiales_cod = 1 if necesidades_especiales == "Si" else 0
            nota_admision = st.number_input("Nota de Admision (95 - 200)", min_value=90.0, max_value=200.0, value=120.0)

        with fcol3:
            st.write("##### Desempeño Academico")
            aprobadas_1 = st.number_input("U. Curriculares Aprobadas 1er Semestre", min_value=0, max_value=30, value=6)
            nota_1 = st.number_input("Nota Promedio 1er Semestre (0 - 20)", min_value=0.0, max_value=20.0, value=12.5)
            matriculadas_1 = st.number_input("U. Curriculares Matriculadas 1er Semestre", min_value=0, max_value=30, value=6)
            evaluadas_1 = st.number_input("U. Curriculares Evaluadas 1er Semestre", min_value=0, max_value=30, value=6)
            
            aprobadas_2 = st.number_input("U. Curriculares Aprobadas 2do Semestre", min_value=0, max_value=30, value=5)
            nota_2 = st.number_input("Nota Promedio 2do Semestre (0 - 20)", min_value=0.0, max_value=20.0, value=11.8)
            matriculadas_2 = st.number_input("U. Curriculares Matriculadas 2do Semestre", min_value=0, max_value=30, value=6)
            evaluadas_2 = st.number_input("U. Curriculares Evaluadas 2do Semestre", min_value=0, max_value=30, value=6)
            
        # Boton de calculo
        if st.button("Calcular Riesgo del Estudiante"):
            # Construir DataFrame de entrada
            # Llenar las columnas restantes con valores por defecto promedio
            datos_estudiante = {col: 0 for col in procesador.columnas_caracteristicas}
            
            # Valores ingresados en el formulario y valores por defecto
            valores_formulario = {
                "Age at enrollment": edad,
                "Gender": genero_cod,
                "Displaced": desplazado_cod,
                "Marital status": estado_civil_cod,
                "Nationality": nacionalidad_cod,
                "Scholarship holder": becario_cod,
                "Debtor": deudor_cod,
                "Tuition fees up to date": matricula_al_dia_cod,
                "Educational special needs": necesidades_especiales_cod,
                "Admission grade": nota_admision,
                "Curricular units 1st sem (approved)": aprobadas_1,
                "Curricular units 1st sem (grade)": nota_1,
                "Curricular units 1st sem (enrolled)": matriculadas_1,
                "Curricular units 1st sem (evaluations)": evaluadas_1,
                "Curricular units 2nd sem (approved)": aprobadas_2,
                "Curricular units 2nd sem (grade)": nota_2,
                "Curricular units 2nd sem (enrolled)": matriculadas_2,
                "Curricular units 2nd sem (evaluations)": evaluadas_2,
                "Unemployment rate": 11.0,
                "Inflation rate": 1.4,
                "GDP": 0.5,
                "Mother's qualification": 1,
                "Father's qualification": 1,
                "Mother's occupation": 1,
                "Father's occupation": 1,
                "Application mode": 1,
                "Application order": 1,
                "Course": 1,
                "Daytime/evening attendance": 1
            }
            
            # Asignar los valores del formulario de forma segura solo si la columna existe en el dataset
            for clave, valor in valores_formulario.items():
                if clave in datos_estudiante:
                    datos_estudiante[clave] = valor
            
            df_entrada = pd.DataFrame([datos_estudiante])
            
            # Normalizar
            df_entrada_normalizado = procesador.normalizar_instancia(df_entrada)
            
            # Predecir
            prediccion_numerica = clasificador.predecir(df_entrada_normalizado)[0]
            probabilidades = clasificador.predecir_probabilidad(df_entrada_normalizado)[0]
            
            # La probabilidad de desercion es el indice 0 (clase 'Dropout')
            probabilidad_desercion = probabilidades[0]
            score_riesgo_pct = probabilidad_desercion * 100
            
            # Determinar clasificacion de riesgo
            if score_riesgo_pct >= 70:
                categoria_riesgo = "ALTO"
                clase_css = "riesgo-alto"
            elif score_riesgo_pct >= 35:
                categoria_riesgo = "MEDIO"
                clase_css = "riesgo-medio"
            else:
                categoria_riesgo = "BAJO"
                clase_css = "riesgo-bajo"
                
            estado_predicho = MAPEO_INVERSO[prediccion_numerica]
            
            # Mostrar Resultados
            st.write("---")
            st.write("### Resultados del Analisis")
            
            rcol1, rcol2 = st.columns(2)
            with rcol1:
                st.markdown(
                    f"""
                    <div style="background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #334155;">
                        <h4 style="margin-top:0; color:#94a3b8;">Score de Riesgo</h4>
                        <p style="font-size: 42px; font-weight: bold; margin:0;" class="{clase_css}">{score_riesgo_pct:.1f}%</p>
                        <p style="font-size: 18px; margin: 10px 0 0 0; color:#f8fafc;">Nivel de Riesgo: <span class="{clase_css}" style="font-weight:bold;">{categoria_riesgo}</span></p>
                        <p style="font-size: 16px; margin: 5px 0 0 0; color:#94a3b8;">Estado Predicho: <b>{estado_predicho}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Asignar grupo socioeconomico
                grupo_perfil = agrupador.asignar_perfil(df_entrada)[0]
                st.info(f"El alumno pertenece al **Perfil Socioeconomico {grupo_perfil}**.")
                
            with rcol2:
                st.write("##### Factores Explicativos de Riesgo (SHAP)")
                try:
                    # Explicar la instancia
                    valores_shap = explicador.explicar_instancia(df_entrada_normalizado)
                    
                    # Generar df para graficar
                    valores_df = pd.DataFrame({
                        "Caracteristica": df_entrada.columns,
                        "Valor_SHAP": valores_shap.values if hasattr(valores_shap, 'values') else valores_shap
                    })
                    
                    # Traducir nombres y ordenar
                    valores_df["Caracteristica_Es"] = valores_df["Caracteristica"].map(MAPEO_COLUMNAS_ESPANOL).fillna(valores_df["Caracteristica"])
                    valores_df = valores_df.sort_values(by="Valor_SHAP", key=abs, ascending=False).head(8)
                    
                    # Graficar
                    fig, ax = plt.subplots(figsize=(6, 4))
                    # Rojo para lo que aumenta el riesgo (positivo), Azul para lo que disminuye (negativo)
                    colores_barras = ["#ef4444" if val >= 0 else "#3b82f6" for val in valores_df["Valor_SHAP"]]
                    
                    sns.barplot(
                        x="Valor_SHAP", 
                        y="Caracteristica_Es", 
                        data=valores_df, 
                        palette=colores_barras, 
                        ax=ax
                    )
                    ax.set_xlabel("Impacto en la probabilidad de desercion")
                    ax.set_ylabel("")
                    ax.axvline(x=0, color="gray", linestyle="--", linewidth=0.8)
                    
                    # Añadir leyenda explicativa
                    st.pyplot(fig)
                    st.caption("Las barras rojas indican factores que aumentan el riesgo de desercion; las barras azules indican factores que lo disminuyen.")
                except Exception as e_shap:
                    st.warning(f"No se pudo generar la explicacion SHAP detallada: {str(e_shap)}")

    # --- PESTAÑA 3: PREDICCIÓN MASIVA ---
    with pestana3:
        st.write("### Evaluacion Masiva de Alumnos")
        st.write("Cargue un archivo CSV con el mismo formato que el dataset para obtener predicciones y scores de riesgo por lote.")
        
        archivo_cargado = st.file_uploader("Cargar Archivo CSV de Alumnos", type=["csv"])
        
        if archivo_cargado is not None:
            try:
                # Cargar datos subidos
                datos_lote = pd.read_csv(archivo_cargado, sep=';')
                if len(datos_lote.columns) <= 1:
                    datos_lote = pd.read_csv(archivo_cargado, sep=',')
                    
                st.write(f"Cargados exitosamente {len(datos_lote)} registros.")
                
                # Validar columnas
                columnas_requeridas = [col for col in procesador.columnas_caracteristicas]
                columnas_faltantes = [col for col in columnas_requeridas if col not in datos_lote.columns]
                
                if columnas_faltantes:
                    st.error(f"El archivo cargado no contiene las columnas requeridas: {columnas_faltantes}")
                else:
                    # Preparar y predecir
                    datos_lote_filtrados = datos_lote[columnas_requeridas]
                    datos_lote_normalizados = procesador.normalizar_instancia(datos_lote_filtrados)
                    
                    predicciones_lote = clasificador.predecir(datos_lote_normalizados)
                    probabilidades_lote = clasificador.predecir_probabilidad(datos_lote_normalizados)
                    
                    # Construir reporte final
                    reporte_df = datos_lote.copy()
                    reporte_df["Prediccion"] = [MAPEO_INVERSO[p] for p in predicciones_lote]
                    reporte_df["Score_Riesgo_Desercion_Pct"] = np.round(probabilidades_lote[:, 0] * 100, 1)
                    
                    # Asignar niveles de riesgo
                    niveles = []
                    for score in reporte_df["Score_Riesgo_Desercion_Pct"]:
                        if score >= 70:
                            niveles.append("ALTO")
                        elif score >= 35:
                            niveles.append("MEDIO")
                        else:
                            niveles.append("BAJO")
                    reporte_df["Nivel_Riesgo"] = niveles
                    
                    # Asignar clúster
                    reporte_df["Perfil_Socioeconomico"] = agrupador.asignar_perfil(datos_lote_filtrados)
                    
                    # Ordenar por nivel de riesgo prioritario
                    reporte_df = reporte_df.sort_values(by="Score_Riesgo_Desercion_Pct", ascending=False)
                    
                    # Mostrar tabla resumida
                    columnas_resumen_salida = ["Age at enrollment", "Gender", "Scholarship holder", "Debtor", "Tuition fees up to date", "Prediccion", "Score_Riesgo_Desercion_Pct", "Nivel_Riesgo", "Perfil_Socioeconomico"]
                    columnas_resumen_disponibles = [col for col in columnas_resumen_salida if col in reporte_df.columns]
                    
                    st.write("##### Alumnos con Mayor Riesgo Detectado:")
                    st.dataframe(reporte_df[columnas_resumen_disponibles].head(15), use_container_width=True)
                    
                    # Ofrecer boton de descarga del reporte completo
                    csv_descargable = reporte_df.to_csv(sep=';', index=False).encode('utf-8')
                    st.download_button(
                        label="Descargar Reporte Completo de Riesgos (CSV)",
                        data=csv_descargable,
                        file_name="reporte_riesgo_estudiantes.csv",
                        mime="text/csv"
                    )
            except Exception as error_lote:
                st.error(f"Error procesando el lote de datos: {str(error_lote)}")

if __name__ == "__main__":
    main()
