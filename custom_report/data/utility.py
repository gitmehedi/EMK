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


    def getAddressByUnit(self, unit):
        address = []
        if unit.partner_id.street:
            address.append(unit.partner_id.street)

        if unit.partner_id.street2:
            address.append(unit.partner_id.street2)

        if unit.partner_id.zip_id:
            address.append(unit.partner_id.zip_id.name)

        if unit.partner_id.city:
            address.append(unit.partner_id.city)

        if unit.partner_id.state_id:
            address.append(unit.partner_id.state_id.name)

        if unit.partner_id.country_id:
            address.append(unit.partner_id.country_id.name)

        str_address = ', '.join(address)

        return str_address