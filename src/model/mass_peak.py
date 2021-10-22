class MassPeak:
    def __init__(self,
                 sample_name,
                 spot_id,
                 mass_peak_name,
                 raw_cps_data,
                 detector_yield,
                 detector_background,
                 dead_time
                 ):
        self.sample_name = sample_name
        self.spot_id = spot_id
        self.name = mass_peak_name
        self.raw_cps_data = raw_cps_data
        self.detector_yield = detector_yield
        self.detector_background = detector_background
        self.dead_time = dead_time
