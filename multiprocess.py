import operator
import multiprocessing
import numpy as np

def worker(column, indices, criterions, prev_matched_idxs=None):
    '''
    This function should handle the multiprocessing of each sliced part of the array.
    Args:
        column_data: data of the column to be scaneed
        indices: list, [[start_idx1,end_idx1],[start_idx2,end_idx2], ...] if use zone_map else None
        criterions: dict, criteria to check values against
    '''  

    matched_idxs = []
    if prev_matched_idxs is not None:
        prev_matched_idxs = set(prev_matched_idxs)
    
    # NOTE: we first iterate across each indices range
    for start_idx, end_idx in indices:
        # NOTE: we iterate over each idx in each range
        for idx in range(start_idx,end_idx):
            
            # if this index has been previously filtered out
            if (prev_matched_idxs is None) or (prev_matched_idxs is not None and idx in prev_matched_idxs):
                
                matched = True
                # Check AND conditions (all conditions must be true)
                if "and" in criterions:
                    if not all(opt(column[idx], value) for opt, value in criterions["and"]):
                        matched = False
                # Check OR conditions (at least one condition must be true)
                if "or" in criterions:
                    if not any(opt(column[idx], value) for opt, value in criterions["or"]):
                        matched = False
                # Handle case for single condition (no need for all() or any())
                if "uni" in criterions:
                    if not all(opt(column[idx], value) for opt, value in criterions["uni"]):
                        matched = False
                if matched:
                    matched_idxs.append(idx)

    return matched_idxs

def parallel_processing(column,
                        all_indices=None,
                        matched_idxs=None,
                        criterions={}):

    '''
    This function should split the columns into number of splits equal to the number of workers
    
    Args:
        column: list of column values to be scanned
        all_indices:
            list, [[start_idx1,end_idx1],[start_idx2,end_idx2], ...] if use zone_map else None
            if None, split the columns into the number of zones where number of zones = number of cpu cores
        matched_idxs:
            list [idx1,idx2,...] else None
            this would be None if this is the first column that is being processed
        criterions: dict, with key being the key for the operator and value being the comparison value
        e.g., {
            "eq": "==",
            "lt": 60,
            "le": 60,
            "gt": 80,
            "ge": 80
        }
        where eq means equals, lt means <, le means <=, gt means >, ge means >=
    '''

    # Split the column up into number of vectors == number of cpus
    # NOTE: indices is a list of ranges of indexes to be split across the workers
    num_workers = multiprocessing.cpu_count()
    if all_indices is None:
        all_indices = [(arr[0], arr[-1]+1) for arr in np.array_split(np.arange(len(column)), num_workers)]
    # run multiple processes simultaneously
    pool = multiprocessing.Pool(processes=num_workers)
    
    # split job across workers
    indices_per_worker = len(all_indices)//num_workers
    worker_indices = [all_indices[(indices_per_worker*i):min(indices_per_worker*(i+1), len(all_indices))] for i in range(num_workers)]
    results = pool.starmap(worker, [(column, indices, criterions, matched_idxs) for indices in worker_indices])

    # combine the results from each vector
    combined_results = [item for sublist in results for item in sublist]
    return combined_results