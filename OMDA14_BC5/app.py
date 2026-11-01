
# ============================================================
# CABECERA
# ============================================================
# Alumno: Edison Michael Salazar Ramos
# URL Streamlit Cloud: https://tu-app-wrapped.streamlit.app
# URL GitHub: https://github.com/tu-usuario/tu-repo

# ============================================================
# IMPORTS
# ============================================================
# Streamlit: framework para crear la interfaz web
# pandas: manipulación de datos tabulares
# plotly: generación de gráficos interactivos
# openai: cliente para comunicarse con la API de OpenAI
# json: para parsear la respuesta del LLM (que llega como texto JSON)
import json
import openai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from openai import OpenAI

# ============================================================
# CONSTANTES
# ============================================================
# Modelo de OpenAI. No lo cambies.
MODEL = "gpt-4.1-mini"

# -------------------------------------------------------
# >>> SYSTEM PROMPT — TU TRABAJO PRINCIPAL ESTÁ AQUÍ <<<
# -------------------------------------------------------
# El system prompt es el conjunto de instrucciones que recibe el LLM
# ANTES de la pregunta del usuario. Define cómo se comporta el modelo:
# qué sabe, qué formato debe usar, y qué hacer con preguntas inesperadas.
#
# Puedes usar estos placeholders entre llaves — se rellenan automáticamente
# con información real del dataset cuando la app arranca:
#   {fecha_min}             → primera fecha del dataset
#   {fecha_max}             → última fecha del dataset
#   {plataformas}           → lista de plataformas (Android, iOS, etc.)
#   {reason_start_values}   → valores posibles de reason_start
#   {reason_end_values}     → valores posibles de reason_end
#
# IMPORTANTE: como el prompt usa llaves para los placeholders,
# si necesitas escribir llaves literales en el texto (por ejemplo para
# mostrar un JSON de ejemplo), usa doble llave: {{ y }}
#
SYSTEM_PROMPT = """Eres un analista de datos experto en Spotify. Tu tarea es generar código Python/Plotly para crear gráficos interactivos basados en un DataFrame de pandas precargado llamado `df`.

ESTRUCTURA DEL DATAFRAME `df`:
Rango temporal de datos: desde {fecha_min} hasta {fecha_max}.
Plataformas disponibles: {plataformas}
Valores reason_start: {reason_start_values}
Valores reason_end: {reason_end_values}

Columnas disponibles en `df`:
- ts: Timestamp de la reproducción (datetime64[ns, UTC])
- ms_played: Tiempo reproducido en milisegundos (int)
- minutes_played: Tiempo reproducido en minutos (float)
- hours_played: Tiempo reproducido en horas (float)
- master_metadata_track_name: Nombre de la canción (string)
- master_metadata_album_artist_name: Nombre del artista principal (string)
- master_metadata_album_album_name: Nombre del álbum (string)
- spotify_track_uri: ID único de la canción (string)
- reason_start: Motivo de inicio de reproducción (string)
- reason_end: Motivo de fin de reproducción (string)
- shuffle: Modo aleatorio activado (bool: True/False)
- skipped: Si la canción fue saltada (bool/None). Regla: una canción es saltada si skipped == True o reason_end == 'fwdbtn'.
- platform: Plataforma utilizada (string)
- year: Año (int)
- month: Número de mes (1 a 12)
- month_name: Nombre del mes en inglés (string)
- month_year: Periodo 'YYYY-MM' (string)
- hour: Hora del día (0 a 23)
- day_name: Nombre del día de la semana en inglés (string)
- is_weekend: Si es fin de semana (bool: True para Sábado y Domingo)
- season: Estación del año ('Primavera', 'Verano', 'Otoño', 'Invierno')
- semester: Semestre del año ('H1 (Ene-Jun)', 'H2 (Jul-Dic)')

FORMATO OBLIGATORIO DE RESPUESTA:
Debes responder ÚNICAMENTE con un objeto JSON válido (sin backticks de código salvo en la propiedad 'codigo').

Si la pregunta se refiere a los datos de Spotify, responde con:
{{
  "tipo": "grafico",
  "codigo": "código python ejecutable que cree una figura de Plotly asignada estrictamente a la variable `fig`",
  "interpretacion": "explicación clara de 2-3 frases en español contextualizando los resultados del gráfico"
}}

Si la pregunta NO está relacionada con el historial de Spotify (ej. recetas, clima, finanzas generales), responde con:
{{
  "tipo": "fuera_de_alcance",
  "codigo": "",
  "interpretacion": "Lo siento, solo puedo responder a preguntas analíticas relacionadas con tu historial de escuchas de Spotify."
}}

REGLAS DE CÓDIGO:
1. El código debe asignar la visualización final a la variable `fig`. Usa `px` (plotly.express) o `go` (plotly.graph_objects).
2. Agrega siempre títulos descriptivos y etiquetas en español a los ejes.
3. No incluyas `import` ni cargas de archivos (usan `df`, `pd`, `px`, `go` precargados).

EJEMPLO DE RESPUESTA VÁLIDA:
{{
  "tipo": "grafico",
  "codigo": "top = df.groupby('master_metadata_album_artist_name')['hours_played'].sum().nlargest(10).reset_index()\\nfig = px.bar(top, x='hours_played', y='master_metadata_album_artist_name', orientation='h', title='Top 10 Artistas por Horas', labels={{'hours_played': 'Horas', 'master_metadata_album_artist_name': 'Artista'}})\\nfig.update_layout(yaxis={{'categoryorder': 'total ascending'}})",
  "interpretacion": "Aquí tienes el ranking de tus 10 artistas más escuchados en horas totales dentro de Spotify."
}}
"""


