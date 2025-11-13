"""Helper utility functions for the scheduler application."""

def chromosome_to_dict(chromo_obj):
    """
    Convert a Chromosome object to a dictionary for JSON serialization.
    
    Args:
        chromo_obj: Chromosome object from the algorithm
        
    Returns:
        dict: Dictionary representation of the chromosome
    """
    return {
        "encoded_list": chromo_obj.encoded_list,
        "ranked_list": chromo_obj.ranked_list,
        "operation_index_list": chromo_obj.operation_index_list,
        # "job_list": chromo_obj.job_list,
        # "amr_list": chromo_obj.amr_list,
        # "operation_schedule": chromo_obj.operation_schedule,
        "machine_sequence": chromo_obj.machine_sequence,
        # "machine_list": chromo_obj.machine_list,
        "ptime_sequence": chromo_obj.ptime_sequence,
        "Cmax": chromo_obj.Cmax,
        "penalty": chromo_obj.penalty,
        "fitness": chromo_obj.fitness,
        "amr_machine_sequences": chromo_obj.amr_machine_sequences,
        "amr_ptime_sequences": chromo_obj.amr_ptime_sequences
    }

