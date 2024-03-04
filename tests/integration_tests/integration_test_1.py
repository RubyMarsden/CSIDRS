import unittest

from controllers.signals import Signals
from model.drift_correction_type import DriftCorrectionType
from model.elements import Element
from model.isotopes import Isotope
from model.settings.material_lists import Material
from model.settings.methods_from_isotopes import two_isotopes_no_hydroxide_oxygen
from model.sidrs_model import SidrsModel


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.signals = Signals()
    def test_integration1(self):
        self.model = SidrsModel(signals=self.signals)
        self.element = Element.OXY
        self.model.method = two_isotopes_no_hydroxide_oxygen
        self.ratio = two_isotopes_no_hydroxide_oxygen.ratios[0]
        isotopes = [Isotope.O16,  Isotope.O18]
        material = Material.ZIR
        self.model._isotopes_input(isotopes, self.element)
        self.model._material_input(material)
        self.model.import_all_files(["fixtures/OGC@01.asc",
                                     "fixtures/OGC@02.asc",
                                     "fixtures/OGC@03.asc",
                                     "fixtures/OGC@04.asc",
                                     "fixtures/OGC@05.asc",
                                     "fixtures/OGC@06.asc",
                                     "fixtures/OGC@07.asc",
                                     "fixtures/OGC@08.asc",
                                     "fixtures/OGC@09.asc",
                                     "fixtures/OGC@10.asc",
                                     "fixtures/OGC@11.asc",
                                     "fixtures/OGC@12.asc",
                                     "fixtures/OGC@13.asc",
                                     "fixtures/unknown@01.asc"
                                     ])

        primary_reference_material = "OGC"
        secondary_reference_material = "No secondary reference material"
        self.model._reference_material_tag_samples(primary_reference_material, secondary_reference_material)
        self.model.process_data()

        self.check_sample_existence()

        self.model.recalculate_data_with_drift_correction_changed(self.ratio, drift_correction_type=DriftCorrectionType.LIN)

        self.model.export_cycle_data_csv('itest1_cycle_data.csv')
        self.model.export_raw_data_csv('itest1_raw_data.csv')
        self.model.export_corrected_data_csv('itest1_corrected_data.csv')
        self.model.export_analytical_conditions_csv('itest1_analytical_conditions.csv')



    def check_sample_existence(self):
        sample_names = [sample.name for sample in self.model.get_samples()]
        self.assertIn('OGC', sample_names)
        self.assertIn('unknown', sample_names)

    def compare_csvs(self):
        pass

if __name__ == '__main__':
    unittest.main()