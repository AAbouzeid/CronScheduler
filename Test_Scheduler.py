import unittest
import socket
import sys
import os
import threading

sys.path.append(os.path.abspath(os.path.join('..')))
SERVER_HOST = 'localhost'
SERVER_PORT = 10000


def send_request(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        client_socket.sendall(command.encode())
        response = client_socket.recv(1024)
        return response.decode().strip()


class TestScheduler(unittest.TestCase):
    """
    This is a testing suite for the Cron Scheduler project
    """
    def test_add_remove_job(self):
        """
        This function is a basic test of functionality, tests if the Scheduler application is able to add and remove a job successfully
        """
        add_response = send_request("ADD 1 10s 5s test_func1 test_func1.py")
        self.assertEqual(add_response, "SUCCESS: Job: 1 added successfully.")

        remove_response = send_request("REMOVE 1")
        self.assertEqual(remove_response, "SUCCESS: Job 1 removed successfully.")


    def test_remove_before_add(self):
        """
        This function is testing how the Scheduler would handle removing a job that is not in the jobs list
        """
        remove_response = send_request("REMOVE 1")
        self.assertEqual(remove_response, "FAILURE: Job 1 is NOT in the jobs list.")


    def test_add_existing_job(self):
        """
        This function tries adding a job that's already in the Scheduler
        """
        add_response = send_request("ADD 1 10s 5s test_func1 test_func1.py")
        self.assertEqual(add_response, "SUCCESS: Job: 1 added successfully.")

        add_response = send_request("ADD 1 10s 5s test_func1 test_func1.py")
        self.assertEqual(add_response, "FAILURE: Job: 1 is already in the jobs list.")

        remove_response = send_request("REMOVE 1")
        self.assertEqual(remove_response, "SUCCESS: Job 1 removed successfully.")


    def test_error_func(self):
        """
        This function runs a job that would cause an exception, and handles it gracefully in the Scheduler
        """
        # The expected behavior is that the scheduler will handle the exception and terminate this job gracefully every time.
        add_response = send_request("ADD 3 10s 5s test_func4 test_func4.py")
        self.assertEqual(add_response, "SUCCESS: Job: 3 added successfully.")

        remove_response = send_request("REMOVE 3")
        self.assertEqual(remove_response, "SUCCESS: Job 3 removed successfully.")


    def test_wrong_func_name(self):
        """
        This function tests running a job with a function name that is not found in the provided file path
        """
        # Testing whether the Application will be able to handle running a job with the function name incorrect
        add_response = send_request("ADD 3 10s 5s test_func4 test_func3.py")
        self.assertEqual(add_response, "FAILURE: Error processing client request: module 'job_module' has no attribute 'test_func4'")

    
    def test_concurrent_requests(self):
        """
        This funciton tests running three jobs concurrently, then removing them also concurrently.
        """
        add_commands = [
            "ADD 1 10s 5s test_func1 test_func1.py",
            "ADD 2 15s 3s test_func2 test_func2.py",
            "ADD 3 20s 1s test_func3 test_func3.py",
        ]

        remove_commands = [
            "REMOVE 1",
            "REMOVE 2",
            "REMOVE 3",
        ]

        responses = [None] * ( len(add_commands) + len(remove_commands) )

        def send_concurrent_request(index, command):
            response = send_request(command)
            responses[index] = (command, response)

        threads = []
        for i, command in enumerate(add_commands):
            thread = threading.Thread(target=send_concurrent_request, args=(i, command))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for i, command in enumerate(remove_commands):
            thread = threading.Thread(target=send_concurrent_request, args=(i+3, command))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for command, response in responses:
            if 'ADD' in command:
                job_id = command.split()[1]
                self.assertEqual(response, "SUCCESS: Job: " + str(job_id) + " added successfully.")
            elif 'REMOVE' in command:
                job_id = command.split()[1]
                self.assertEqual(response, "SUCCESS: Job " + str(job_id) + " removed successfully.")




if __name__ == '__main__':
    unittest.main()
