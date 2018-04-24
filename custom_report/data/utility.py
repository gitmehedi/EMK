from odoo import models
import datetime


class ReportUtility(models.TransientModel):
    _name = "report.utility"

    def getERPDateFormat(self, date):
        try:
            if date:
                return date.strftime('%d-%b-%Y')
            else:
                return ""
        except Exception as e:
            return ""