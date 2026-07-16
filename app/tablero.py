import sys
import os
# Agregar el directorio raiz del proyecto al path de Python para permitir importaciones de src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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

# Estilos CSS personalizados para apariencia premium (Glassmorphism y sombras neón)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-weight: 700;
        background: linear-gradient(90deg, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.2);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px 0 rgba(96, 165, 250, 0.15);
        border: 1px solid rgba(96, 165, 250, 0.25);
    }
    .metric-card h3 {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }
    .metric-card p {
        color: #f8fafc;
        font-size: 32px;
        font-weight: 700;
        margin: 8px 0 0 0;
    }
    
    /* Variantes de color de riesgo */
    .riesgo-alto {
        color: #f87171 !important;
        text-shadow: 0 0 10px rgba(248, 113, 113, 0.2);
    }
    .riesgo-medio {
        color: #fbbf24 !important;
        text-shadow: 0 0 10px rgba(251, 191, 36, 0.2);
    }
    .riesgo-bajo {
        color: #34d399 !important;
        text-shadow: 0 0 10px rgba(52, 211, 153, 0.2);
    }
    
    .panel-resultado {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
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
    st.markdown('<h1 class="main-title">🎓 Sistema de Analisis de Riesgo y Rendimiento Estudiantil</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8; font-size:16px; margin-top:-10px;">Herramienta inteligente de gestion academica y prevencion de la desercion</p>', unsafe_allow_html=True)
    
    # Barra lateral de configuración
    st.sidebar.markdown("### ⚙️ Configuracion de Modelos")
    
    ruta_datos = "datos/datos_estudiantes.csv"
    if not os.path.exists(ruta_datos):
        st.sidebar.error("Archivo de datos no encontrado. Ejecute descargar_datos.py primero.")
        st.stop()
        
    tipo_modelo = st.sidebar.selectbox(
        "Seleccione el Algoritmo Predictivo",
        ["bosque_aleatorio", "regresion_logistica", "xgboost"],
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    # Cargar y procesar
    try:
        procesador, clasificador, agrupador, explicador = inicializar_sistema_completo(ruta_datos, tipo_modelo)
    except Exception as e:
        st.error(f"Error al inicializar el sistema: {str(e)}")
        st.stop()
        
    # Pestañas principales
    pestana1, pestana2, pestana3, pestana4 = st.tabs([
        "📊 Estadisticas Institucionales",
        "🧮 Calculadora de Riesgo Individual",
        "📁 Prediccion Masiva (CSV)",
        "🧪 Validacion del Modelo"
    ])
    
    # --- PESTAÑA 1: ESTADÍSTICAS INSTITUCIONALES ---
    with pestana1:
        st.markdown("### 📊 Vista General de la Institucion")
        
        datos_crudos = procesador.datos
        total_alumnos = len(datos_crudos)
        tasa_desercion = (datos_crudos["Target"] == "Dropout").mean() * 100
        tasa_graduados = (datos_crudos["Target"] == "Graduate").mean() * 100
        
        # Tarjetas de resumen premium
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'''
                <div class="metric-card">
                    <h3>Total Alumnos Analizados</h3>
                    <p style="color: #60a5fa;">{total_alumnos:,}</p>
                </div>
            ''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'''
                <div class="metric-card">
                    <h3>Tasa de Desercion Global</h3>
                    <p class="riesgo-alto">{tasa_desercion:.1f}%</p>
                </div>
            ''', unsafe_allow_html=True)
        with col3:
            st.markdown(f'''
                <div class="metric-card">
                    <h3>Tasa de Graduacion Global</h3>
                    <p class="riesgo-bajo">{tasa_graduados:.1f}%</p>
                </div>
            ''', unsafe_allow_html=True)
            
        st.markdown("---")
        
        gcol1, gcol2 = st.columns(2)
        
        with gcol1:
            st.markdown("#### Distribucion de Alumnos por Estado Final")
            conteo_estados = datos_crudos["Target"].value_counts()
            conteo_estados = conteo_estados.rename(index={"Dropout": "Desercion", "Enrolled": "Matriculado", "Graduate": "Graduado"})
            
            # Gráfico de Torta (Donut Chart) interactivo con Plotly
            fig_pie = px.pie(
                names=conteo_estados.index,
                values=conteo_estados.values,
                hole=0.4,
                color=conteo_estados.index,
                color_discrete_map={"Desercion": "#f87171", "Matriculado": "#3b82f6", "Graduado": "#34d399"}
            )
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with gcol2:
            st.markdown("#### Factores de Desercion según Pago de Matricula")
            tabla_cruzada = pd.crosstab(datos_crudos["Tuition fees up to date"], datos_crudos["Target"], normalize='index') * 100
            tabla_cruzada = tabla_cruzada.rename(
                index={0: "Con Deudas de Matricula", 1: "Matricula al Dia"},
                columns={"Dropout": "Desercion", "Enrolled": "Matriculado", "Graduate": "Graduado"}
            )
            
            # Gráfico de barras apiladas interactivo de Plotly
            fig_bar = px.bar(
                tabla_cruzada,
                x=tabla_cruzada.index,
                y=["Desercion", "Matriculado", "Graduado"],
                color_discrete_map={"Desercion": "#f87171", "Matriculado": "#fbbf24", "Graduado": "#34d399"},
                labels={"value": "Porcentaje (%)", "index": "Estado de Matricula"}
            )
            fig_bar.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.markdown("---")
        
        # Perfiles Socioeconomicos (Clustering)
        st.markdown("#### 👥 Segmentacion Socioeconomica de Vulnerabilidad (Clustering K-Means)")
        st.markdown("El sistema agrupa automaticamente a los estudiantes en 3 perfiles socioeconomicos al momento del ingreso para poder ayudarlos antes de que iniciien las clases:")
        
        resumen_perfiles = agrupador.obtener_descripcion_perfiles(datos_crudos)
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
        st.markdown("### 🧮 Calculadora de Riesgo de Desercion Individual")
        st.markdown("Complete el formulario para evaluar la probabilidad de riesgo de un estudiante en tiempo real.")
        
        # Secciones visuales bien delimitadas con expanders e iconos
        with st.container():
            st.markdown("#### 📝 Datos del Estudiante")
            fcol1, fcol2, fcol3 = st.columns(3)
            
            with fcol1:
                st.markdown("**🧑‍💼 Demografia y Situacion Personal**")
                edad = st.number_input("Edad al inscribirse", min_value=15, max_value=80, value=20)
                genero = st.selectbox("Genero", ["Femenino", "Masculino"])
                genero_cod = 1 if genero == "Masculino" else 0
                desplazado = st.selectbox("¿Vive lejos de su hogar? (Desplazado)", ["No", "Si"])
                desplazado_cod = 1 if desplazado == "Si" else 0
                estado_civil = st.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado / Separado / Otro"])
                estado_civil_cod = 1 if estado_civil == "Soltero" else (2 if estado_civil == "Casado" else 4)
                nacionalidad_cod = st.number_input("Nacionalidad (Codigo)", min_value=1, max_value=50, value=1)
                
            with fcol2:
                st.markdown("**💰 Situacion Financiera**")
                becario = st.selectbox("¿Cuenta con Beca?", ["No", "Si"])
                becario_cod = 1 if becario == "Si" else 0
                deudor = st.selectbox("¿Tiene deudas de Matricula?", ["No", "Si"])
                deudor_cod = 1 if deudor == "Si" else 0
                matricula_al_dia = st.selectbox("¿Esta al dia en los pagos de matricula?", ["Si", "No"])
                matricula_al_dia_cod = 1 if matricula_al_dia == "Si" else 0
                necesidades_especiales = st.selectbox("Necesidades educativas especiales", ["No", "Si"])
                necesidades_especiales_cod = 1 if necesidades_especiales == "Si" else 0
                nota_admision = st.number_input("Nota de Admision general", min_value=90.0, max_value=200.0, value=120.0)
    
            with fcol3:
                st.markdown("**📚 Desempeño Academico**")
                aprobadas_1 = st.number_input("Materias Aprobadas 1er Semestre", min_value=0, max_value=30, value=6)
                nota_1 = st.number_input("Nota Promedio 1er Semestre (0 - 20)", min_value=0.0, max_value=20.0, value=12.5)
                matriculadas_1 = st.number_input("Materias Matriculadas 1er Semestre", min_value=0, max_value=30, value=6)
                evaluadas_1 = st.number_input("Materias Evaluadas 1er Semestre", min_value=0, max_value=30, value=6)
                
                aprobadas_2 = st.number_input("Materias Aprobadas 2do Semestre", min_value=0, max_value=30, value=5)
                nota_2 = st.number_input("Nota Promedio 2do Semestre (0 - 20)", min_value=0.0, max_value=20.0, value=11.8)
                matriculadas_2 = st.number_input("Materias Matriculadas 2do Semestre", min_value=0, max_value=30, value=6)
                evaluadas_2 = st.number_input("Materias Evaluadas 2do Semestre", min_value=0, max_value=30, value=6)
                
        # Boton de calculo
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔮 Evaluar Riesgo del Estudiante", type="primary", use_container_width=True):
            datos_estudiante = {col: 0 for col in procesador.columnas_caracteristicas}
            
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
            
            for clave, valor in valores_formulario.items():
                if clave in datos_estudiante:
                    datos_estudiante[clave] = valor
            
            df_entrada = pd.DataFrame([datos_estudiante])
            df_entrada_normalizado = procesador.normalizar_instancia(df_entrada)
            
            prediccion_numerica = clasificador.predecir(df_entrada_normalizado)[0]
            probabilidades = clasificador.predecir_probabilidad(df_entrada_normalizado)[0]
            
            probabilidad_desercion = probabilidades[0]
            score_riesgo_pct = probabilidad_desercion * 100
            
            if score_riesgo_pct >= 70:
                categoria_riesgo = "ALTO RIESGO"
                clase_css = "riesgo-alto"
                color_color = "#f87171"
            elif score_riesgo_pct >= 35:
                categoria_riesgo = "RIESGO MEDIO"
                clase_css = "riesgo-medio"
                color_color = "#fbbf24"
            else:
                categoria_riesgo = "RIESGO BAJO"
                clase_css = "riesgo-bajo"
                color_color = "#34d399"
                
            estado_predicho = MAPEO_INVERSO[prediccion_numerica]
            
            st.markdown("---")
            st.markdown("### 🔍 Resultados del Analisis de Riesgo")
            
            rcol1, rcol2 = st.columns([1, 1.2])
            
            with rcol1:
                # Panel Glassmorphism para los resultados de texto
                st.markdown(
                    f"""
                    <div class="panel-resultado">
                        <h4 style="margin-top:0; color:#94a3b8; font-size: 15px; letter-spacing:0.05em; text-transform:uppercase;">Resultado del Analisis</h4>
                        <p style="font-size: 48px; font-weight: 700; margin:5px 0;" class="{clase_css}">{score_riesgo_pct:.1f}%</p>
                        <p style="font-size: 20px; margin: 10px 0 0 0; color:#f8fafc;">Rango: <span class="{clase_css}" style="font-weight:bold;">{categoria_riesgo}</span></p>
                        <p style="font-size: 16px; margin: 5px 0 0 0; color:#94a3b8;">Estado del estudiante predicho: <b>{estado_predicho}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                grupo_perfil = agrupador.asignar_perfil(df_entrada)[0]
                st.markdown(f"<div style='margin-top:15px; padding:12px; border-radius:10px; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); color:#93c5fd;'>ℹ️ El alumno pertenece al <b>Perfil Socioeconomico {grupo_perfil}</b> (K-Means).</div>", unsafe_allow_html=True)
                
            with rcol2:
                # Mostrar Velocímetro (Gauge Chart) en Plotly
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score_riesgo_pct,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Indicador de Desercion (%)", 'font': {'size': 18, 'color': '#f8fafc'}},
                    number={'suffix': "%", 'font': {'size': 32, 'color': color_color}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                        'bar': {'color': color_color},
                        'bgcolor': "rgba(30, 41, 59, 0.4)",
                        'borderwidth': 2,
                        'bordercolor': "rgba(255,255,255,0.1)",
                        'steps': [
                            {'range': [0, 35], 'color': 'rgba(52, 211, 153, 0.15)'},
                            {'range': [35, 70], 'color': 'rgba(251, 191, 36, 0.15)'},
                            {'range': [70, 100], 'color': 'rgba(248, 113, 113, 0.15)'}
                        ]
                    }
                ))
                fig_gauge.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=280,
                    margin=dict(t=50, b=10, l=30, r=30)
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
                
            st.markdown("---")
            st.markdown("#### 🔍 ¿Por que el alumno tiene esta prediccion? (Explicacion SHAP)")
            try:
                valores_shap = explicador.explicar_instancia(df_entrada_normalizado)
                
                valores_df = pd.DataFrame({
                    "Caracteristica": df_entrada.columns,
                    "Valor_SHAP": valores_shap.values if hasattr(valores_shap, 'values') else valores_shap
                })
                
                valores_df["Caracteristica_Es"] = valores_df["Caracteristica"].map(MAPEO_COLUMNAS_ESPANOL).fillna(valores_df["Caracteristica"])
                # Filtrar las 8 con mayor impacto absoluto
                valores_df = valores_df.sort_values(by="Valor_SHAP", key=abs, ascending=False).head(8)
                
                # Gráfico interactivo de barras de Plotly para SHAP
                valores_df["Tipo_Impacto"] = ["Aumenta el Riesgo 🔴" if val >= 0 else "Disminuye el Riesgo 🔵" for val in valores_df["Valor_SHAP"]]
                
                fig_shap = px.bar(
                    valores_df,
                    x="Valor_SHAP",
                    y="Caracteristica_Es",
                    orientation="h",
                    color="Tipo_Impacto",
                    color_discrete_map={"Aumenta el Riesgo 🔴": "#f87171", "Disminuye el Riesgo 🔵": "#60a5fa"},
                    labels={"Valor_SHAP": "Impacto en el riesgo", "Caracteristica_Es": "Variable del estudiante"}
                )
                fig_shap.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=10, b=10, l=10, r=10),
                    legend=dict(title=None, orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_shap, use_container_width=True)
                st.caption("Las barras rojas son los factores del estudiante que elevan su riesgo de desercion. Las barras azules son los factores protectores que le ayudan a continuar.")
            except Exception as e_shap:
                st.warning(f"No se pudo generar la explicacion SHAP detallada: {str(e_shap)}")

    # --- PESTAÑA 3: PREDICCIÓN MASIVA ---
    with pestana3:
        st.markdown("### 📁 Evaluacion Masiva de Alumnos (CSV)")
        st.markdown("Cargue la lista de sus alumnos en un archivo CSV para evaluarlos de forma masiva y ordenada de mayor a menor riesgo.")
        
        archivo_cargado = st.file_uploader("Cargar Archivo CSV de Alumnos", type=["csv"])
        
        if archivo_cargado is not None:
            try:
                datos_lote = pd.read_csv(archivo_cargado, sep=';')
                if len(datos_lote.columns) <= 1:
                    datos_lote = pd.read_csv(archivo_cargado, sep=',')
                    
                st.success(f"📂 Archivo cargado correctamente: {len(datos_lote)} estudiantes detectados.")
                
                # Validar columnas
                columnas_requeridas = [col for col in procesador.columnas_caracteristicas]
                columnas_faltantes = [col for col in columnas_requeridas if col not in datos_lote.columns]
                
                if columnas_faltantes:
                    st.error(f"El archivo cargado no contiene las columnas requeridas: {columnas_faltantes}")
                else:
                    datos_lote_filtrados = datos_lote[columnas_requeridas]
                    datos_lote_normalizados = procesador.normalizar_instancia(datos_lote_filtrados)
                    
                    predicciones_lote = clasificador.predecir(datos_lote_normalizados)
                    probabilidades_lote = clasificador.predecir_probabilidad(datos_lote_normalizados)
                    
                    reporte_df = datos_lote.copy()
                    reporte_df["Prediccion"] = [MAPEO_INVERSO[p] for p in predicciones_lote]
                    reporte_df["Score_Riesgo_Desercion_Pct"] = np.round(probabilidades_lote[:, 0] * 100, 1)
                    
                    niveles = []
                    for score in reporte_df["Score_Riesgo_Desercion_Pct"]:
                        if score >= 70:
                            niveles.append("ALTO")
                        elif score >= 35:
                            niveles.append("MEDIO")
                        else:
                            niveles.append("BAJO")
                    reporte_df["Nivel_Riesgo"] = niveles
                    reporte_df["Perfil_Socioeconomico"] = agrupador.asignar_perfil(datos_lote_filtrados)
                    reporte_df = reporte_df.sort_values(by="Score_Riesgo_Desercion_Pct", ascending=False)
                    
                    # --- RESUMEN DE RIESGO DEL LOTE CON COLORES ---
                    st.markdown("#### 📋 Resumen del Lote Evaluado")
                    
                    altos = (reporte_df["Nivel_Riesgo"] == "ALTO").sum()
                    medios = (reporte_df["Nivel_Riesgo"] == "MEDIO").sum()
                    bajos = (reporte_df["Nivel_Riesgo"] == "BAJO").sum()
                    
                    mcol1, mcol2, mcol3 = st.columns(3)
                    with mcol1:
                        st.markdown(f'''
                            <div class="metric-card">
                                <h3>🚨 Alumnos en Riesgo ALTO</h3>
                                <p class="riesgo-alto">{altos}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                    with mcol2:
                        st.markdown(f'''
                            <div class="metric-card">
                                <h3>⚠️ Alumnos en Riesgo MEDIO</h3>
                                <p class="riesgo-medio">{medios}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                    with mcol3:
                        st.markdown(f'''
                            <div class="metric-card">
                                <h3>🟢 Alumnos en Riesgo BAJO</h3>
                                <p class="riesgo-bajo">{bajos}</p>
                            </div>
                        ''', unsafe_allow_html=True)
                        
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Gráfica interactiva de la distribución del lote cargado
                    dist_col1, dist_col2 = st.columns([1, 1.2])
                    
                    with dist_col1:
                        st.markdown("##### Distribucion porcentual del riesgo")
                        fig_lote_pie = px.pie(
                            names=["Riesgo Alto 🔴", "Riesgo Medio 🟡", "Riesgo Bajo 🟢"],
                            values=[altos, medios, bajos],
                            color=["Riesgo Alto 🔴", "Riesgo Medio 🟡", "Riesgo Bajo 🟢"],
                            color_discrete_map={"Riesgo Alto 🔴": "#f87171", "Riesgo Medio 🟡": "#fbbf24", "Riesgo Bajo 🟢": "#34d399"},
                            hole=0.4
                        )
                        fig_lote_pie.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=10, b=10, l=10, r=10),
                            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
                        )
                        st.plotly_chart(fig_lote_pie, use_container_width=True)
                        
                    with dist_col2:
                        st.markdown("##### Distribucion por Perfil Socioeconomico (Clustering)")
                        perfiles_conteo = reporte_df["Perfil_Socioeconomico"].value_counts().sort_index()
                        perfiles_conteo.index = [f"Perfil {idx}" for idx in perfiles_conteo.index]
                        
                        fig_lote_bar = px.bar(
                            x=perfiles_conteo.index,
                            y=perfiles_conteo.values,
                            color=perfiles_conteo.index,
                            color_discrete_sequence=["#60a5fa", "#fbbf24", "#34d399"],
                            labels={"x": "Grupo Socioeconomico", "y": "Numero de Alumnos"}
                        )
                        fig_lote_bar.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=10, b=10, l=10, r=10),
                            showlegend=False
                        )
                        st.plotly_chart(fig_lote_bar, use_container_width=True)
                    
                    st.markdown("---")
                    st.markdown("##### 🔍 Nomina Detallada del Lote (Primeros 15 alumnos de mayor prioridad)")
                    columnas_resumen_salida = ["Age at enrollment", "Gender", "Scholarship holder", "Debtor", "Tuition fees up to date", "Prediccion", "Score_Riesgo_Desercion_Pct", "Nivel_Riesgo", "Perfil_Socioeconomico"]
                    columnas_resumen_disponibles = [col for col in columnas_resumen_salida if col in reporte_df.columns]
                    
                    st.dataframe(reporte_df[columnas_resumen_disponibles].head(15), use_container_width=True)
                    
                    csv_descargable = reporte_df.to_csv(sep=';', index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar Reporte Completo de Riesgos (CSV)",
                        data=csv_descargable,
                        file_name="reporte_riesgo_estudiantes.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            except Exception as error_lote:
                st.error(f"Error procesando el lote de datos: {str(error_lote)}")

    # --- PESTAÑA 4: VALIDACIÓN DEL MODELO ---
    with pestana4:
        st.markdown("### 🧪 Validacion Estadistica del Sistema")
        st.markdown("Esta seccion evalua la robustez del modelo predictivo y la calidad del agrupamiento socioeconomico.")
        
        vcol1, vcol2 = st.columns(2)
        
        # --- Cross-Validation K-Fold ---
        with vcol1:
            st.markdown("#### Validacion Cruzada Estratificada (K-Fold, k=5)")
            st.write("Mide la estabilidad del accuracy al evaluar el modelo en 5 partes diferentes de la base de datos.")
            if st.button("🚀 Ejecutar Validacion Cruzada", key="btn_cv", use_container_width=True):
                with st.spinner("Ejecutando validacion cruzada..."):
                    try:
                        X_completo = pd.concat([procesador.X_entrenamiento, procesador.X_prueba])
                        y_completo = pd.concat([procesador.y_entrenamiento, procesador.y_prueba])
                        resultado_cv = clasificador.validar_cruzado(X_completo, y_completo, n_splits=5)
                        
                        st.success(f"Accuracy medio: **{resultado_cv['precision_media']*100:.2f}%** ± {resultado_cv['desviacion_estandar']*100:.2f}%")
                        
                        scores_df = pd.DataFrame({
                            "Fold": [f"Fold {i+1}" for i in range(len(resultado_cv['scores_por_fold']))],
                            "Accuracy (%)": [round(s * 100, 2) for s in resultado_cv['scores_por_fold']]
                        })
                        
                        # Gráfico interactivo Plotly para Cross-Validation
                        fig_cv = px.bar(
                            scores_df,
                            x="Fold",
                            y="Accuracy (%)",
                            color="Accuracy (%)",
                            color_continuous_scale=[(0, "#3b82f6"), (1, "#22c55e")],
                            range_y=[50, 100]
                        )
                        fig_cv.add_hline(y=resultado_cv['precision_media']*100, line_dash="dash", line_color="#f87171", annotation_text=f"Media: {resultado_cv['precision_media']*100:.2f}%", annotation_position="bottom right")
                        fig_cv.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=20, b=10, l=10, r=10),
                            coloraxis_showscale=False
                        )
                        st.plotly_chart(fig_cv, use_container_width=True)
                    except Exception as e_cv:
                        st.error(f"Error en validacion cruzada: {str(e_cv)}")
        
        # --- Silhouette Score del Clustering ---
        with vcol2:
            st.markdown("#### Silhouette Score (Validacion del Numero de Grupos)")
            st.write("Mide que tan bien separados y definidos estan los 3 perfiles socioeconomicos de los alumnos.")
            if st.button("🚀 Calcular Silhouette por K", key="btn_sil", use_container_width=True):
                with st.spinner("Calculando indices de separacion..."):
                    try:
                        scores_sil = agrupador.calcular_silhouette_por_k(procesador.datos, rango_k=(2, 6))
                        sil_actual = agrupador.obtener_silhouette()
                        
                        st.success(f"Silhouette Score con K=3: **{sil_actual}** (valor recomendado)")
                        
                        sil_df = pd.DataFrame(list(scores_sil.items()), columns=["K Clusters", "Silhouette Score"])
                        sil_df["K Clusters"] = sil_df["K Clusters"].astype(str)
                        
                        # Gráfico interactivo Plotly para Silhouette
                        fig_sil = px.bar(
                            sil_df,
                            x="K Clusters",
                            y="Silhouette Score",
                            color="K Clusters",
                            color_discrete_map={"3": "#f87171", "2": "#3b82f6", "4": "#3b82f6", "5": "#3b82f6", "6": "#3b82f6"}
                        )
                        fig_sil.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=20, b=10, l=10, r=10),
                            showlegend=False
                        )
                        st.plotly_chart(fig_sil, use_container_width=True)
                    except Exception as e_sil:
                        st.error(f"Error al calcular Silhouette: {str(e_sil)}")
        
        st.markdown("---")
        
        # --- SHAP Importancia Global ---
        st.markdown("#### Importancia Global de Variables (SHAP)")
        st.write("Muestra que caracteristicas de los estudiantes influyen mas en la desercion a nivel de toda la universidad.")
        if st.button("🚀 Generar Importancia Global SHAP", key="btn_shap_global", use_container_width=True):
            with st.spinner("Generando importancia global..."):
                try:
                    df_importancia = explicador.calcular_importancia_global(procesador.X_entrenamiento, max_muestra=200)
                    df_importancia["Variable"] = df_importancia["Caracteristica"].map(MAPEO_COLUMNAS_ESPANOL).fillna(df_importancia["Caracteristica"])
                    top_15 = df_importancia.head(15)
                    
                    # Gráfico de barras horizontal interactivo de Plotly
                    fig_shap_glob = px.bar(
                        top_15,
                        x="Importancia_Media_SHAP",
                        y="Variable",
                        orientation="h",
                        color="Importancia_Media_SHAP",
                        color_continuous_scale=[(0, "#3b82f6"), (1, "#f87171")],
                        labels={"Importancia_Media_SHAP": "Importancia media (impacto promedio en la desercion)"}
                    )
                    fig_shap_glob.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=10, b=10, l=10, r=10),
                        coloraxis_showscale=False
                    )
                    st.plotly_chart(fig_shap_glob, use_container_width=True)
                    
                    st.dataframe(top_15[["Variable", "Importancia_Media_SHAP"]].rename(
                        columns={"Importancia_Media_SHAP": "Impacto Medio |SHAP|"}
                    ), use_container_width=True)
                except Exception as e_shap_g:
                    st.error(f"Error al generar importancia SHAP global: {str(e_shap_g)}")

if __name__ == "__main__":
    main()
