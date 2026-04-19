def lru(pages, capacity):
    memory = []
    page_faults = 0
    history = []

    for i in range(len(pages)):
        if pages[i] not in memory:
            if len(memory) < capacity:
                memory.append(pages[i])
            else:
                # find least recently used
                least_used = min(memory, key=lambda x: pages[:i][::-1].index(x))
                memory.remove(least_used)
                memory.append(pages[i])
            page_faults += 1

        history.append(memory.copy())

    return page_faults, history