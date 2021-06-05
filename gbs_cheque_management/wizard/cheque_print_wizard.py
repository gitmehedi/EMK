# imports of python library
import datetime

# imports of odoo
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class ChequePrintWizard(models.TransientModel):
    _name = "cheque.print.wizard"

    pay_to = fields.Char("Pay To", required=True)
    is_cross_cheque = fields.Boolean(string='Is Cross Cheque')
    date_on_cheque = fields.Date("Date On Cheque", required=True)
    amount = fields.Float("Amount", required=True)
    amount_in_word = fields.Char("Amount In Word", required=True)
    narration = fields.Char("Narration", required=True)

    hide_field = fields.Boolean(string='Hide')
    
    @api.multi
    def button_print_pdf(self):
        print ('hi pdf')


    @api.multi
    def button_print_on_printer(self):
        print ('hi printer')
