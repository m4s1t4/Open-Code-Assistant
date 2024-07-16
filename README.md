# Open Code Assistant

Este proyecto es un asistente de código abierto que utiliza varias herramientas y APIs para ayudar en el desarrollo de software. El asistente puede realizar tareas como crear y editar archivos, leer contenido de archivos, listar archivos en un directorio, realizar búsquedas web, tomar capturas de pantalla, y más.

## Descripción del Proyecto

El asistente está diseñado para interactuar con el usuario a través de la consola, permitiendo ejecutar comandos y recibir respuestas en tiempo real. Utiliza la API de OpenAI para generar respuestas y la API de Tavily para realizar búsquedas avanzadas en internet. Además, puede procesar imágenes y manejar contenido del portapapeles.

## Instalación

1. Clona el repositorio:
    ```sh
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_REPOSITORIO>
    ```

2. Crea un entorno virtual (opcional pero recomendado):
    ```sh
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias:
    ```sh
    pip install -r requirements.txt
    ```

4. Crea un archivo `.env` en la raíz del proyecto y agrega tus claves API:
    ```env
    OPENAI_API_KEY=tu_clave_api_de_openai
    TAVILY_API_KEY=tu_clave_api_de_tavily
    ```

## Uso

Para iniciar el asistente, simplemente ejecuta el archivo `app.py`:
```sh
python app.py
```

### Comandos Disponibles

- **Texto**: Ingresa cualquier texto para interactuar con el asistente.
- **`exit`**: Salir del asistente.
- **`image`**: Procesar una imagen. Se te pedirá que arrastres y sueltes la imagen en la consola.
- **`take screenshot`**: Tomar una captura de pantalla y guardarla en el directorio `img`.

### Ejemplo de Uso

1. Inicia el asistente:
    ```sh
    python app.py
    ```

2. Ingresa un comando:
    ```sh
    User: create a new file
    ```

3. Sigue las instrucciones del asistente para completar la tarea.
