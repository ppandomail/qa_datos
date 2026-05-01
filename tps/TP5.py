#!/usr/bin/env python
# coding: utf-8

# # Métricas e Indicadores de Calidad - Dashboard Ejecutivo
# ---

# ## Consigna

# Elegir una industria (banco, salud, retail, universidad, gobierno) y responder:
# 1. ¿Qué datos son críticos?
# 2. ¿Qué problemas de calidad pueden aparecer?
# 3. Diseñar 5 KPIs de calidad.
# 4. Bocetar un dashboard ejecutivo.

# ## Dataset

# [Dataset: Estudiantes y egresados del nivel superior clasificados por áreas de la OCDE](https://www.argentina.gob.ar/ciencia/indicadorescti/datasets/dataset-estudiantes-y-egresados-del-nivel-superior-clasificados-por)

# ### 1. Datos críticos del dataset

# * Cantidad de estudiantes y egresados por año.
# * Área OCDE (clasificación temática).
# * Tipo de universidad (pública/privada).
# * Nivel educativo (pregrado, grado, posgrado).
# * Modalidad (presencial/virtual).
# * Región geográfica (si está disponible).

# ### 2. Problemas de calidad posibles 

# * **Duplicados**: registros repetidos de estudiantes o egresados.
# * **Inconsistencias**: valores que no coinciden (ej. egresados > estudiantes).
# * **Datos faltantes**: ausencia de área OCDE, modalidad o tipo de universidad.
# * **Codificación heterogénea**: nombres distintos para la misma categoría (ej. “virtual” vs. “a distancia”).
# * **Errores temporales**: años fuera de rango o mal registrados.

# ### 3. KPIs de calidad

# * **Tasa de completitud**: % de registros con todos los campos críticos completos.
# * **Índice de duplicación**: proporción de registros duplicados sobre el total.
# * **Consistencia matrícula-egreso**: % de casos donde egresados ≤ estudiantes.
# * **Uniformidad de codificación**: % de categorías estandarizadas en variables clave.
# * **Disponibilidad temporal**: % de años con datos completos en todas las dimensiones.

# ### 4. Boceto de un Dashboard Ejecutivo

# ![boceto.png](attachment:9aa3e90b-45e6-4938-b1cf-3ee844b4f487.png)

# El tablero incluye:
# * **KPIs globales**: tasa de completitud y duplicación.
# * **Serie temporal**: evolución de estudiantes vs. egresados.
# * **Distribución**: tipo de universidad y modalidad.
# * **Comparación por área OCDE**: barras estudiantes/egresados.
# * **Alertas de calidad**: semáforo con problemas detectados.
# 
# Este diseño sintetiza la información crítica y permite a directivos identificar rápidamente tendencias y riesgos.

# ### 5. Pipeline

# In[3]:


import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st


# #### a. Configuración inicial

# In[4]:


st.set_page_config(page_title="Dashboard Educación Superior", layout="wide")


# #### b. Carga de dataset

# In[5]:


df = pd.read_csv('educ_superior.csv')


# #### c. Identificación de datos críticos

# In[6]:


columnas_clave = [
    'ANIO', 'TIPO_UNIV', 'NIVEL_ACADEM', 'OF_ACADEM',
    'DISCIP_OCDE', 'DISCIP_ESPECIF', 'TIPO_ALUMNO', 'U_MED', 'VALOR'
]
df = df[columnas_clave]


# #### d. Filtros dinámicos

# In[8]:


st.sidebar.header('🔎 Filtros')
anios = st.sidebar.multiselect("Seleccionar Año(s)", sorted(df['ANIO'].unique()), default=sorted(df['ANIO'].unique()))
universidades = st.sidebar.multiselect("Tipo de Universidad", df['TIPO_UNIV'].unique(), default=df['TIPO_UNIV'].unique())
areas = st.sidebar.multiselect("Área OCDE", df['DISCIP_OCDE'].unique(), default=df['DISCIP_OCDE'].unique())

# Aplicar filtros
df_filtrado = df[
    (df['ANIO'].isin(anios)) &
    (df['TIPO_UNIV'].isin(universidades)) &
    (df['DISCIP_OCDE'].isin(areas))
]


# #### e. Detección de problemas de calidad

# In[9]:


duplicados = df_filtrado.duplicated().sum()


# In[10]:


faltantes = df_filtrado.isnull().sum().sum()


# In[11]:


inconsistencias = df_filtrado.query("TIPO_ALUMNO == 'Egresado' and VALOR < 0").shape[0]


# #### f. Cálculo de KPIs de calidad

# In[12]:


total_registros = len(df_filtrado)
kpi_completitud = round((1 - faltantes / (total_registros * len(df_filtrado.columns))) * 100, 2)
kpi_duplicacion = round((duplicados / total_registros) * 100, 2)
kpi_consistencia = round((1 - inconsistencias / total_registros) * 100, 2)

kpi_resumen = {
    'Tasa de completitud': kpi_completitud,
    'Índice de duplicación': kpi_duplicacion,
    'Consistencia matrícula-egreso': kpi_consistencia
}

kpi_df = pd.DataFrame(list(kpi_resumen.items()), columns=["KPI", "Valor (%)"])
st.title("📊 Análisis de Calidad en Educación Superior")
kpi_df


# #### g. Visualizaciones

# In[13]:


# Serie temporal estudiantes vs egresados
serie = df_filtrado.groupby(['ANIO', 'TIPO_ALUMNO'])['VALOR'].sum().reset_index()
fig1 = px.line(serie, x='ANIO', y='VALOR', color='TIPO_ALUMNO',
               title='Evolución de Estudiantes y Egresados')
st.plotly_chart(fig1, use_container_width=True)


# In[14]:


# Barras comparativas por área OCDE
area = df_filtrado.groupby(['DISCIP_OCDE', 'TIPO_ALUMNO'])['VALOR'].sum().reset_index()
fig2 = px.bar(area, x='DISCIP_OCDE', y='VALOR', color='TIPO_ALUMNO',
              barmode='group', title='Estudiantes y Egresados por Área OCDE')
st.plotly_chart(fig2, use_container_width=True)


# In[15]:


# Heatmap modalidad vs nivel educativo
pivot = df_filtrado.pivot_table(values='VALOR', index='NIVEL_ACADEM', columns='OF_ACADEM', aggfunc='sum')
fig, ax = plt.subplots(figsize=(8, 4))
sns.heatmap(pivot, cmap='Blues', ax=ax)
st.pyplot(fig)


# In[17]:


# Semáforo de calidad
st.subheader('🚦 Alertas de Calidad')
alertas = {
    "Completitud": "🟢" if kpi_completitud > 90 else "🟠" if kpi_completitud > 70 else "🔴",
    "Duplicación": "🟢" if kpi_duplicacion < 5 else "🟠" if kpi_duplicacion < 10 else "🔴",
    "Consistencia": "🟢" if kpi_consistencia > 95 else "🟠" if kpi_consistencia > 80 else "🔴"
}
for k, v in alertas.items():
    st.write(f"{v} {k}")


# #### h. Footer

# In[18]:


st.markdown("---")
st.caption("Fuente: Dataset Educación Superior Argentina - OCDE. Desarrollado por Pablo Pandolfo.")


# #### i. Ejecución

# 1. File > Export Notebook As > Executable Script
# 2. streamlit run TP5.py
