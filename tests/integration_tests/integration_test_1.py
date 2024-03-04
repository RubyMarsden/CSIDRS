import unittest

from controllers.signals import Signals
from model.sidrs_model import SidrsModel

class IntegrationTest1(unittest.TestCase):
    model = SidrsModel(signals=Signals)