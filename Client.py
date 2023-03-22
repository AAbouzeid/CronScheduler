import socket
import sys

def exchange_message( client_socket, command ):
    client_socket.sendall( command.encode() )
    response = client_socket.recv( 1024 )
    return response.decode().strip()

def main():
    # To catch if the input command is iu
    if len( sys.argv ) < 2:
        print( "Usage: " + str( sys.argv[ 0 ] ) + " ADD JOB_ID INTERVAL FREQUENCY JOB_FUNCTION_NAME FUNCTION_IMPLEMENTATION_PATH" )
        print( "OR " + str( sys.argv[ 0 ] ) + " REMOVE JOB_ID" ) 
        sys.exit( 1 )

    # Connected to the server
    command = ' '.join( sys.argv[ 1: ] )
    with socket.socket( socket.AF_INET, socket.SOCK_STREAM ) as client_socket:
        server_address = ( 'localhost', 10000 )
        client_socket.connect( server_address )

        # Trying to send request to the server
        try:
            print( exchange_message( client_socket, command ) )
        finally:
            client_socket.close()

if __name__ == "__main__":
    main()
