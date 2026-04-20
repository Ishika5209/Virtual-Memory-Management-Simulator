def segmentation(segment_table, segment, offset):
    if segment >= len(segment_table):
        return "Invalid Segment"

    base, limit = segment_table[segment]

    if offset >= limit:
        return "Segmentation Fault"

    physical_address = base + offset
    return physical_address