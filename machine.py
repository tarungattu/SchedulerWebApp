#number of machines


class Machine:
    def __init__(self, machine_id, m):
        self.operationlist = []
        self.machine_id = machine_id % m #machine number
        self.start_operation_time = 0
        self.finish_operation_time = 0
        self.job_sequence_list = []   # sequence in which jobs are received

    def get_job_sequence(self):
        temp_list = self.operationlist
        for operation in temp_list:
            if operation.Pj != 0:
                self.job_sequence_list.append(operation.job_number)
            
        
