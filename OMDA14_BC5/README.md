# 🎵 Spotify Analytics Assistant

Aplicación web interactiva que permite analizar el historial de reproducciones de Spotify mediante consultas en lenguaje natural, utilizando inteligencia artificial para generar visualizaciones dinámicas y facilitar la interpretación de los hábitos de escucha.

El proyecto implementa una arquitectura **Text-to-Code**, donde un modelo de lenguaje interpreta las preguntas del usuario, genera código Python con Plotly y permite visualizar los resultados a través de una interfaz desarrollada con Streamlit.

## 🚀 Objetivo del proyecto

Transformar el historial de reproducciones de Spotify en información útil mediante herramientas de análisis de datos e inteligencia artificial, permitiendo identificar patrones de consumo musical sin necesidad de conocimientos técnicos o programación.

## ✨ Funcionalidades principales

- **Consultas en lenguaje natural:** permite realizar preguntas sobre los hábitos de escucha sin escribir código.
- **Generación automática de gráficos:** utiliza GPT-4.1-mini para generar código Python y visualizaciones interactivas con Plotly.
- **Análisis temporal:** permite estudiar reproducciones por año, mes, día, hora, semestre y estación del año.
- **Análisis musical:** facilita la identificación de artistas, canciones y álbumes más escuchados.
- **Análisis de comportamiento:** permite explorar patrones relacionados con el modo aleatorio, canciones saltadas y motivos de inicio o finalización de reproducciones.
- **Análisis por plataforma:** permite comparar el comportamiento de escucha según la plataforma utilizada.
- **Interpretación automatizada:** acompaña cada visualización con una explicación en español.
- **Control de acceso:** incorpora autenticación mediante contraseña.

## 🛠️ Tecnologías utilizadas

| Tecnología | Aplicación |
|---|---|
| Python | Lenguaje principal |
| Streamlit | Desarrollo de la interfaz web |
| Pandas | Manipulación y preparación de datos |
| Plotly | Visualizaciones interactivas |
| OpenAI API | Generación de código mediante IA |
| GPT-4.1-mini | Interpretación de consultas y generación de gráficos |
| JSON | Procesamiento de respuestas del modelo |

## 🏗️ Arquitectura del proyecto

El sistema utiliza una arquitectura Text-to-Code que separa el procesamiento de datos de la generación de instrucciones mediante inteligencia artificial.

### Flujo de funcionamiento

1. **Carga de datos:** se importa el historial de reproducciones desde `streaming_history.json`.
2. **Preparación de datos:** Pandas transforma las fechas, calcula los tiempos de reproducción y genera variables temporales.
3. **Construcción del contexto:** se proporciona al modelo la estructura del DataFrame, sus columnas y los valores disponibles.
4. **Interpretación de la consulta:** GPT-4.1-mini recibe la pregunta del usuario y genera una respuesta estructurada en JSON.
5. **Generación de código:** el modelo produce código Python utilizando Plotly para construir la visualización solicitada.
6. **Ejecución local:** Python ejecuta el código generado utilizando el DataFrame previamente cargado.
7. **Visualización:** Streamlit presenta el gráfico, la interpretación y el código utilizado.

### Diagrama de arquitectura

```text
       HISTORIAL DE SPOTIFY
       streaming_history.json
                 |
                 v
       PREPARACIÓN DE DATOS
              Pandas
                 |
                 v
        DATAFRAME EN MEMORIA
                 |
                 v
       CONSULTA DEL USUARIO
             Streamlit
                 |
                 v
          OPENAI API
          GPT-4.1-mini
                 |
                 v
       GENERACIÓN DE CÓDIGO
          Python + Plotly
                 |
                 v
         RESPUESTA JSON
                 |
                 v
        EJECUCIÓN LOCAL
              exec()
                 |
                 v
       VISUALIZACIÓN INTERACTIVA
              Streamlit
```

## 📊 Estructura de los datos

El DataFrame incorpora variables que permiten realizar diferentes tipos de análisis:

- **Información musical:** canción, artista, álbum e identificador de Spotify.
- **Tiempo de reproducción:** milisegundos, minutos y horas reproducidas.
- **Información temporal:** año, mes, hora y día de la semana.
- **Comportamiento:** canciones saltadas, reproducción aleatoria y motivos de inicio y finalización.
- **Segmentación temporal:** estaciones del año, fines de semana y semestres.
- **Plataformas:** dispositivo o plataforma desde la que se realizó la reproducción.

## 🔐 Privacidad y procesamiento

Una característica importante de la arquitectura es que el historial completo de reproducciones no se envía directamente al modelo de inteligencia artificial.

El modelo recibe la estructura del DataFrame y el contexto necesario para generar el código analítico. Los cálculos se realizan localmente sobre los datos cargados en la aplicación.

La aplicación utiliza variables de entorno de Streamlit Secrets para gestionar la API Key de OpenAI y la contraseña de acceso.

## ⚙️ Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo
```

### 2. Instalar dependencias

```bash
pip install streamlit pandas plotly openai
```

### 3. Incorporar los archivos

```text
spotify-analytics/
│
├── app.py
├── streaming_history.json
├── requirements.txt
└── .streamlit/
    └── secrets.toml
```

### 4. Configurar credenciales

Crear el archivo `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "tu_api_key"
PASSWORD = "tu_contraseña"
```

### 5. Ejecutar la aplicación

```bash
streamlit run app.py
```

## ☁️ Despliegue

La aplicación está diseñada para desplegarse en Streamlit Community Cloud, utilizando GitHub como repositorio de código y Streamlit Secrets para almacenar las credenciales necesarias.

- **Aplicación:** https://tu-app-wrapped.streamlit.app
- **Repositorio:** https://github.com/tu-usuario/tu-repo

*Nota: los enlaces anteriores son marcadores de posición y deben reemplazarse por las direcciones definitivas.*

## 🧠 Conceptos aplicados

Este proyecto integra conocimientos de:

- Análisis y transformación de datos.
- Ingeniería de prompts (*Prompt Engineering*).
- Modelos de lenguaje de gran escala (LLM).
- Arquitectura Text-to-Code.
- Automatización de análisis mediante inteligencia artificial.
- Generación de visualizaciones dinámicas.
- Desarrollo de aplicaciones web con Python.

## 👨‍💻 Autor

**Edison Michael Salazar Ramos**

Proyecto desarrollado como aplicación práctica de integración entre análisis de datos, inteligencia artificial generativa y visualización interactiva.

Solución al caso Spotify