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

    def getBranchAddress(self,branch):
            address = []
            if branch.street:
                address.append(branch.street)

            if branch.street2:
                address.append(branch.street2)

            if branch.zip:
                address.append(branch.zip)

            if branch.city:
                address.append(branch.city)

            if branch.country_id:
                address.append(branch.country_id.name)

            str_address = ', '.join(address)
            return str_address

    def getBankAddress2(self,bank):
            address = []
            if bank.street:
                address.append('<p>'+bank.street+'</p>')

            if bank.street2:
                address.append('<p>'+bank.street2+'</p>')

            if bank.zip:
                address.append('<p>'+bank.zip+'</p>')

            if bank.city:
                address.append('<p>'+bank.city+'</p>')

            if bank.state:
                address.append('<p>'+bank.state.name+'</p>')

            if bank.country:
                address.append('<p>'+bank.country.name+'</p>')

            str_address = ''.join(address)
            return str_address

    def getBranchAddress2(self,branch):
            address = []
            if branch.street:
                address.append('<p>'+branch.street+'</p>')

            if branch.street2:
                address.append('<p>'+branch.street2+'</p>')

            if branch.zip:
                address.append('<p>'+branch.zip+'</p>')

            if branch.city:
                address.append('<p>'+branch.city+'</p>')

            if branch.country_id:
                address.append('<p>'+branch.country_id.name+'</p>')

            str_address = ''.join(address)
            return str_address