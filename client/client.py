import socket

HOST = 'localhost'
PORT = 5000

def main():
    """Función principal del cliente."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print(f"Conectado al servidor en {HOST}:{PORT}")

        while True:
            message = input("Ingrese el mensaje (o 'exito' para salir): ")
            if message.lower() == 'exito':
                break

            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Respuesta del servidor: {response}")

    except socket.error as e:
        print(f"Error de socket: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        print("Cerrando conexión.")
        if client_socket:
            client_socket.close()

if __name__ == "__main__":
    main()