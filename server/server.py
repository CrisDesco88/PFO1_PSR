import socket
import sqlite3
import threading
import time
import datetime

# Configuración del servidor
HOST = 'localhost'
PORT = 5000
DB_NAME = 'database.db'

def init_socket():
    """Inicializa el socket del servidor."""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Servidor escuchando en {HOST}:{PORT}")
        return server_socket
    except socket.error as e:
        print(f"Error al inicializar el socket: {e}")
        return None

def handle_client(client_socket, client_address):
    """Maneja la conexión de un cliente."""
    print(f"Conexión aceptada de {client_address}")
    db_conn = None  # Inicializar db_conn a None
    try:
        db_conn = sqlite3.connect(DB_NAME)
        cursor = db_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio DATETIME NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        """)
        db_conn.commit()
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            message = data.decode('utf-8')
            timestamp = datetime.datetime.now().isoformat()
            print(f"Mensaje recibido: {message} de {client_address}")

            # Guardar el mensaje en la base de datos
            try:
                cursor.execute("""
                    INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
                    VALUES (?, ?, ?)
                """, (message, timestamp, client_address[0]))
                db_conn.commit()
                print("Mensaje guardado en la base de datos.")
            except sqlite3.Error as e:
                print(f"Error al guardar el mensaje en la base de datos: {e}")

            # Responder al cliente
            response = f"Mensaje recibido: {timestamp}".encode('utf-8')
            client_socket.send(response)

    except Exception as e:
        print(f"Error al manejar la conexión del cliente: {e}")
    finally:
        print(f"Conexión con {client_address} cerrada.")
        client_socket.close()
        if db_conn:
            db_conn.close()


def main():
    """Función principal del servidor."""
    server_socket = init_socket()
    if not server_socket:
        print("No se pudo inicializar el socket. Saliendo...")
        return

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address,))
            client_thread.start()
    except socket.error as e:
        print(f"Error al aceptar conexiones: {e}")
    except KeyboardInterrupt:
        print("Servidor detenido manualmente.")
    finally:
        if server_socket:
            server_socket.close()
        print("Servidor cerrado.")

if __name__ == "__main__":
    main()