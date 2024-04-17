import re
import os
from typing import List


def find_longest_common_prefix_index(values: List[str]) -> int:
    if not values:
        return 0

    counter = 0
    while True:
        characters_at_index = set()

        for value in values:
            if counter < len(value):
                characters_at_index.add(value[counter])
            else:
                return counter

        if len(characters_at_index) == 1:
            counter += 1
        else:
            return counter


def split_cameca_data_filename(filename):
    base_name = os.path.basename(filename)
    # splitting x@y.z into [x,y,z] where y is the spot number and x is the sample and mount name (usually).
    parts = re.split('@|\\.|/', base_name)

    error_message = "Unexpected filename '" + base_name + "'. Expected format: x@y.asc where y is the spot " \
                                                          "number and x is the mount and sample name."
    if len(parts) != 3:
        raise Exception(error_message)
    full_sample_name = parts[0]
    spot_id = parts[1]
    if len(parts) != 3 or len(full_sample_name) == 0 or len(spot_id) == 0:
        raise Exception(error_message)

    return full_sample_name, spot_id
