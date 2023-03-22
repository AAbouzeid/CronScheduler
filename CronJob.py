import threading
from Utils import convert_to_seconds
import time
from queue import Queue, Empty

class CronJob:
    """
    This class is to hold the information about a Cron Job

    Attributes:
    id: The Id of the Cron Job
    funct: The function object of the job to run
    interval: The expected interval of a single run 
    freq: The scheduling frequency - the time that should elapse between every run of the job
    signal_queue: a Synchronizing Queue instance - To flag that the job should stop repeating

    Methods:
    run: The method starts running the job and logs various information
    stop: stops running the cron job periodically.
    """
    def __init__( self, id, funct, interval, freq ):
        self.id = id
        self.funct = funct
        self.interval = convert_to_seconds( interval )
        self.freq = convert_to_seconds( freq )
        self._signal_queue = Queue()

    def run( self ):
        """
        This function is invoked when the Cron Job is ready to run the function provided to the schedule at the 
        creation of the job.
        """
        while True:
            # Info/Time before starting the job
            start_time = time.time()
            start_str = "LOGGING: Job: " + str(self.id) + " started at: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)))
            print( start_str )
            
            # Running the job requested by the client in a try-catch statement to prevent errors from
            # Crashing the Scheduler
            try:
                self.funct()

            except Exception as e:
                print( "FAILURE: Error Running the provided job: " + str(e))

            # Info/Time after running the job
            end_time = time.time()
            end_str = "LOGGING: Job: " + str(self.id) + " finished at " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)))
            print( end_str )

            # Calculating the Elapsed time vs the expected time, and putting the thread to sleep until, it's
            # time to run it again 
            time_elapsed = end_time - start_time
            elapsed_str = "LOGGING: Expected running time: " + str(self.interval) + " seconds. Actual running time: " + ('%.6f' % time_elapsed) + " seconds."
            print( elapsed_str )
            try:
                self._signal_queue.get( timeout=self.freq )
                break  # Stop the loop when a stop signal is received
            except Empty:
                pass

    def stop(self): 
        """
        This function signals the Cron job to stop repeating itself, as scheduler will remove it from the job list.
        """
        self._signal_queue.put(True)
        print("LOGGING: Job: " + str(self.id) + " removed from the jobs list." )