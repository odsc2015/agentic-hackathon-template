memory_log = []

def store_memory(claim, verification):
    memory_log.append({"claim": claim, "verification": verification})

def get_memory():
    return memory_log[-5:]  # Last 5 for timeline