import random
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.stats import rankdata
import time
import os
import json

from job import Job
from machine import Machine
from operation import Operation
from chromosome import Chromosome
from datetime import datetime
from amr import AMR


import distances
import benchmarks

import traceback
import inspect


class JobShopScheduler():
    def __init__(self, m, n, num_amrs, N, pc, pm, T, machine_data, ptime_data):
        self.m = m
        self.n = n
        self.num_amrs = num_amrs
        self.N = N
        self.pc = pc
        self.pm = pm
        self.pswap = pm
        self.pinv = pm
        self.T = T
        self.machine_data = machine_data
        self.ptime_data = ptime_data
        self.stagnation_limit = 50
        
        self.activate_termination = 0
        self.enable_travel_time = 0
        self.display_convergence = 0
        self.display_schedule = 1
        self.create_txt_file = 0
        self.update_json_file = 0
        self.runs = 1
        
        self.distance_matrix = None
        self.save_file_directory = 'E:\\Python\\JobShopGA\\Results\\default'
        
        if self.enable_travel_time:
            self.distance_matrix = distances.four_machine_matrix
        else:
            self.distance_matrix = distances.empty_matrix
            
            
        self.operation_data = self.create_operation_data(self.machine_data, self.ptime_data, self.m)
        self.amr_assignments = None
        
        
    def GetUniqueFileName (self, prefix, ftype):
        timestamp = int (time.time())
        fileName = "{}_m{}_n{}_a{}_{}.{}".format (prefix, self.m, self.n, self.num_amrs, timestamp, ftype)
        return fileName
        
    # recieve number of completed jobs and reschedule the remaining jobs, also mention number of amrs present during rescheduling.
    def reschedule(self, num_completed_jobs, num_amrs):
        self.machine_data = self.machine_data[num_completed_jobs * self.m:]
        self.ptime_data = self.ptime_data[num_completed_jobs * self.m:]
        self.operation_data = self.create_operation_data(self.machine_data, self.ptime_data, self.m)
        self.n = self.n - num_completed_jobs
        self.num_amrs = num_amrs
        
        
        
    def set_distance_matrix(self, matrix):
        self.distance_matrix = matrix
                    
            
    def create_operation_data(self, machine_data, ptime_data, m):
        matrix = []
        sublist = []
        for i in range(len(machine_data)):
            sublist.append([machine_data[i], ptime_data[i]])
            if (i + 1) % m == 0:
                matrix.append(sublist)
                sublist = []
        # Check if there are remaining elements
        if sublist:
            matrix.append(sublist)
        
        return matrix
    
    def assign_operations(self, jobs, operation_data):
        for job, operation in zip(jobs, operation_data):
            job.operations = operation
    
    def generate_population(self, N):
        population = []
        for _ in range(N):
            num = [round(random.uniform(0,self.m*self.n), 2) for _ in range(self.n*self.m)]
            population.append(num)
        return population    
    
    
    def integer_list(self, population):
        ranked_population = []
        for i in range(self.N):
            sorted_list = []
            ranks = {}
            # Sort the list to get ranks in ascending order
            sorted_list = sorted(population[i])
                
            # Create a dictionary to store the ranks of each float number
            ranks = {value: index + 1 for index, value in enumerate(sorted_list)}
                
            # Convert each float number to its corresponding rank
            rank_list = [ranks[value] for value in population[i]]
            ranked_population.append(rank_list)
            
        return ranked_population    
    
    def indiv_integer_list(self, chromosome):    
        ranks = rankdata(chromosome)
        return [int(rank - 1) for rank in ranks]
    
    def remove_duplicates(self, numbers):
        seen = set()
        modified_numbers = []
        
        for num in numbers:
            # Check if the number is already in the set
            if num in seen:
                # Modify the number slightly
                modified_num = num + 0.01
                # Keep modifying until it's unique
                while modified_num in seen:
                    modified_num += 0.01
                modified_numbers.append(modified_num)
                seen.add(modified_num)
            else:
                modified_numbers.append(num)
                seen.add(num)
            
        
        return modified_numbers    
    
    def getJobindex(self, population):
        new_index = 0
        operation_index_pop = []
        for i in range(self.N):
            tlist = []
            temp = population[i]
            for j in range(self.m*self.n):
                new_index = (temp[j] % self.n) + 1
                tlist.append(new_index)
            operation_index_pop.append(tlist)
        
        return operation_index_pop
    
    def indiv_getJobindex(self, chromosome):
        new_index = 0
        operation_index_pop = []

        tlist = []
        temp = chromosome
        for j in range(len(chromosome)):
            new_index = (temp[j] % self.n)
            tlist.append(new_index)
        operation_index_pop = tlist
        
        return operation_index_pop
    
    
    def indiv_schedule_operations(self, chromosome, jobs):
        operation_list = []
        explored = []

        for i in range(len(chromosome)):
            explored.append(chromosome[i])
            numcount = explored.count(chromosome[i])

            operation_list.append(jobs[chromosome[i]].operations[numcount-1])  # changed chromosome[i] to chromosome[i]-1
        return operation_list

    def install_operations(self, jobs):
        for job in jobs:
            job.operations = [Operation(job.job_number) for i in range(self.m)]

    # operation_data = create_operation_data(machine_data,ptime_data, m)

    def assign_data_to_operations(self, jobs, operation_data):
        for job,sublist in zip(jobs, operation_data):
            for operation,i in zip(job.operations, range(self.m)):
                operation.operation_number = i
                operation.machine = sublist[i][0]
                operation.Pj = sublist[i][1]
    
    def assign_amrs_to_jobs(self, jobs, amrs, amr_assignments):
        for job, amr_num in zip(jobs, amr_assignments):
            job.amr_number = amr_num
            amrs[job.amr_number].assigned_jobs.append(job.job_number)
            amrs[job.amr_number].job_sequence.append(job.job_number)
            
            
    def get_amr_assignments(self):
        amr_assignments = []
        for num in range(self.n):
            amr_num = random.randint(0, self.num_amrs - 1)
            amr_assignments.append(amr_num)
            
        return amr_assignments
                
                
    def get_machine_sequence(self, operation_schedule):
        machine_sequence = []
        for operation in operation_schedule:
            machine_sequence.append(operation.machine)
            
        return machine_sequence

    def get_processing_times(self, operation_schedule):
        ptime_sequence = []
        for operation in operation_schedule:
            ptime_sequence.append(operation.Pj)
            
        return ptime_sequence
    
    def calculate_Cj_with_amr(self, operation_schedule, machines, jobs, amrs):
        t_op = operation_schedule
        skipped = []
        while t_op != []:
            # print('running')
            
            for operation in t_op:
                # CHECK IF AMR IS ASSIGNED TO A JOB, ONLY ASSIGN IF THE OPERATION NUMBER IS ZERO
                if amrs[jobs[operation.job_number].amr_number].current_job == None and operation.operation_number == 0:
                    amrs[jobs[operation.job_number].amr_number].current_job = operation.job_number
                    amrs[jobs[operation.job_number].amr_number].job_objects.append(jobs[operation.job_number]) # APPEND JOB OBJECTS
                    # IF AMR JUST COMPLETED A JOB UPDATE THE NEXT JOBS MACHINE START TO THE TIME WHEN AMR COMPLETED PREVIOUS JOB
                    if machines[operation.machine].finish_operation_time < amrs[jobs[operation.job_number].amr_number].job_completion_time:
                        machines[operation.machine].finish_operation_time = amrs[jobs[operation.job_number].amr_number].job_completion_time
                    
                    
                # CHECK IF AMR IS CURRENTLY PROCESSING THIS JOB
                if operation.job_number == amrs[jobs[operation.job_number].amr_number].current_job:
                    
                    if operation.operation_number == 0:
                        if amrs[jobs[operation.job_number].amr_number].completed_jobs == []:
                            # THE AMR MUST TRAVEL TO FIRST MACHINE BEFORE PROCESSING FIRST OPERATION
                            initial_travel_time = operation.calculate_travel_time(amrs, jobs, self.distance_matrix, self.enable_travel_time, 1)
                            if machines[operation.machine].finish_operation_time > initial_travel_time:
                                operation.start_time = machines[operation.machine].finish_operation_time
                            else:
                                operation.start_time = machines[operation.machine].finish_operation_time + initial_travel_time
                        else:
                            # MAKE SURE THE PREVIOUS JOBS TRAVEL TIME SHOULD BE GIVEN TO NEXT JOB IF M'TH JOB IS HAVING PJ = 0
                            i = 0
                            while jobs[amrs[jobs[operation.job_number].amr_number].completed_jobs[-1]].operations[self.m-i-1].Pj == 0:
                                i+=1   
                            operation.start_time = machines[operation.machine].finish_operation_time + jobs[amrs[jobs[operation.job_number].amr_number].completed_jobs[-1]].operations[self.m-i-1].travel_time
                            
                        jobs[operation.job_number].job_start_time = operation.start_time # SET JOB START TIME
                        operation.Cj = operation.start_time + operation.Pj
                        machines[operation.machine].finish_operation_time = operation.Cj
                        # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
                        
                        
                    else:
                        # IF MACHINE RUN TIME IS LESSER THAN JOB COMPLETION TIME AND TRAVEL TIME FROM PREVIOUS LOCATION COMBINED.
                        if jobs[operation.job_number].operations[operation.operation_number - 1].Cj + jobs[operation.job_number].operations[operation.operation_number - 1].travel_time < machines[operation.machine].  finish_operation_time:
                            operation.start_time = machines[operation.machine].finish_operation_time
                            operation.Cj = operation.start_time + operation.Pj
                            machines[operation.machine].finish_operation_time = operation.Cj 
                            # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
                            
                        else:
                            operation.start_time = jobs[operation.job_number].operations[operation.operation_number - 1].Cj + jobs[operation.job_number].operations[operation.operation_number - 1].travel_time
                            operation.Cj = operation.start_time + operation.Pj
                            if operation.Pj != 0:
                                machines[operation.machine].finish_operation_time = operation.Cj
                            # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
                    
                
                # SKIP THE JOB AND RETURN TO IT LATER
                else:
                    skipped.append(operation)
                
                # UPDATE PARAMETERS ONCE A JOB IS COMPLETED
                if operation.operation_number == self.m - 1 and amrs[jobs[operation.job_number].amr_number].current_job == operation.job_number:
                            amrs[jobs[operation.job_number].amr_number].current_job = None
                            if amrs[jobs[operation.job_number].amr_number].assigned_jobs != []:
                                amrs[jobs[operation.job_number].amr_number].assigned_jobs.remove(operation.job_number)
                            amrs[jobs[operation.job_number].amr_number].completed_jobs.append(operation.job_number)
                            # IF FINAL JOB PJ IS ZERO TAKE PREV COMPLETED TIME
                            if operation.Pj != 0:
                                amrs[jobs[operation.job_number].amr_number].job_completion_time = operation.Cj
                                jobs[operation.job_number].job_completion_time = amrs[jobs[operation.job_number].amr_number].job_completion_time
                            else:
                                i = 0
                                while jobs[operation.job_number].operations[operation.operation_number - i].Pj == 0:
                                    i += 1
                                amrs[jobs[operation.job_number].amr_number].job_completion_time = jobs[operation.job_number].operations[operation.operation_number -  i].Cj
                            jobs[operation.job_number].job_completion_time = amrs[jobs[operation.job_number].amr_number].job_completion_time
                    
            t_op = skipped
            skipped = []
        # eof while    
 
    def assign_machine_operationlist(self, machines, operation_schedule):
        for operation in operation_schedule:
            machines[operation.machine].operationlist.append(operation)

    def get_Cmax(self, machines):
        runtimes = []
        for machine in machines:
            runtimes.append(machine.finish_operation_time)
            
        return max(runtimes) 
    
    def get_travel_time(self, jobs, amrs, distance_matrix):
        for job in jobs:
            for operation in job.operations:
                operation.travel_time = operation.calculate_travel_time(amrs, jobs, distance_matrix, self.enable_travel_time)
                
    def process_chromosome(self, chromosome, amr_assignments):
        
        # print(operation_data)
        jobs = [Job(number, self.n) for number in range(self.n)]
        machines = [Machine(number, self.m) for number in range(self.m)]
        amrs = [AMR(number) for number in range(self.num_amrs)]
        self.assign_operations(jobs, self.operation_data)
        
        chromosome = self.remove_duplicates(chromosome)
        # print(chromosome)
        ranked_list = self.indiv_integer_list(chromosome)
        # print(ranked_list)
        operation_index_list = self.indiv_getJobindex(ranked_list)
        
        # CASE 1
        # operation_index_list = [1, 2, 0, 1, 2, 0, 2, 0, 1, 0, 2, 1]
        
        
        self.install_operations(jobs)
        self.assign_data_to_operations(jobs, self.operation_data)
        # check_list_length(operation_index_list)
        
        operation_schedule = self.indiv_schedule_operations(operation_index_list, jobs)    # HERE IS THE MF ERROR
        # check_list_length(operation_schedule)
        self.assign_amrs_to_jobs(jobs, amrs, amr_assignments)
        
        # get the sequence of machines
        machine_sequence = self.get_machine_sequence(operation_schedule)
        
        # get the sequence of processing times
        ptime_sequence = self.get_processing_times(operation_schedule)
        
        # SET TRAVEL TIMES FOR EACH JOB
        self.get_travel_time(jobs, amrs, self.distance_matrix)
        
        # calculate_Cj(operation_schedule, machines, jobs)
        self.calculate_Cj_with_amr(operation_schedule, machines, jobs, amrs)
        self.assign_machine_operationlist(machines, operation_schedule)
        Cmax = self.get_Cmax(machines)
        
        chromosome = Chromosome(chromosome)
            
        chromosome.ranked_list = ranked_list
        chromosome.operation_index_list = operation_index_list
        chromosome.job_list = jobs
        chromosome.amr_list = amrs
        chromosome.operation_schedule = operation_schedule
        chromosome.machine_sequence = machine_sequence
        chromosome.machine_list = machines
        chromosome.ptime_sequence = ptime_sequence
        chromosome.Cmax = round(Cmax, 0)
        chromosome.fitness = chromosome.Cmax + chromosome.penalty
        
        return chromosome
    
    def PlotGanttChar_with_amr(self, chromosome):

        # Get the makespan (Cmax) from the chromosome
        Cmax = chromosome.Cmax

        # Figure and set of subplots
        fig, axs = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [8, 1]})
        
        # Bottom Gantt chart (main)
        ax = axs[0]
        ax.set_ylabel('Machine', fontweight='bold', loc='top', color='magenta', fontsize=16)
        ax.set_ylim(-0.5, self.m - 0.5)
        ax.set_yticks(range(self.m), minor=False)
        ax.set_yticklabels(range(1, self.m + 1), minor=False)
        ax.tick_params(axis='y', labelcolor='magenta', labelsize=16)
        
        ax.set_xlim(0, Cmax + 2)
        ax.tick_params(axis='x', labelcolor='red', labelsize=16)
        ax.grid(True)

        tmpTitle = f'Job Shop Scheduling (m={self.m}; n={self.n}; AMRs:{self.num_amrs}; Cmax={round(Cmax, 2)}; )'
        ax.set_title(tmpTitle, size=20, color='blue')

        colors = ['orange', 'deepskyblue', 'indianred', 'limegreen', 'slateblue', 'gold', 'violet', 'grey', 'red', 'magenta', 'blue', 'green', 'silver', 'lavender', 'turquoise', 'orchid', 'yellow', 'pink', 'purple', 'brown', 'cyan']

        for i in range(self.m):
            joblen = len(chromosome.machine_list[i].operationlist)
            for k in range(joblen):
                j = chromosome.machine_list[i].operationlist[k]
                ST = j.start_time
                if j.Pj != 0:
                    ax.broken_barh([(ST, j.Pj)], (-0.3 + i, 0.6), facecolor=colors[j.job_number % len(colors)], linewidth=1, edgecolor='black')
                    ax.broken_barh([(j.Cj, j.travel_time)], (-0.3 + i, 0.6), facecolor='black', linewidth=1, edgecolor='black')
                    
                    ax.text(ST + (j.Pj / 2 - 0.3), i + 0.03, '{}'.format(j.job_number + 1), fontsize=18)
        
        # Top Gantt chart with custom y-ticks
        top_ax = axs[1]
        top_ax.set_ylabel('AMRs', fontweight='bold', loc='top', color='magenta', fontsize=16)
        top_ax.set_xlabel('Time', fontweight='bold', loc='right', color='red', fontsize=16)
        top_ax.set_ylim(-0.5, self.num_amrs - 0.5)
        top_ax.set_yticks(range(self.num_amrs), minor=False)
        top_ax.set_yticklabels(range(1, self.num_amrs + 1), minor=False)  # Corrected y-tick labels for AMRs
        top_ax.tick_params(axis='y', labelcolor='magenta', labelsize=16)
        top_ax.set_xlim(0, Cmax + 2)
        top_ax.tick_params(axis='x', labelcolor='red', labelsize=16)
        top_ax.grid(True)

        # Plot the AMR jobs
        top_colors = ['orange', 'deepskyblue', 'indianred', 'limegreen', 'slateblue', 'gold', 'violet', 'grey', 'red', 'magenta', 'blue', 'green', 'silver', 'lavender', 'turquoise', 'orchid', 'yellow', 'pink', 'purple', 'brown', 'cyan']

        for i in range(self.num_amrs):
            joblen = len(chromosome.amr_list[i].job_objects)
            for k in range(joblen):
                j = chromosome.amr_list[i].job_objects[k]
                ST = j.job_start_time
                duration = j.job_completion_time - j.job_start_time
                if duration != 0:
                    top_ax.broken_barh([(ST, duration)], (-0.3 + i, 0.6), facecolor=top_colors[j.job_number % len(top_colors)], linewidth=1, edgecolor='black')
                    top_ax.text(ST + (duration) / 2 , i - 0.2, '{}'.format(j.job_number + 1), fontsize=14, ha='center')

        plt.tight_layout()
        
        if self.create_txt_file:
            # CHANGE DIRECTORY FOR SAVING FIGURE
            
            folder_name = "run results"
        
            # Check if the folder exists,   if not, create it
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
                
                
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = os.path.join(folder_name, self.GetUniqueFileName("GA", "png"))
            
            plt.savefig(filename)
        

    def tournament(self, population):
        indices2 = [x for x in range(self.N)]
        
        winners = []
        while len(indices2) != 0:
            i1 = random.choice(indices2)
            i2 = random.choice(indices2)
            while i1 == i2:
                i2 = random.choice(indices2)
                
            if population[i1].fitness < population[i2].fitness:
                winners.append(population[i1])
            else:
                winners.append(population[i2])
                
            indices2.remove(i1)
            indices2.remove(i2)
        
        indices2 = [x for x in range(self.N)]
        
        while len(indices2) != 0:
            i1 = random.choice(indices2)
            i2 = random.choice(indices2)
            while i1 == i2:
                i2 = random.choice(indices2)
                
            if population[i1].fitness < population[i2].fitness:
                winners.append(population[i1])
            else:
                winners.append(population[i2])
                
            indices2.remove(i1)
            indices2.remove(i2)
            
        return winners
    

    def stochastic_universal_sampling(self, population, num_parents):
        # Calculate inverted fitness values
        max_fitness = max(chromosome.fitness for chromosome in population)
        inverted_fitness = [max_fitness - chromosome.fitness for chromosome in population]

        # Calculate total inverted fitness
        total_inverted_fitness = sum(inverted_fitness)

        # Calculate distance between selection pointers
        pointer_distance = total_inverted_fitness / num_parents

        # Randomly choose a starting point for the selection pointers
        start_point = random.uniform(0, pointer_distance)

        # Create selection pointers
        pointers = [start_point + i * pointer_distance for i in range(num_parents)]

        # Initialize selected individuals list
        selected_individuals = []

        # Iterate over selection pointers and select individuals
        cumulative_fitness = 0
        idx = 0
        for pointer in pointers:
            while cumulative_fitness < pointer:
                cumulative_fitness += inverted_fitness[idx]
                idx += 1
            selected_individuals.append(population[idx])

        return selected_individuals
    
    def single_point_crossover(self, chrom1, chrom2, amr_assignments):
        
        parent1 = chrom1.encoded_list
        parent2 = chrom2.encoded_list
        
        r = random.uniform(0,1)
        # r = 0.4
        
        p = random.randint(0,len(parent1))
        if r > self.pc:
            return chrom1 , chrom2
        else:
            offspring1 = parent1[0:p] + parent2[p:]
            offspring2 = parent2[0:p] + parent1[p:]
            # checked_offsp1 = remove_duplicates(offspring1)[:]
            # checked_offsp2 = remove_duplicates(offspring2)[:]
            chrom_out1 = self.process_chromosome(offspring1, amr_assignments)
            chrom_out2 = self.process_chromosome(offspring2, amr_assignments)
        
        return chrom_out1, chrom_out2   
    
    def single_bit_mutation(self, chromosome, amr_assignments):
        
        r = random.uniform(0,1)
        code = chromosome.encoded_list[:]
        
        if r > self.pm:
            return chromosome
        else:
            index = random.randint(0, len(code) - 1)
            code[index] = round(random.uniform(0,self.m*self.n), 2)
            # checked_code = remove_duplicates(code)[:]
            mutated_chromosome = self.process_chromosome(code, amr_assignments)
        
        return mutated_chromosome 
    
    def next_gen_selection(self, parents, offsprings):
        total_population = []
        total_population.extend(parents)
        total_population.extend(offsprings)
        
        sortedGen = []
        sortedGen = sorted(total_population, key = lambda x : x.fitness)
        return sortedGen[:self.N], sortedGen[0]
    
    def swapping(self, chromosome, amr_assignments):
        r = random.uniform(0,1)
        if r >self.pswap:
            return chromosome
        
        code = chromosome.encoded_list[:]
        indexes = [num for num in range(len(code))]
        
        p = random.choice(indexes)
        q = random.choice(indexes)
        while p == q:
            q = random.choice(indexes)
            
        code[p], code[q] = code[q], code[p]
        
        swapped_chromosome = self.process_chromosome(code, amr_assignments)
        return swapped_chromosome
        
    def inversion(self, chromosome, amr_assignments):
        
        r = random.uniform(0,1)
        if r > self.pinv:
            return chromosome
        
        code = chromosome.encoded_list[:]
        indexes = [num for num in range(len(code))]
        p = random.choice(indexes)
        q = random.choice(indexes)
        while p == q:
            q = random.choice(indexes)
            
        
        p, q = min(p, q), max(p, q)
        code[p:q+1] = reversed(code[p:q+1])
        
        inverted_chromosome = self.process_chromosome(code, amr_assignments)
        
        return inverted_chromosome
    
    def SPT_heuristic(self, operation_data):
        operation_index_list = []
        n = len(operation_data[0])  # Number of operations
        m = len(operation_data)     # Number of jobs

        for j in range(n):
            tlist = [(i, operation_data[i][j]) for i in range(m)]
            tlist.sort(key=lambda x: x[1][1])  # Sort based on processing time
            operation_index_list.extend([t[0] for t in tlist])

        return operation_index_list

    def LPT_heuristic(self, operation_data):
        operation_index_list = []
        n = len(operation_data[0])  # Number of operations
        m = len(operation_data)     # Number of jobs

        for j in range(n):
            tlist = [(i, operation_data[i][j]) for i in range(m)]
            tlist.sort(key=lambda x: x[1][1], reverse=True)  # Sort based on processing time
            operation_index_list.extend([t[0] for t in tlist])
            
        return operation_index_list

    def srt_heuristic(self, operation_data):
        rem_time = 0
        job_rem_time = []
        operation_index_list = []
        
        for i in range(self.m):
            job_rem_time = []
            for job in operation_data:
                rem_time = 0
                tjob = job[i:]
                for operation in tjob:
                    rem_time += operation[1]
                job_rem_time.append(rem_time)
            sorted_indices = sorted(range(len(job_rem_time)), key=lambda x: job_rem_time[x])
            operation_index_list.extend(sorted_indices)
        return operation_index_list

    def decode_operations_to_schedule(self, operation_index, num_jobs):
        n = len(operation_index)
        possible_indices = [[(num_jobs * j + op) for j in range(n // num_jobs + 1)] for op in operation_index]
        ranked_list = [0] * n
        used_indices = set()
        is_valid = True
        for i, options in enumerate(possible_indices):
            # Find the smallest available index that hasn't been used yet
            for option in sorted(options):
                if option not in used_indices and option < n:
                    ranked_list[i] = option
                    used_indices.add(option)
                    break
            else:
                # If no valid option is found, note that configuration may be invalid
                is_valid = False
                break

        if not is_valid:
            return None, None  # Indicate that no valid configuration was found
        
        random_numbers = [0] * n
        index_to_number = {rank: i for i, rank in enumerate(ranked_list)}
        for i in range(n):
            random_numbers[index_to_number[i]] = i + 1  # Simple 1-to-n mapping for simplicity

        return ranked_list, random_numbers
    
    def generate_population_with_heuristic(self, operation_data, amr_assignments):
        n = self.n
        m = self.m
        N = self.N
        population = []
        number = n*m
        
        if N > 6:
        
            for i in range(2):
                srt_op_seq = self.srt_heuristic(operation_data)
                ranked, code = self.decode_operations_to_schedule(srt_op_seq, n)
                population.append(self.process_chromosome(code, amr_assignments))
            
            for i in range(2):
                spt_op_seq = self.SPT_heuristic(operation_data)
                ranked, code = self.decode_operations_to_schedule(spt_op_seq, n)
                population.append(self.process_chromosome(code, amr_assignments))
                
                
            for i in range(2):
                lpt_op_seq = self.LPT_heuristic(operation_data)
                ranked, code = self.decode_operations_to_schedule(lpt_op_seq, n)
                population.append(self.process_chromosome(code, amr_assignments))
            
            for i in range(N - 6):
                num = [round(random.uniform(0,m*n), 2) for _ in range(n*m)]
                population.append(self.process_chromosome(num, amr_assignments))
            
        else:
            initial_population = self.generate_population(N)
            population = []
            for encoded_list in initial_population:
                # print(f'generated list: {encoded_list}')
                chromosome = self.process_chromosome(encoded_list, amr_assignments)
                population.append(chromosome)
            
        return population

    def get_sequences_in_amr(self, amrs):
        amr_machines = []
        amr_ptimes = []
        glob_amr_machine = []
        glob_amr_ptime = []
        for amr in amrs:
            for j in amr.job_objects:
                for o in j.operations:
                    amr_machines.append(o.machine)
                    amr_ptimes.append(o.Pj)
                amr_machines.extend([-2, -1])
                amr_ptimes.extend([3, 3])
            amr.machine_sequence = amr_machines
            amr.ptime_sequence = amr_ptimes
            glob_amr_machine.append(amr_machines)
            glob_amr_ptime.append(amr_ptimes)
            amr_machines = []
            amr_ptimes = []
            
        return glob_amr_machine, glob_amr_ptime
    
    def create_amr_json(self, machine_sequences, ptime_sequences, output_file):
        # Initialize the structure
        amr_data = {
            "amr_list": [
                {
                    "amr_no": 1,
                    "machine_sequence": machine_sequences[0],
                    "ptime_sequence": ptime_sequences[0]
                },
                {
                    "amr_no": 2,
                    "machine_sequence": machine_sequences[1],
                    "ptime_sequence": ptime_sequences[1]
                }
            ]
        }

        # Write the data to a JSON file
        with open(output_file, 'w') as json_file:
            json.dump(amr_data, json_file, indent=4)
            
    def generate_population(self, N):
        population = []
        for _ in range(N):
            num = [round(random.uniform(0,self.m*self.n), 2) for _ in range(self.n*self.m)]
            population.append(num)
        return population
            
    def get_file(self, best_chromosome, processing_time, converged_at, xpoints, ypoints):
        # Generate timestamp for filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = self.GetUniqueFileName("GA", "txt")
        
        if converged_at == 0:
            converged_at = processing_time

        # Define the folder name
        directory = "run results"  # Folder for saving the file

        # Check if folder exists, create if necessary
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Construct the full file path
        filepath = os.path.join(directory, filename)

        # Write the contents to the file
        with open(filepath, 'w') as file:
            file.write(f"Welcome to main function at {datetime.now().strftime('%d-%m %H:%M:%S')}.{datetime.now().microsecond}\n")
            file.write(f"Population size: {self.N}\n")
            file.write(f"Number of generations: {self.T}\n")
            file.write(f"Number of AMRs: {self.num_amrs}\n")
            file.write(f"Encoded list: {best_chromosome.encoded_list}\n")
            file.write(f"Ranked list: {best_chromosome.ranked_list}\n")
            file.write(f"Operation_index list: {best_chromosome.operation_index_list}\n")
            file.write(f"Machine sequence: {best_chromosome.machine_sequence}\n")
            file.write(f"Ptime sequence: {best_chromosome.ptime_sequence}\n\n")
            
            file.write(f"AMR machine sequences: {best_chromosome.amr_machine_sequences}\n")
            file.write(f"AMR ptime sequences: {best_chromosome.amr_ptime_sequences}\n")
            
            file.write(f"Makespan is {best_chromosome.Cmax} time units\n")
            file.write(f"Fitness is {best_chromosome.fitness} \n")
            file.write(f"Problem solved in {round(processing_time, 2)} seconds\n\n")
            
            file.write("----------------------------------------------------------------------------------------------\n")
            file.write("n \t m\t a\t T \t N \t Pc \t Pm \t Cmax \t CPU Time (s) \t Termination value\n")
            file.write("----------------------------------------------------------------------------------------------\n")
            file.write(f" {self.n} \t {self.m} \t {self.num_amrs} \t {self.T} \t {self.N} \t {self.pc} \t {self.pm}  \t {best_chromosome.Cmax} \t {round(processing_time, 2)} \t {self.stagnation_limit} \n")
            file.write("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
            
            for i, j in zip(xpoints, ypoints):
                file.write(f'{i} \t {j} \n')

    def GeneticAlgorithm(self):
    
        # Record the start time
        start_time = time.time()
        flag = 0
        count = 0
        t = 0
        ypoints = []
        
        
        self.amr_assignments = self.get_amr_assignments()
        # generate initial population
        
        
        # RANDOM BUG HEURISTIC NOT WORKING WHEN MACHINES ARE 20
        if self.m == 20:
            initial_population = self.generate_population(self.N)
            population = []
            for encoded_list in initial_population:
                # print(f'generated list: {encoded_list}')
                chromosome = self.process_chromosome(encoded_list, self.amr_assignments)
                population.append(chromosome)
        else:
            population = self.generate_population_with_heuristic(self.operation_data, self.amr_assignments)
            
        sorted_population = sorted(population, key = lambda  x : x.fitness )
            
        best_chromosome = sorted_population[0]
        
        # TERMINATION CONDITION
        history = 0
        stagnation = 0
        
            
        # start generations
        while t < self.T:
            
            new_amr_assignments = self.get_amr_assignments()
            
            # create mating pool
            winners_list = self.tournament(population)
            # winners_list = three_way_tournament(population)
            
            
            
            # perform crossover on mating pool
            indices = [x for x in range(self.N)]
            offspring_list = winners_list
            while len(indices) != 0:
                i1 = random.choice(indices)
                i2 = random.choice(indices)
                while i1 == i2:
                    i2 = random.choice(indices)
                    
                rchoice = random.uniform(0,1)
                if rchoice < 1:
                    offspring1, offspring2 = self.single_point_crossover(winners_list[i1], winners_list[i2], new_amr_assignments)
                else:
                    # potential bug, skipping job
                    offspring1, offspring2 = self.double_point_crossover(winners_list[i1], winners_list[i2], new_amr_assignments)
                offspring_list[i1] = offspring1
                offspring_list[i2] = offspring2
                
                indices.remove(i1)
                indices.remove(i2)
                
            # perform mutation
            enhanced_list = []
            for chromosome in offspring_list:
                mutated_chromosome = self.single_bit_mutation(chromosome, new_amr_assignments)
                
                # perform swapping operation
                swap_chromosome = self.swapping(mutated_chromosome, new_amr_assignments)
                
                if swap_chromosome.Cmax < mutated_chromosome.Cmax:
                    enhanced_list.append(swap_chromosome)
                    inverted_chromosome = self.inversion(swap_chromosome, new_amr_assignments)
                    if inverted_chromosome.Cmax < swap_chromosome.Cmax:
                        enhanced_list.append(inverted_chromosome)
                    else:
                        enhanced_list.append(swap_chromosome)
                else:    
                    enhanced_list.append(mutated_chromosome)
            
                # # perform inversion operation on chromosome
                # inverted_chromosome = inversion(swap_chromosome, new_amr_assignments)
                
                # enhanced_list.append(mutated_chromosome)
                
                # # selection of survivors for next generation
            
            survivors, best_in_gen = self.next_gen_selection(winners_list, enhanced_list)
            
            survivors[-1] = best_in_gen
            if best_in_gen.fitness < best_chromosome.fitness:
                best_chromosome = best_in_gen
                amr_assignments = new_amr_assignments
                
            if best_chromosome.fitness == history and self.activate_termination == 1:
                stagnation += 1
            else:
                stagnation = 0
                           
            if stagnation > self.stagnation_limit:
                elapsed = time.time() - start_time
                converged_at = elapsed
                break
            else:
                converged_at = 0
            
            #CHECK IF AMR ASSIGNMENT IS BETTER OR WORSE
            
            history = best_chromosome.fitness
                
            ypoints.append(best_chromosome.fitness)
            winners_list = survivors
            
            if (t + 1) % 25 == 0:
                print(f'At generation {t + 1}, best fitness :{best_chromosome.fitness}')
            
            
            
            t += 1
            # end of loop
            
        
        
        
        xpoints = [x for x in range(1, t+ 1)]
        
        if self.display_convergence:
            plt.plot(xpoints, ypoints,  color= 'b')
        
        # Record the end time
        end_time = time.time()
        processing_time = end_time - start_time
        
        machine_seq_amrs, ptime_seq_amrs = self.get_sequences_in_amr(best_chromosome.amr_list)
        print(machine_seq_amrs,'\n',ptime_seq_amrs)   


        # Update the job sequence list for each machine for best chromosome.
        for machine in best_chromosome.machine_list:
            machine.get_job_sequence()
        
        if self.update_json_file:
            self.create_amr_json(machine_seq_amrs, ptime_seq_amrs, 'amr_data.json')

        best_chromosome.amr_machine_sequences = machine_seq_amrs
        best_chromosome.amr_ptime_sequences = ptime_seq_amrs
        
        
        if self.create_txt_file:
            self.get_file(best_chromosome, processing_time, converged_at, xpoints, ypoints)
        
        
        # print(f'best Cmax = {ypoints[N-1]}')
        print(f'best Cmax = {best_chromosome.fitness}')
        
        print('random generated numbers:',best_chromosome.encoded_list)
        print(f'ranked list : {best_chromosome.ranked_list}\n operation_index :{best_chromosome.operation_index_list},\n operation object{best_chromosome.operation_schedule}\n')
        print(f'machine sequence: {best_chromosome.machine_sequence}\n ptime sequence: {best_chromosome.ptime_sequence}\n Cmax: {best_chromosome.Cmax}')



        self.PlotGanttChar_with_amr(best_chromosome)
        
        
        if self.display_schedule:
            plt.show()
        else:
            plt.close()
        
        
        return best_chromosome


if __name__ == '__main__':
    pass