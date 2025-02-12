import pandas as pd
import numpy as np
import streamlit as st
from pymongo.mongo_client import MongoClient

import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

uri = "mongodb+srv://usr_python:pepinoni887@cluster0.brm9o.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["dbmongo_sesnsp"]  # Nombre de la BD

# **Recuperar la información**

@st.cache_data
def get_incidencia():
  collection = db["incidencia"]
  cursor = collection.find()
  df = pd.DataFrame(list(cursor))
  if "_id" in df.columns:
   df.drop(columns=["_id"], inplace=True)
  return df
df = get_incidencia()

# **Recuperar los catálogos**
@st.cache_data
def get_entidad():
  collection = db["cat_entidad"]
  cursor = collection.find()
  dfEnt = pd.DataFrame(list(cursor))
  if "_id" in dfEnt.columns:
    dfEnt.drop(columns=["_id"], inplace=True)
  return dfEnt
dfEnt = get_entidad()

@st.cache_data
def get_municipio():
  collection = db["cat_municipio"]
  cursor = collection.find()
  dfMun = pd.DataFrame(list(cursor))
  if "_id" in dfMun.columns:
    dfMun.drop(columns=["_id"], inplace=True)
  return dfMun
dfMun = get_municipio()

dfMun = pd.merge(dfMun, dfEnt, on='Id_Entidad', how='left')
dfMun['mun_compuesto'] = dfMun['Nom_Municipio'] + ', ' + dfMun['Abrev_Entidad']

@st.cache_data
def get_delito():
  collection = db["cat_delito"]
  cursor = collection.find()
  dfDel = pd.DataFrame(list(cursor))
  if "_id" in dfDel.columns:
     dfDel.drop(columns=["_id"], inplace=True)
  return dfDel
dfDel = get_delito()

@st.cache_data
def get_mes():
  collection = db["cat_mes"]
  cursor = collection.find()
  dfMes = pd.DataFrame(list(cursor))
  if "_id" in dfMes.columns:
    dfMes.drop(columns=["_id"], inplace=True)
  return dfMes
dfMes = get_mes ()

@st.cache_data
def get_cab_agrupador_delito():
  collection = db["cab_agrupador_delito"]
  cursor = collection.find()
  dfCabAgrp = pd.DataFrame(list(cursor))
  if "_id" in dfCabAgrp.columns:
     dfCabAgrp.drop(columns=["_id"], inplace=True)
  return dfCabAgrp
dfCabAgrp = get_cab_agrupador_delito()

@st.cache_data
def get_det_agrupador_delito():
  collection = db["det_agrupador_delito"]
  cursor = collection.find()
  dfDetAgrp = pd.DataFrame(list(cursor))
  if "_id" in dfDetAgrp.columns:
     dfDetAgrp.drop(columns=["_id"], inplace=True)
  return dfDetAgrp
dfDetAgrp = get_det_agrupador_delito()

@st.cache_data
def get_poblacion():
  collection = db["cat_poblacion"]
  cursor = collection.find()
  dfPob = pd.DataFrame(list(cursor))
  if "_id" in dfPob.columns:
     dfPob.drop(columns=["_id"], inplace=True)
  return dfPob
dfPob = get_poblacion()

client.close()


#Va la parte de Streamlit

# App Configuration
#st.set_page_config(page_title="App de Graficas del SESNSP", layout="wide")

#Título
st.title("Generación de gráficas delictivas")

#Función para obtener Aniomes estilo np.datetime64
def get_dt64(Aniomes) -> np.datetime64:
    year = Aniomes // 100
    mes = Aniomes % year
    dt = datetime.datetime(year, mes, 1)
    dt64 = np.datetime64(dt)
    return dt64

# Sidebar
st.sidebar.header("Ajustes")
nom_agrupador_selecc = st.sidebar.selectbox("Selecciona un delito:", dfCabAgrp['Nombre_Agrupador_Delito'])
IdAgrupDel= list (dfCabAgrp.loc[dfCabAgrp['Nombre_Agrupador_Delito'] == nom_agrupador_selecc, 'Id_Agrupador_Delito'])[0]

AnchoBar = st.sidebar.select_slider("Selecciona el ancho de barra:", options= np.arange (5,20,0.5), value =10.5)
AnchoLinea = st.sidebar.select_slider("Selecciona el ancho de línea:", options= np.arange (2.5,10,0.5), value =4)
tipo_linea = st.sidebar.selectbox("Selecciona tipo de línea:", ['-', '--', '-.', ':', 'None'])

#Cuerpo
nom_mun_selecc = st.selectbox("Selecciona un municipio:", dfMun['mun_compuesto'])
IdMun = list (dfMun.loc[dfMun['mun_compuesto'] == nom_mun_selecc, 'Id_Municipio'])[0]

list_aniomes = df['Aniomes'].unique()
list_aniomes.sort()
Aniomes_Ini, Aniomes_Fin = st.select_slider(
    "Selecciona los meses a considerar:",
    options = list_aniomes,
    value = (list_aniomes[-12], list_aniomes[-1]))


#IdMun= 32056
#Aniomes_Ini= 202206
#Aniomes_Fin= 202406
#IdAgrupDel= 'B03'
#AnchoBar= 10.5

years = mdates.YearLocator()
months = mdates.MonthLocator()
years_fmt = mdates.DateFormatter('%Y')
months_fmt = mdates.DateFormatter('%b')
fmt = mdates.DateFormatter('%Y-%m')


dftemp= df.loc[(df['Id_Municipio'] == IdMun) &
               (df['Aniomes'] >= Aniomes_Ini) &
               (df['Aniomes'] <= Aniomes_Fin) &
               (df['Id_Agrupador_Delito'] == IdAgrupDel) ,  ['Aniomes','Id_Agrupador_Delito','tasa','tasa_nal']]
dftemp['dt64']= dftemp['Aniomes'].apply (get_dt64)


fig, ax = plt.subplots(1, 1, figsize=(16.0, 10.0), layout='constrained')
fig.set_constrained_layout_pads(w_pad=2./12., h_pad=8./12., hspace=0., wspace=0.)

ax.bar ('dt64', 'tasa', data= dftemp, width= AnchoBar,  color='darkslategrey', label='tasa municipal')
ax.plot ('dt64', 'tasa_nal', data= dftemp, linewidth= AnchoLinea, linestyle= tipo_linea, color='salmon', label='tasa nacional')

ax.bar_label(ax.containers[0], label_type='edge', fontsize= 10, color='black')

#ax.xaxis.set_major_locator(years)
#ax.xaxis.set_major_locator(months)
#ax.xaxis.set_major_formatter(years_fmt)
ax.xaxis.set_major_formatter(fmt)

ax.xaxis.set_minor_locator(months)
#ax.xaxis.set_minor_formatter(months_fmt)

ax.set_xlabel('Periodo',fontsize= 14,color='black')
ax.set_ylabel('Tasa delictiva',fontsize= 14, color='black')

titulo_grafica= 'Tasa delictiva mensual de ' + nom_agrupador_selecc + ' \n' + nom_mun_selecc
ax.set_title(titulo_grafica,fontsize= 26,color='darkslategrey')

ax.grid(which='major', alpha=0.2)
fig.legend(loc='lower right', fontsize='10', shadow=True)

st.pyplot(fig)

#Columnas
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Variación del periodo", value="40%", delta="+5%", delta_color= "inverse")
with col2:
    st.metric(label="Variación últimos tres meses", value="12%", delta="-2%", delta_color= "inverse")


with st.expander("Ver tabla de datos"):    
    st.table(dftemp[['Aniomes','tasa','tasa_nal']])