# ============================================================
# CARGA Y PREPARACIÓN DE DATOS
# ============================================================
# Esta función se ejecuta UNA SOLA VEZ gracias a @st.cache_data.
# Lee el fichero JSON y prepara el DataFrame para que el código
# que genere el LLM sea lo más simple posible.
#

@st.cache_data
def load_data():

    # Obtener la ruta del archivo JSON
    file_path = BASE_DIR / "streaming_history.json"

    # Validar que el archivo exista
    if not file_path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo JSON: {file_path}"
        )

    # Cargar dataset
    df = pd.read_json(file_path)

    # ----------------------------------------------------------
    # PREPARACIÓN DE DATOS
    # ----------------------------------------------------------

    # Conversión de fechas
    df["ts"] = pd.to_datetime(df["ts"])

    # Conversión de tiempos
    df["minutes_played"] = df["ms_played"] / 60000.0
    df["hours_played"] = df["ms_played"] / 3600000.0

    # Columnas temporales derivadas
    df["year"] = df["ts"].dt.year
    df["month"] = df["ts"].dt.month
    df["month_name"] = df["ts"].dt.strftime("%B")
    df["month_year"] = df["ts"].dt.strftime("%Y-%m")
    df["hour"] = df["ts"].dt.hour
    df["day_name"] = df["ts"].dt.day_name()
    df["is_weekend"] = df["ts"].dt.dayofweek >= 5

    # Estaciones del año
    def assign_season(m):
        if m in [12, 1, 2]:
            return "Invierno"
        elif m in [3, 4, 5]:
            return "Primavera"
        elif m in [6, 7, 8]:
            return "Verano"
        else:
            return "Otoño"

    df["season"] = df["month"].apply(assign_season)

    # Semestres
    df["semester"] = df["month"].apply(
        lambda m: "H1 (Ene-Jun)" if m <= 6 else "H2 (Jul-Dic)"
    )

    return df


