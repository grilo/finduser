import logging

import task


class TaskManager:

    def __init__(self):
        self.__running = []
        self.__done = []

    def add_task(self, task):
        self.__running.append(task)
        task.start()
        logging.debug("Started task with PID %s" % (task.pid))

    def __refresh(self):
        # Collect the output of processes which are done
        for task in list(self.__running):
            if not task.done(): continue
            if task.returncode != 0:
                logging.error("Error executing the task! PID (%s) cmd (%s) output (%s)" % \
                    (task.pid, task.command, "\n".join(task.stdout, task.stderr)))
            else:
                self.__done.append(task.stdout)
            self.__running.remove(task)

    def get_finished(self):
        self.__refresh()
        reports = self.__done[:]
        self.__done = [] # Clear our 'done' queue
        return reports

    def get_running(self):
        self.__refresh()
        return self.__running
