from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
import numpy as np

class LetterOfCreditCommon(models.Model):
    _inherit = "letter.credit"

    cover_note_no = fields.Char(string='Cover Note No.')
    insurance_date = fields.Date(string='Date')

    transshipment_country_id = fields.Many2one('res.country', 'Transshipment Country')
    landing_port_country_id = fields.Many2one('res.country', 'Landing Port Country')
    discharge_port_country_id = fields.Many2one('res.country', 'Discharge Port Country')

    not_for_medical_use = fields.Boolean(string='Not For Medical Use')
    declaration = fields.Text(string='Declaration') # (For Packing List  & Commercial Invoice)
    document_receiver_bank = fields.Text(string='Document Receiver Bank')
    insurance_company_address = fields.Text(string='Address')
    insurance_policy_date = fields.Date(string='Policy Date')
    is_seaworthy_packing = fields.Boolean(string='Is Seaworthy Packing')

    model_type = fields.Selection([
        ('lc', 'LC'),
        ('tt', 'TT'),
        ('sales_contract', 'SC'),
    ], string="Type",
        help="LC: Letter Of Credit\n"
             "TT: Telegraphic Transfer\n"
             "SC: Sales Contract.",default='lc')

    sc_type = fields.Selection([
        ('sc', 'SC'),
        ('po', 'PO'),
        ('pi', 'PI')
    ], string="SC Type")

    @api.onchange('second_party_applicant')
    def onchange_second_party_applicant(self):
        if self.region_type == 'foreign' and self.type == 'export':
            if self.second_party_applicant.country_id.code:
                if self.second_party_applicant.country_id.code == 'IN':
                    self.declaration = "We hereby certify that goods are of Bangladesh origin " \
                                       "and are freely importable and not covered under the negative " \
                                       "list as per foreign trade policy 2015-2020, India."
                else:
                    self.declaration = "We hereby certify that goods are of Bangladesh origin."
            else:
                self.declaration = " "
    @api.multi
    def action_revision_export_foreign(self,amendment_date=None):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('lc_sales_product_foreign', 'view_lc_export_foreign_form')
        view_id = view_ref and view_ref[1] or False,
        self.with_context(new_lc_revision=True,amendment_date=amendment_date).copy()

        number = len(self.old_revision_ids)

        comm_utility_pool = self.env['commercial.utility']
        note = comm_utility_pool.getStrNumber(number) + ' ' + 'Amendment'

        self.write({'state': self.state, 'last_note': note})
        return {
            'type': 'ir.actions.act_window',
            'name': _('LC'),
            'res_model': 'letter.credit',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
            'flags': {'initial_mode': 'edit'},
        }


    @api.multi
    def action_shipment_export_foreign(self):
        self.write({'state': 'progress'})
        res = self.env.ref('lc_sales_product_foreign.view_shipment_export_form')
        if not self.shipment_ids:
            shipmentNo = 1
        else:
            shipmentNo = len(self.shipment_ids) + 1

        comm_utility_pool = self.env['commercial.utility']

        result = {'name': _('Shipment'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'purchase.shipment',
                  'context': {'shipment_number': comm_utility_pool.getStrNumber(shipmentNo) + ' Shipment',
                              'lc_id': self.id,
                              'operating_unit_id': self.operating_unit_id.id,
                              'company_id': self.first_party.id},
                  'type': 'ir.actions.act_window',
                  'target': 'current'}
        self.env['letter.credit'].search([('id', '=', self.id)])
        return result


    @api.multi
    def action_amendment_foreign(self):
        res = self.env.ref('lc_sales_product_foreign.lc_amendment_wizard_foreign')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.amendment.wizard.foreign',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result




