import unittest
import socket
import sqlite3
import threading
import time
import datetime
import os
from server import server  # Importa el módulo server.py

class TestApp(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para cada prueba."""
        # Configuración del servidor para pruebas
        self.HOST = 'localhost'
        self.PORT = 5001  # Usar un puerto diferente para las pruebas
        self.DB_NAME = 'test_database.db'  # Usar una base de datos diferente para las pruebas

        # Eliminar la base de datos de prueba si existe
        if os.path.exists(self.DB_NAME):
            os.remove(self.DB_NAME)

        # Inicializar el socket del servidor
        #self.server_socket = server.init_socket()
        #if not self.server_socket:
        #    self.fail("No se pudo inicializar el socket del servidor.")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Check if the port is already in use, and if so, select a different port
        while True:
            try:
                self.server_socket.bind((self.HOST, self.PORT))
                break
            except socket.error as e:
                if e.errno == 98:  # Address already in use
                    self.PORT += 1
                else:
                    self.fail(f"No se pudo inicializar el socket del servidor: {e}")
        self.server_socket.listen(5)

        # Inicializar la base de datos
        self.db_conn = sqlite3.connect(self.DB_NAME)
        self.cursor = self.db_conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio DATETIME NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        """)
        self.db_conn.commit()

        # Iniciar el servidor en un thread separado
        #self.server_thread = threading.Thread(target=server.main)
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True  # Permite que el thread se cierre cuando el programa principal termina
        self.server_thread.start()
        time.sleep(0.1)  # Esperar a que el servidor se inicie

    def tearDown(self):
        """Limpieza después de cada prueba."""
        # Cerrar el socket del servidor
        if self.server_socket:
            self.server_socket.close()

        # Cerrar la conexión a la base de datos
        if self.db_conn:
            self.db_conn.close()

        # Eliminar la base de datos de prueba
        if os.path.exists(self.DB_NAME):
            os.remove(self.DB_NAME)

    def run_server(self):
        """Ejecuta el servidor en un bucle."""
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
        except socket.error as e:
            print(f"Error al aceptar conexiones: {e}")

    def handle_client(self, client_socket, client_address):
        """Maneja la conexión de un cliente."""
        try:
            db_conn = sqlite3.connect(self.DB_NAME)
            cursor = db_conn.cursor()
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8')
                timestamp = datetime.datetime.now().isoformat()

                # Guardar el mensaje en la base de datos
                try:
                    cursor.execute("""
                        INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
                        VALUES (?, ?, ?)
                    """, (message, timestamp, client_address[0]))
                    db_conn.commit()
                except sqlite3.Error as e:
                    print(f"Error al guardar el mensaje en la base de datos: {e}")

                # Responder al cliente
                response = f"Mensaje recibido: {timestamp}".encode('utf-8')
                client_socket.send(response)

        except Exception as e:
            print(f"Error al manejar la conexión del cliente: {e}")
        finally:
            client_socket.close()
            if db_conn:
                db_conn.close()

    def test_server_connection(self):
        """Prueba la conexión al servidor."""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.HOST, self.PORT))
            client_socket.close()
        except socket.error as e:
            self.fail(f"No se pudo conectar al servidor: {e}")

    def test_send_message(self):
        """Prueba el envío de un mensaje al servidor."""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.HOST, self.PORT))

            message = "Hola, servidor!"
            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')

            self.assertTrue(response.startswith("Mensaje recibido:"), "La respuesta del servidor no es la esperada.")
            client_socket.close()
        except socket.error as e:
            self.fail(f"Error al enviar el mensaje: {e}")

    def test_database_insertion(self):
        """Prueba la inserción de un mensaje en la base de datos."""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.HOST, self.PORT))

            message = "Mensaje de prueba para la base de datos."
            client_socket.send(message.encode('utf-8'))
            client_socket.recv(1024)  # Recibir la respuesta del servidor

            # Verificar que el mensaje se haya guardado en la base de datos
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT contenido FROM mensajes WHERE contenido = ?", (message,))
            result = cursor.fetchone()

            self.assertIsNotNone(result, "El mensaje no se guardó en la base de datos.")
            client_socket.close()
        except socket.error as e:
            self.fail(f"Error al interactuar con el servidor: {e}")

if __name__ == '__main__':
    unittest.main()