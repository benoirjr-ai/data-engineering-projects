import csv


def read_batches(file_path, batch_size):
    """Read a CSV file and yield rows in batches."""
    
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        batch = []

        for row in reader:
            batch.append(row)

            # Yield a full batch once the requested size is reached.
            if len(batch) == batch_size:
                yield batch
                batch = []

        # Yield the remaining rows if the final batch is incomplete.
        if batch:
            yield batch