def build_prompt(df):
    """Inyecta información dinámica del dataset en el system prompt.

    Los valores que calcules aquí reemplazan a los placeholders {fecha_min},
    {fecha_max}, etc. dentro de SYSTEM_PROMPT.

    Si añades columnas nuevas en load_data() y quieres que el LLM conozca sus
    valores posibles, añade aquí el cálculo y un nuevo placeholder en
    SYSTEM_PROMPT.
    """
    fecha_min = df["ts"].min()
    fecha_max = df["ts"].max()
    plataformas = df["platform"].unique().tolist()
    reason_start_values = df["reason_start"].unique().tolist()
    reason_end_values = df["reason_end"].unique().tolist()

    return SYSTEM_PROMPT.format(
        fecha_min=fecha_min,
        fecha_max=fecha_max,
        plataformas=plataformas,
        reason_start_values=reason_start_values,
        reason_end_values=reason_end_values,
    )


# ============================================================
# FUNCIÓN DE LLAMADA A LA API
# ============================================================
# Esta función envía DOS mensajes a la API de OpenAI:
# 1. El system prompt (instrucciones generales para el LLM)
# 2. La pregunta del usuario
#
# El LLM devuelve texto (que debería ser un JSON válido).
# temperature=0.2 hace que las respuestas sean más predecibles.
#
# No modifiques esta función.
#
def get_response(user_msg, system_prompt):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


# ============================================================
# PARSING DE LA RESPUESTA
# ============================================================
# El LLM devuelve un string que debería ser un JSON con esta forma:
#
#   {"tipo": "grafico",          "codigo": "...", "interpretacion": "..."}
#   {"tipo": "fuera_de_alcance", "codigo": "",    "interpretacion": "..."}
#
# Esta función convierte ese string en un diccionario de Python.
# Si el LLM envuelve el JSON en backticks de markdown (```json...```),
# los limpia antes de parsear.
#
# No modifiques esta función.
#
def parse_response(raw):
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    return json.loads(cleaned)


# ============================================================
# EJECUCIÓN DEL CÓDIGO GENERADO
# ============================================================
# El LLM genera código Python como texto. Esta función lo ejecuta
# usando exec() y busca la variable `fig` que el código debe crear.
# `fig` debe ser una figura de Plotly (px o go).
#
# El código generado tiene acceso a: df, pd, px, go.
#
# No modifiques esta función.
#
def execute_chart(code, df):
    local_vars = {"df": df, "pd": pd, "px": px, "go": go}
    exec(code, {}, local_vars)
    return local_vars.get("fig")


# ============================================================
# INTERFAZ STREAMLIT
# ============================================================
# Toda la interfaz de usuario. No modifiques esta sección.
#

# Configuración de la página
st.set_page_config(page_title="Spotify Analytics", layout="wide")

