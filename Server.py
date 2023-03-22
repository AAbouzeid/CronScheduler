import socket
import threading
import importlib.util
import os
import sys
from Scheduler import CentralScheduler
import signal
import time

# Host and Port Values
SERVER_HOST = "localhost"
SERVER_PORT = 10000

# The single instance of the Scheduler that holds all the jobs
scheduler = CentralScheduler()

def import_func( job_func_name, file_path):
    """
    Helper Function that returns a function object given it's name, and file path

    inputs:
        job_func_name: The name of the job function
        file_path: The path of the file containing the function implementation
    """
    spec = importlib.util.spec_from_file_location( "job_module", file_path )
    job_module = importlib.util.module_from_spec( spec )
    sys.modules[ "job_module" ] = job_module
    spec.loader.exec_module( job_module )
    return getattr( job_module, job_func_name )

def add( request_parts ):
    """
    This function handles any Add requests made by a client

    inputs:
        request_parts: The request made by the client on the command line splitted into components
    """
    _, job_id, interval, frequency, job_func_name, file_path = request_parts

    if os.path.exists( file_path ):
        job_func = import_func( job_func_name, file_path )
        add = scheduler.add_job( job_id, job_func, interval, frequency )
        if "SUCCESS" in add:
            return "SUCCESS: Job: " + str( job_id ) + " added successfully.\n"
        else:
            return "FAILURE: Job: " + str( job_id ) + " is already in the jobs list.\n"
    else:
        return "FAILURE: File not found: " + str( file_path ) + "\n"

def remove( request_parts ):
    """
    This function handles any Remove requests made by a client

    inputs:
        request_parts: The request made by the client on the command line splitted into components
    """
    _, job_id = request_parts
    remove = scheduler.remove_job( job_id )
    if "SUCCESS" in remove:
        return "SUCCESS: Job " + str( job_id ) + " removed successfully.\n"
    else:
        return "FAILURE: Job " + str( job_id ) + " is NOT in the jobs list.\n"

def parse_request( client_socket ):
    """
    This function parses the users request, serves it and retursn the response to the client

    input:
        client_socket: The client's socket to which the data is received and sent
    """
    request_data = client_socket.recv( 1024 ).decode()
    request_parts = request_data.strip().split()

    command_map = {
        "ADD": add,
        "REMOVE": remove,
    }

    if request_parts[0] in command_map:
        response = command_map[request_parts[0]](request_parts)
    else:
        response = "FAILURE: Invalid command.\n"

    client_socket.sendall( response.encode() )

def process_client_request( client_socket ):
    """
    This function takes a client socket value, receives it's request, decodes,
    Verifies it's formatting and executes it accordingly.

    input:
        client_socket: The socket value of the client
    """
    try:
        parse_request( client_socket )

    except Exception as e:
        response = "FAILURE: Error processing client request: "+ str(e)
        print( response )
        client_socket.sendall( response.encode() )

    finally:
        client_socket.close()

def main():
    def signal_handler( signal, frame ):
        time.sleep(0.5)
        print( "\nExiting the Server Gracefully due to a Keyboard Interrupt\n" )
        with server_socket:
            server_socket.close()
            sys.exit( 0 )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_address = ( SERVER_HOST, SERVER_PORT )
        server_socket.bind( server_address )
        server_socket.listen()

        print( "LOGGING: Starting scheduler server on " + str( server_address ) )
        signal.signal( signal.SIGINT, signal_handler )

        while True:
            client_socket, client_address = server_socket.accept()
            print( "LOGGING: Connection from " + str( client_address ) )
            client_thread = threading.Thread( target=process_client_request, args=( client_socket, ) )
            client_thread.daemon = True
            client_thread.start()



if __name__ == "__main__":
    main()
