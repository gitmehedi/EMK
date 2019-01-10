from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError

class LetterOfCredit(models.Model):
    _inherit = "letter.credit"


    pi_ids = fields.One2many('proforma.invoice', 'lc_id', string='Proforma Invoice')
    pi_ids_temp = fields.Many2many('proforma.invoice', 'pi_lc_rel', 'lc_id', 'pi_id', string='Proforma Invoice',
                                   domain="[('state', '=', 'confirm'),('lc_id','=',False)]")

    tenure = fields.Char(string='Tenure')
    product_lines = fields.One2many('lc.product.line', 'lc_id', string='Product(s)')
    lc_document_line = fields.One2many('lc.document.line', 'lc_id', string='LC Documents')


    @api.onchange('pi_ids_temp')
    def pi_product_line(self):
        self.product_lines = []
        vals = []
        self.first_party = None
        self.second_party_applicant = None
        self.currency_id = None
        self.lc_value = None
        self.operating_unit_id = None
        self.first_party_bank_acc = None

        for pi_id in self.pi_ids_temp:
            so_id = self.env['sale.order'].search([('pi_id', '=', pi_id.id)])

            if not so_id:
                raise ValidationError('Please add Proforma Invoice whose have Sale Order.')
            elif self.first_party and self.first_party != pi_id.beneficiary_id:
                raise ValidationError('Please add Proforma Invoice whose Beneficiary are same.')
            # elif self.operating_unit_id and self.operating_unit_id != pi_id.operating_unit_id:
            #     raise ValidationError('Please add Proforma Invoice whose Unit are same.')
            elif self.second_party_applicant and self.second_party_applicant != pi_id.partner_id:
                raise ValidationError('Please add Proforma Invoice whose Applicant are same.')
            elif self.currency_id and self.currency_id != pi_id.currency_id:
                raise ValidationError('Please add Proforma Invoice whose Currency are same.')
            elif self.first_party_bank_acc and self.first_party_bank_acc != pi_id.advising_bank_acc_id:
                raise ValidationError('Please add Proforma Invoice whose Bank Account are same.')
            else:
                self.first_party = pi_id.beneficiary_id
                self.second_party_applicant = pi_id.partner_id.id
                self.currency_id = pi_id.currency_id.id
                self.lc_value += pi_id.total
                self.operating_unit_id = pi_id.operating_unit_id.id
                self.first_party_bank_acc = pi_id.advising_bank_acc_id
            for obj in pi_id.line_ids:
                vals.append((0, 0, {'product_id': obj.product_id,
                                    'name': obj.product_id.name,
                                    'product_qty': obj.quantity,
                                    'price_unit': obj.price_unit,
                                    'currency_id': pi_id.currency_id,
                                    'product_uom': obj.uom_id
                                    }))
        self.product_lines = vals


    @api.multi
    def action_confirm_export(self):
        for pi in self.pi_ids_temp:

            pi.suspend_security().write({'lc_id': self.id})

            sale_obj = pi.env['sale.order'].search([('pi_id','=',pi.id)])
            if sale_obj:
                for s_order in sale_obj:
                    s_order.write({'lc_id':self.id}) # update lc_id

                    # Update 100 MT logic
                    da_obj = self.env['delivery.authorization'].search([('sale_order_id', '=', s_order.id)])

                    for d in da_obj:
                        d.sudo().update_lc_id_for_houndred_mt()

        self.write({'state': 'confirmed', 'last_note': 'Getting Confirmation'})

    @api.multi
    def action_cancel_export(self):

        # Precondition
        # Condition - 1
        for shipment in self.shipment_ids:
            if shipment.state != 'done' and shipment.state != 'cancel':
                raise ValidationError(_("This LC has " + str(len(self.shipment_ids)) +
                                        " shipment(s).Before Cancel this LC, need to Cancel or Done all Shipment(s)."))
        # Condition - 2
        for pi in self.pi_ids:

            sale_obj = pi.env['sale.order'].search([('pi_id','=',pi.id)])
            if sale_obj:
                for s_order in sale_obj:
                    da_obj = self.env['delivery.authorization'].search([('sale_order_id', '=', s_order.id)])
                    if da_obj.state == 'close':
                        raise ValidationError(_("This LC contain Approve DA. At this time you can not Cancel this LC."))

        for pi in self.pi_ids:

            pi.suspend_security().write({'lc_id': None})

            sale_obj = pi.env['sale.order'].search([('pi_id','=',pi.id)])
            if sale_obj:
                for s_order in sale_obj:
                    s_order.write({'lc_id':None})

        self.state = "cancel"
        self.last_note = "LC Cancel"

    @api.multi
    def action_revision_export(self,amendment_date=None):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('lc_sales_product', 'view_lc_export_form')
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
    def action_shipment_export(self):
        self.write({'state': 'progress'})
        res = self.env.ref('lc_sales_product.view_shipment_export_form')
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
    def action_lc_done_export(self):
        self.write({'state': 'done', 'last_note': 'Close/Done the LC'})

    @api.multi
    def action_amendment(self):
        res = self.env.ref('lc_sales_product.lc_amendment_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.amendment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result




