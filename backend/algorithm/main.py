from JobShopScheduler import JobShopScheduler
import benchmarks
import distances

def main():
    machine_data = benchmarks.ft06['machine_data']
    ptime_data = benchmarks.ft06['ptime_data']
    machine_data4 = benchmarks.pinedo['machine_data']
    ptime_data4 = benchmarks.pinedo['ptime_data']
    machine_data6 = benchmarks.ft06['machine_data']
    ptime_data6 = benchmarks.ft06['ptime_data']
    machine_data5  = benchmarks.la01['machine_data']
    ptime_data5  = benchmarks.la01['ptime_data']
    machine_data10 = benchmarks.ft10['machine_data']
    ptime_data10 = benchmarks.ft10['ptime_data']
    
    la06_data5  = benchmarks.la06['machine_data']
    la06_ptime5  = benchmarks.la06['ptime_data']
    la23_data10 = benchmarks.la23['machine_data']
    la23_ptime10 = benchmarks.la23['ptime_data']
    
    ta20_20_machine_data = benchmarks.twenty_twenty['machine_data']
    ta20_20_ptime_data = benchmarks.twenty_twenty['ptime_data']
    ta20_50_machine_data = benchmarks.twenty_fifty['machine_data']
    ta20_50_ptime_data = benchmarks.twenty_fifty['ptime_data']
    
    
    # scheduler1 = JobShopScheduler(4, 3, 2, 50, 0.7, 0.5, 100, machine_data4, ptime_data4)    
    # scheduler1.set_distance_matrix(distances.four_machine_matrix)
    
    
    scheduler1 = JobShopScheduler(6, 6, 2, 250, 0.7, 0.5, 300, machine_data6, ptime_data6)    
    scheduler1.set_distance_matrix(distances.six_machine_matrix)
    
    
    # scheduler1 = JobShopScheduler(5, 10, 3, 350, 0.7, 0.5, 450, machine_data5, ptime_data5)    
    # scheduler1 = JobShopScheduler(5, 15, 3, 350, 0.7, 0.5, 450, la06_data5, la06_ptime5)    
    # scheduler1.set_distance_matrix(distances.five_machine_matrix)
    
    
    # scheduler1 = JobShopScheduler(10, 10, 2, 350, 0.7, 0.5, 450, machine_data10, ptime_data10)    
    # scheduler1 = JobShopScheduler(10, 15, 3, 350, 0.7, 0.5, 450, la23_data10, la23_ptime10) 
    # scheduler1.set_distance_matrix(distances.ten_machine_matrix)
    
    
    # scheduler1 = JobShopScheduler(20, 20, 4, 100, 0.7, 0.5, 600, ta20_20_machine_data, ta20_20_ptime_data)    
    # scheduler1 = JobShopScheduler(20, 50, 7, 100, 0.7, 0.5, 600, ta20_50_machine_data, ta20_50_ptime_data)    
    # scheduler1.set_distance_matrix(distances.twenty_machine_matrix)
    
    
    scheduler1.runs = 1
    scheduler1.display_schedule = 1
    scheduler1.display_convergence = 0
    scheduler1.enable_travel_time = 1
    scheduler1.create_txt_file = 0
    
    scheduler1.stagnation_limit = 200
    scheduler1.activate_termination = 0
    
    print(scheduler1.operation_data)
    for _ in range(scheduler1.runs):
        chromosome1 = scheduler1.GeneticAlgorithm()
    
    # scheduler1.reschedule(2, 3)
    # chromosome2 = scheduler1.GeneticAlgorithm()
    
    print('AMR MACHINE SEQUENCES')
    print(chromosome1.amr_machine_sequences)
    print(chromosome1.amr_ptime_sequences)
    # print(chromosome2.amr_machine_sequences)
    # print(chromosome2.amr_ptime_sequences)
    
    
if __name__ == '__main__':
    main()