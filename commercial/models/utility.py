from odoo import api, models
from enum import Enum
import math

class Status(Enum):
    OPEN = "LC Open"
    CONFIRM = "Getting Bank Confirmation"
    AMENDMENT = "Amendment"
    SHIPMENT = "Shipment"
    PROGRESS = "LC In Progress"
    DONE = "Close/Done the LC"

class UtilityNumber(models.TransientModel):

    _name = "commercial.utility"



    def getStrNumber(self,number):
        ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])
        return ordinal(number)