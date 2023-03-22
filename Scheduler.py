import threading
from CronJob import CronJob

class CentralScheduler:
    """
    This class is the Scheduler of the Cron Jobs, it is essentially a dictionary of Cron Jobs, with syncrhonization to
    support concurrency and not exhibit race conditions

    Attributes:
    jobs: Dictionary of Cron Jobs
    dictt_lock: an atomic lock to ensure the atomicity of the access of the dictionary inside the critical section

    Methods:
    add_job: a method to be called on the scheduler instance to add Cron Jobs to it.
    remove_job: a method to be called on the scheduler instance to remove Cron Jobs from it.
    """
    def __init__( self ):
        self.jobs = {}
        self.dictt_lock = threading.Lock()

    def add_job( self, id, funct, interval, freq ):
        """
        This method adds a Cron Job to the scheduler - can be called concurrently

        inputs:
            id: The Id of the Cron Job
            funct: The function object of the job to run
            interval: The expected interval of a single run 
            freq: The scheduling frequency - the time that should elapse between every run of the job
        """

        # Lock to ensure the atomicity of accessing the jobs dictionary - The Critical Section
        with self.dictt_lock:
            if id not in self.jobs:
                job = CronJob( id, funct, interval, freq )
                self.jobs[ id ] = job

            else:
                return "FAILURE: The Job with the id: " + str(id) + " is already in the jobs list."
                
            
        # Running the job itself doesn't have to be inside the lock
        try:
            thread = threading.Thread( target=job.run )
            thread.start()
            return "SUCCESS: The Job with the id: " + str(id) + " was added successfully to the jobs list."
        except Exception as e:
            return "FAILURE: The Job with the id: " + str(id) + " couldn't start, error: " + str(e)



    def remove_job( self, id ):
        """
        This method Removes the Cron Job with the Id: id from the scheduler - can be called concurrently

        inputs:
            id: The Id of the Cron Job
            funct: The function object of the job to run
            interval: The expected interval of a single run 
            frequency: The scheduling frequency - the time that should elapse between every run of the job
        """

        # Lock to ensure the atomicity of accessing the jobs dictionary - The Critical Section
        with self.dictt_lock:
            if id not in self.jobs:
                return "FAILURE: The Job with the id: " + str(id) + " is NOT in the jobs list."
            
            self.jobs[ id ].stop()
            del self.jobs[ id ]
            return "SUCCESS: The Job with the id: " + str(id) + " was removed successfully from the jobs list."
                
