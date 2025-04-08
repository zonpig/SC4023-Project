import time
import multiprocessing
import numpy as np


# Function for sequential scan
def sequential_scan(column, criterion):
    return [idx for idx, value in enumerate(column) if criterion(value)]


# Worker function for multiprocessing
def worker(column_slice, criterion):
    return [idx for idx, value in enumerate(column_slice) if criterion(value)]


# Define the condition function instead of lambda
def condition(value):
    return value > 0.5


# Parallel processing function
def parallel_scan(column, criterion, num_workers):
    pool = multiprocessing.Pool(processes=num_workers)

    # Split data into chunks for each worker
    chunk_size = len(column) // num_workers
    chunks = [column[i * chunk_size : (i + 1) * chunk_size] for i in range(num_workers)]

    results = pool.starmap(worker, [(chunk, criterion) for chunk in chunks])
    pool.close()
    pool.join()

    # Adjust indices to match the full array
    offset_results = []
    for i, res in enumerate(results):
        offset_results.extend([idx + i * chunk_size for idx in res])

    return offset_results


# Benchmarking function
def benchmark():
    sizes = [10**4, 10**6, 10**8]  # Test array sizes
    num_workers = multiprocessing.cpu_count()

    print(f"Using {num_workers} CPU cores for parallel processing.\n")

    for i, size in enumerate(sizes):
        column = np.random.rand(size)  # Generate random array

        # Measure sequential processing time
        start_time = time.time()
        sequential_result = sequential_scan(column, condition)
        sequential_time = time.time() - start_time

        # Measure parallel processing time
        start_time = time.time()
        parallel_result = parallel_scan(column, condition, num_workers)
        parallel_time = time.time() - start_time

        # Print results with scientific notation
        print(
            f"Array Size: {size:.0e}"
        )  # This prints in scientific notation (e.g., 1e+04)
        print(
            f"Does Sequential Scan Result = Parallel Scan Result: {sequential_result == parallel_result}"
        )

        print(f"  Sequential Scan Time: {sequential_time:.6e} sec")
        print(f"  Parallel Scan Time:   {parallel_time:.6e} sec")

        print(
            f"  Speedup/Slowdown (Parallel/Sequential): {parallel_time / sequential_time:.2f}x\n"
        )


if __name__ == "__main__":
    benchmark()
