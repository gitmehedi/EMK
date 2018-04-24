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

    def getDateTimeFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
        else:
            return None


    # Utility Methods
    def getDateFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d")
        else:
            return datetime.datetime.now()