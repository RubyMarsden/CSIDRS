######################################
### Getting data from old asc file ###
######################################

ACQUISITION_PARAMETERS_LINE = 13
DETECTOR_LINE = 25
ANALYTICAL_PARAMETERS_LINE = 30
DETECTOR_PARAMETERS_LINE = 62


def get_raw_cps_data(raw_data_line_start, column_number, spot_data, block_number):
    line_range = range(raw_data_line_start, raw_data_line_start + int(block_number))
    raw_cps_data = [spot_data[line][column_number] for line in line_range]

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

    return detector_data


def get_data_from_old_asc(spot_data, mass_peak_name):
    block_number = get_block_number_from_old_asc(spot_data)

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
    column_number = spot_data[raw_data_mass_peak_line].index(mass_peak_name.value) + 1

    raw_cps_data = get_raw_cps_data(raw_data_line_start, column_number, spot_data, block_number)

    detector_data = get_detector_data(spot_data, column_number)

    return raw_cps_data, detector_data


def get_primary_beam_current_data_old_asc(spot_data):
    # Finding the primary ion beam current at the beginning and end of the spot measurement
    line_number = 131
    contains_primary = False
    while not contains_primary:
        line_number += 1
        line = spot_data[line_number]
        contains_primary = "Primary Current START (A):" in line
    primary_start_data = spot_data[line_number][-1]
    data, magnitude = primary_start_data.split("E")
    primary_start_value = float(data) * 10 ** int(magnitude)
    primary_end_data = spot_data[line_number + 1][-1]
    data, magnitude = primary_end_data.split("E")
    primary_end_value = float(data) * 10 ** int(magnitude)
    primary_beam_current = (primary_start_value + primary_end_value) / 2
    return primary_beam_current


def get_dtfa_x_and_y_from_old_asc(spot_data):
    line_number = 138
    contains_beam_centering = False
    while not contains_beam_centering:
        line_number += 1
        line = spot_data[line_number]
        contains_beam_centering = "Field App (DT1)" in line

    dtfa_x = int(spot_data[line_number][3])
    dtfa_y = int(spot_data[line_number][4])

    return dtfa_x, dtfa_y


def get_block_number_from_old_asc(spot_data):
    # Finding the number of blocks - this is actually the number of cycles, but is labelled blocks in the asc file.
    line_number = 113
    contains_blocks = "Blocks" in spot_data[line_number]
    while not contains_blocks:
        line_number += 1
        line = spot_data[line_number]
        contains_blocks = "Blocks" in line
    block_index = spot_data[line_number].index("Blocks")
    block_number = spot_data[line_number][block_index - 1]

    return block_number


def get_analytical_conditions_data_from_old_asc_file(data):
    start_line_number = ACQUISITION_PARAMETERS_LINE
    end_line_number = 112
    analytical_conditions_data = []
    for i in range(start_line_number, end_line_number):
        analytical_conditions_data.append(data[i])

    return analytical_conditions_data
