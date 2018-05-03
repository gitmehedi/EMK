from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from openerp.addons.commercial.models.utility import Status, UtilityNumber

class LetterOfCredit(models.Model):
    _inherit = "letter.credit"


    @api.multi
    def action_confirm_export(self):
        self.write({'state': 'open', 'last_note': Status.OPEN.value})

    # last_note = fields.Char(string='Step', track_visibility='onchange')
    #
    # @api.multi
    # @api.constrains('operating_unit_id')
    # def _check_operating_unit_id(self):
    #     for po in self.po_ids:
    #         if self.operating_unit_id.id != po.operating_unit_id.id:
    #             raise ValidationError(_("Operating unit of %s is not same with operating unit of letter of credit.\n"
    #                   "Your purchase order's operating unit and letter of credit's operating unit must be same.") % (po.name))
    #
    # @api.one
    # @api.constrains('name')
    # def _check_unique_constraint(self):
    #     if self.name:
    #         filters = [['name', '=ilike', self.name]]
    #         name = self.search(filters)
    #         if len(name) > 1:
    #             raise Warning('LC Number must be unique!')

