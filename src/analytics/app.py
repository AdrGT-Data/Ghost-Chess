import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import os
import chess
import chess.svg

"""
Este script crea una interfaz web interactiva usando Streamlit para visualizar la telemetría mecánica
"""

# Configuración de la página web
st.set_page_config(page_title="Ghost Chess | Telemetría", layout="wide")
st.title("Ghost Chess - Telemetría Mecánica")

@st.cache_data
def load_data():
    """Extrae y cachea los datos para que la web no se ralentice al recargar"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "ghost_chess_telemetry.db")
    conn = sqlite3.connect(db_path)
    
    df_turnos = pd.read_sql_query("SELECT * FROM TELEMETRIA_TURNOS", conn)
    df_partidas = pd.read_sql_query("SELECT * FROM PARTIDAS", conn)
    conn.close()
    
    return pd.merge(df_turnos, df_partidas, on="id_partida", how="left")

# 1. CARGA DE DATOS
df = load_data()

# --------------------2. METRICAS GLOBALES---------------------------
st.markdown("### Resumen Mecánico Global")
col1, col2, col3 = st.columns(3)

col1.metric("Partidas Simuladas", df['id_partida'].nunique())
col2.metric("Total Movimientos (Turnos)", len(df))
# Convertimos los milímetros a metros para que sea más legible
col3.metric("Desgaste de Correas (Metros)", round(df['distancia_mm'].sum() / 1000, 2))

st.divider()


#----------------------3. VISOR INTERACTIVO DE PARTIDAS--------------------------------
st.markdown("### Replay de Partidas")

# Memoria de sesión
if 'turno_actual' not in st.session_state:
    st.session_state.turno_actual = 1
if 'partida_activa' not in st.session_state:
    st.session_state.partida_activa = None 

# Interfaz: Selector de Partida en una columna, datos del turno en otra
col_control, col_visor = st.columns([1, 2])

with col_control:
    # Obtenemos la lista de todas las partidas jugadas
    lista_partidas = df['id_partida'].unique()
    
    # Selector desplegable
    partida_seleccionada = st.selectbox("Selecciona el ID de la Partida:", lista_partidas)

    # Seguro: Si el usuario elige otra partida, reseteamos el turno al inicio
    if partida_seleccionada != st.session_state.partida_activa:
        st.session_state.partida_activa = partida_seleccionada
        st.session_state.turno_actual = 1


    # Filtramos el DataFrame maestro para quedarnos solo con los turnos de ESA partida
    df_partida = df[df['id_partida'] == partida_seleccionada].sort_values('numero_turno')
    
    # Slider para navegar por los turnos
    max_turnos = int(df_partida['numero_turno'].max())

    # Sistema de Botones (Paso a Paso)
    col_btn_izq, col_btn_der = st.columns(2)
    
    with col_btn_izq:
        if st.button("⬅️ Anterior", use_container_width=True):
            if st.session_state.turno_actual > 1:
                st.session_state.turno_actual -= 1
                
    with col_btn_der:
        if st.button("Siguiente ➡️", use_container_width=True):
            if st.session_state.turno_actual < max_turnos:
                st.session_state.turno_actual += 1
                
    turno_seleccionado = st.slider("Desliza para avanzar el turno:", min_value=1, max_value=max_turnos, value=1)

# Extraemos la información del turno exacto que ha seleccionado el usuario
fila_turno = df_partida[df_partida['numero_turno'] == turno_seleccionado].iloc[0]

# Variables del turno
fen_actual = fila_turno['estado_fen']
movimiento_uci = fila_turno['movimiento_uci']
jugador = fila_turno['jugador']
tiempo_ia = fila_turno['tiempo_calculo_ms']

with col_control:
    # Mostramos los metadatos del turno debajo del slider
    st.info(f"**Turno {turno_seleccionado}**")
    st.write(f"**Jugador:** {jugador}")
    st.write(f"**Movimiento (UCI):** `{movimiento_uci}`")
    if "IA" in jugador:
        st.write(f"⏱️ **Latencia Cálculo:** `{tiempo_ia} ms`")

with col_visor:
    # 1. Cargamos el FEN en el motor lógico
    board = chess.Board(fen_actual)
    
    # 2. Resaltamos la última jugada (opcional pero muy útil visualmente)
    ultimo_mov = chess.Move.from_uci(movimiento_uci)
    
    # 3. Generamos el código SVG del tablero
    board_svg = chess.svg.board(board=board, lastmove=ultimo_mov, size=450)
    
    # 4. Lo inyectamos directamente en la web de Streamlit usando HTML
    st.components.v1.html(board_svg, height=500)

st.divider()


# -----------------4. MAPA DE CALOR MECÁNICO -----------------------
st.markdown("### Mapa de calor por casillas")

# Creamos una lista con la opción global + todos los IDs de partidas disponibles
opciones_filtro = ["Todas las partidas"] + list(df['id_partida'].unique())

# El desplegable para que el usuario elija
filtro_partida = st.selectbox("Analizar fricción mecánica de:", opciones_filtro)

# Filtramos el DataFrame antes de hacer los cálculos
if filtro_partida == "Todas las partidas":
    df_calor = df.copy()
else:
    df_calor = df[df['id_partida'] == filtro_partida].copy()

# Transformación de datos sobre el DataFrame filtrado
df_calor['casilla_destino'] = df_calor['movimiento_uci'].str[2:4]
frecuencias = df_calor['casilla_destino'].value_counts().reset_index()
frecuencias.columns = ['casilla', 'visitas']

if not frecuencias.empty:
    frecuencias['columna'] = frecuencias['casilla'].str[0]
    frecuencias['fila'] = frecuencias['casilla'].str[1].astype(int)
    matriz = frecuencias.pivot(index='fila', columns='columna', values='visitas').fillna(0)
else:
    # Seguro por si una partida se canceló en el turno 0
    matriz = pd.DataFrame()

# MAGIA DE INGENIERÍA DE DATOS: 
# Forzamos la matriz a ser 8x8 siempre, aunque en esta partida no se hayan pisado todas las casillas
matriz = matriz.reindex(index=range(8, 0, -1), columns=list('abcdefgh'), fill_value=0)

# Dibujamos el mapa
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(matriz, annot=True, fmt="g", cmap="YlOrRd", linewidths=.5, ax=ax, cbar_kws={'label': 'Nº de Impactos'})
ax.set_ylabel("Fila")
ax.set_xlabel("Columna")

st.pyplot(fig)