######################################
### Getting data from old asc file ###
######################################

DETECTOR_LINE = 25
DETECTOR_PARAMETERS_LINE = 62


def get_raw_cps_data(raw_data_line_start, column_number, spot_data, block_number):
    line_range = range(raw_data_line_start, raw_data_line_start + int(block_number))
    raw_cps_data = []
    for line in line_range:
        raw_cps_data.append(spot_data[line][column_number])

    print(raw_cps_data)
    return raw_cps_data


def get_detector_data(spot_data, column_number):
    detector = spot_data[DETECTOR_LINE][column_number - 1]
    detector_data = []
    line = DETECTOR_PARAMETERS_LINE
    contains_detector = detector in spot_data[line]
    while not contains_detector:
        line += 1
        contains_detector = detector in spot_data[line]

    detector_data.append(spot_data[line][1])
    detector_data.append(spot_data[line][2])
    detector_data.append(spot_data[line][3])

    print(detector_data)
    return detector_data


def get_data_from_old_asc(spot_data, mass_peak_name):
    # Finding the number of blocks
    line_number = 113
    contains_blocks = "Blocks" in spot_data[line_number]
    while not contains_blocks:
        line_number += 1
        line = spot_data[line_number]
        contains_blocks = "Blocks" in line
    block_index = spot_data[line_number].index("Blocks")
    block_number = spot_data[line_number][block_index - 1]

    # Finding the start of the raw data
    line_number = 160
    contains_word_raw_data = False
    while not contains_word_raw_data:
        line_number += 1
        line = spot_data[line_number]
        if any("RAW DATA" in i for i in line):
            contains_word_raw_data = True
    raw_data_mass_peak_line = line_number + 4
    raw_data_line_start = line_number + 6

    # +1 is because the file format is fairly terrible
    column_number = spot_data[raw_data_mass_peak_line].index(mass_peak_name) + 1

    raw_cps_data = get_raw_cps_data(raw_data_line_start, column_number, spot_data, block_number)

    detector_data = get_detector_data(spot_data, column_number)

    return raw_cps_data, detector_data