# --- Control de acceso ---
# Lee la contraseña de secrets.toml. Si no coincide, no muestra la app.
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Acceso restringido")
    pwd = st.text_input("Contraseña:", type="password")
    if pwd:
        if pwd == st.secrets["PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.stop()

# --- App principal ---
st.title("🎵 Spotify Analytics Assistant")
st.caption("Pregunta lo que quieras sobre tus hábitos de escucha")

# Cargar datos y construir el prompt con información del dataset
df = load_data()
system_prompt = build_prompt(df)

# Caja de texto para la pregunta del usuario
if prompt := st.chat_input("Ej: ¿Cuál es mi artista más escuchado?"):

    # Mostrar la pregunta en la interfaz
    with st.chat_message("user"):
        st.write(prompt)

    # Generar y mostrar la respuesta
    with st.chat_message("assistant"):
        with st.spinner("Analizando..."):
            try:
                # 1. Enviar pregunta al LLM
                raw = get_response(prompt, system_prompt)

                # 2. Parsear la respuesta JSON
                parsed = parse_response(raw)

                if parsed["tipo"] == "fuera_de_alcance":
                    # Pregunta fuera de alcance: mostrar solo texto
                    st.write(parsed["interpretacion"])
                else:
                    # Pregunta válida: ejecutar código y mostrar gráfico
                    fig = execute_chart(parsed["codigo"], df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        st.write(parsed["interpretacion"])
                        st.code(parsed["codigo"], language="python")
                    else:
                        st.warning(
                            "El código no produjo ninguna visualización. Intenta"
                            " reformular la pregunta."
                        )
                        st.code(parsed["codigo"], language="python")

            except json.JSONDecodeError:
                st.error(
                    "No he podido interpretar la respuesta. Intenta reformular"
                    " la pregunta."
                )
            except Exception as e:
                st.error(
                    "Ha ocurrido un error al generar la visualización. Intenta"
                    " reformular la pregunta."
                )


# ============================================================
# REFLEXIÓN TÉCNICA (máximo 30 líneas)
# ============================================================
#
# Responde a estas tres preguntas con tus palabras. Sé concreto
# y haz referencia a tu solución, no a generalidades.
# No superes las 30 líneas en total entre las tres respuestas.
#
# 1. ARQUITECTURA TEXT-TO-CODE
#    ¿Cómo funciona la arquitectura de tu aplicación? ¿Qué recibe
#    el LLM? ¿Qué devuelve? ¿Dónde se ejecuta el código generado?
#    ¿Por qué el LLM no recibe los datos directamente?
#
#    El LLM no recibe las ~15.000 reproducciones del archivo JSON, sino únicamente
#    la estructura estática del DataFrame (`df`), los nombres de columnas, tipos y
#    un esquema JSON obligatorio de salida. Devuelve un texto JSON conteniendo el
#    código Python/Plotly y la interpretación narrada. El código se ejecuta de
#    forma local e aislada en el servidor mediante la función `exec()`. No se envían
#    los datos directamente al LLM por privacidad del usuario, para evitar sobrepasar
#    los límites de tokens/costes de la API, y porque Python garantiza un cómputo 100%
#    exacto evitando las alucinaciones matemáticas del LLM.
#
# 2. EL SYSTEM PROMPT COMO PIEZA CLAVE
#    ¿Qué información le das al LLM y por qué? Pon un ejemplo
#    concreto de una pregunta que funciona gracias a algo específico
#    de tu prompt, y otro de una que falla o fallaría si quitases
#    una instrucción.
#
#    Al LLM le proporciono el esquema enriquecido de columnas (incluyendo derivadas
#    como `hours_played`, `is_weekend`, `season`), reglas explícitas de filtrado (como la
#    definición de canciones saltadas) y la estructura del JSON de salida. Por ejemplo, la
#    pregunta "¿Compara mi top de verano vs invierno?" funciona gracias a que en `load_data`
#    se creó la columna `season` y en el prompt se explicitaron sus valores. Si quitase la
#    instrucción de devolver `tipo: fuera_de_alcance`, ante preguntas no musicales (ej. "¿Cómo
#    hacer pizza?"), el LLM intentaría filtrar columnas del DataFrame buscando "pizza",
#    fallando estrepitosamente.
#
# 3. EL FLUJO COMPLETO
#    Describe paso a paso qué ocurre desde que el usuario escribe
#    una pregunta hasta que ve el gráfico en pantalla.
#
#    El usuario escribe una consulta en el `st.chat_input`. `build_prompt(df)` inyecta
#    los rangos de fechas y valores reales en el `SYSTEM_PROMPT`. `get_response()` envía
#    el prompt y la pregunta a `gpt-4.1-mini`. `parse_response()` convierte la cadena JSON
#    devuelta en un diccionario de Python. Si el tipo es `grafico`, `execute_chart()` ejecuta
#    el string de código con `exec()` inyectándole `df`, `pd`, `px` y `go`, asignando la figura
#    a `fig`. Finalmente, Streamlit renderiza el gráfico mediante `st.plotly_chart()`, muestra
#    la interpretación y desglosa el código ejecutado.
