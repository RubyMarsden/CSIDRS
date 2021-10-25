class MassPeak:
    def __init__(self,
                 sample_name,
                 spot_id,
                 mass_peak_name,
                 raw_cps_data,
                 detector_data
                 ):
        self.sample_name = sample_name
        self.spot_id = spot_id
        self.name = mass_peak_name
        self.raw_cps_data = raw_cps_data
        # TODO add detector data
        self.detector_yield = detector_data
        self.detector_background = detector_data
        self.dead_time = detector_data
