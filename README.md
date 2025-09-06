# Servidor y Cliente de Sockets

Este proyecto implementa un servidor y un cliente de sockets en Python. El servidor escucha en `localhost:5000` y guarda los mensajes recibidos en una base de datos SQLite. El cliente se conecta al servidor y permite enviar múltiples mensajes hasta que el usuario escriba "exito".

## Requisitos

*   Python 3.x
*   sqlite3 (generalmente incluido con Python)

## Instrucciones de uso

1.  **Ejecutar el servidor:**

    ```bash
    python server/server.py
    ```

2.  **Ejecutar el cliente:**

    ```bash
    python client/client.py
    ```

## Base de datos

La base de datos SQLite se guarda en el archivo `database.db` en la raíz del proyecto. La tabla `mensajes` tiene los siguientes campos:

*   `id`: Identificador único del mensaje (entero, clave primaria, autoincremental).
*   `contenido`: Contenido del mensaje (texto).
*   `fecha_envio`: Fecha y hora de envío del mensaje (texto en formato ISO 8601).
*   `ip_cliente`: Dirección IP del cliente que envió el mensaje (texto).

## Manejo de errores

El servidor implementa manejo de errores para:

*   Puerto ocupado: Si el puerto 5000 ya está en uso, el servidor mostrará un mensaje de error y se cerrará.
*   Base de datos no accesible: Si no se puede conectar a la base de datos, el servidor mostrará un mensaje de error y se cerrará.
*   Errores de socket: Si ocurre un error durante la aceptación de conexiones, el servidor mostrará un mensaje de error.
*   Errores de base de datos: Si ocurre un error al guardar el mensaje en la base de datos, se mostrará un mensaje de error.

El cliente implementa manejo de errores para:

*   Error de socket: Si no se puede conectar al servidor, el cliente mostrará un mensaje de error.
*   Error inesperado: Si ocurre un error inesperado, el cliente mostrará un mensaje de error.

## Notas

*   El servidor utiliza threads para manejar múltiples clientes concurrentemente.
*   El cliente se cierra cuando el usuario escribe "exito".
