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



    def getCoustomerAddress(self,coustomer):
            address = []
            if coustomer.street:
                address.append(coustomer.street)

            if coustomer.street2:
                address.append(coustomer.street2)

            if coustomer.zip_id:
                address.append(coustomer.zip_id.name)

            if coustomer.city:
                address.append(coustomer.city)

            if coustomer.state_id:
                address.append(coustomer.state_id.name)

            if coustomer.country_id:
                address.append(coustomer.country_id.name)

            str_address = ', '.join(address)
            return str_address

    def getBankAddress(self,bank):
            address = []
            if bank.street:
                address.append(bank.street)

            if bank.street2:
                address.append(bank.street2)

            if bank.zip:
                address.append(bank.zip)

            if bank.city:
                address.append(bank.city)

            if bank.state:
                address.append(bank.state.name)

            if bank.country:
                address.append(bank.country.name)

            str_address = ', '.join(address)
            return str_address