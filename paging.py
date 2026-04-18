def fifo_paging(pages, capacity):
    memory = []
    page_faults = 0
    history = []

    for page in pages:
        if page not in memory:
            if len(memory) < capacity:
                memory.append(page)
            else:
                memory.pop(0)  # remove oldest
                memory.append(page)
            page_faults += 1

        history.append(memory.copy())

    return page_faults, history