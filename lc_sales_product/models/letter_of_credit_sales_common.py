from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
import numpy as np

class LetterOfCreditCommon(models.Model):
    _inherit = "letter.credit"


    pi_ids = fields.One2many('proforma.invoice', 'lc_id', string='Proforma Invoice')
    pi_ids_temp = fields.Many2many('proforma.invoice', 'pi_lc_rel', 'lc_id', 'pi_id', string='Proforma Invoice',
                                   domain="[('state', '=', 'confirm'),('lc_id','=',False)]")

    tenure = fields.Char(string='Tenure')
    product_lines = fields.One2many('lc.product.line', 'lc_id', string='Product(s)')

    pi_note = fields.Char(string='PI Step', track_visibility='onchange')

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
    def write(self, values):
        # In this funtion only allow local, foreign -> export
        # Update or Remove LC reference at PI change
        if self.type == 'export' and (self.state == 'confirmed' or self.state == 'progress'):
            if values.get('pi_ids_temp'):
                pi_numbers = []
                old_pi = self.pi_ids_temp.ids
                current_pi = values['pi_ids_temp'][0][2]
                newly_added_pi = np.setdiff1d(current_pi, old_pi)
                newly_removed_pi = np.setdiff1d(old_pi,current_pi)

                for pi_id in newly_added_pi:
                    pi_obj = self.env['proforma.invoice'].search([('id', '=', pi_id)])
                    self.associate_with_lc(pi_obj)
                    pi_numbers.append(pi_obj.name)

                values['pi_note'] = ""

                if pi_numbers:
                    values['pi_note'] = 'Newly Added ' + ','.join(pi_numbers) +' PI(s)'

                pi_numbers = []
                for pi_id in newly_removed_pi:
                    pi_obj = self.env['proforma.invoice'].search([('id', '=', pi_id)])
                    pi_numbers.append(pi_obj.name)

                    pi_obj.suspend_security().write({'lc_id': None})

                    sale_obj = self.env['sale.order'].search([('pi_id', '=', pi_id)])
                    if sale_obj:
                        for s_order in sale_obj:
                            s_order.suspend_security().write({'lc_id': None})

                if pi_numbers:
                    values['pi_note'] += ' Remove '+ ','.join(pi_numbers) +' PI(s)'

        res = super(LetterOfCreditCommon, self).write(values)
        return res

    @api.multi
    def action_confirm_export(self):
        pi_numbers = []
        for pi in self.pi_ids_temp:
            self.associate_with_lc(pi)
            pi_numbers.append(pi.name)

        self.write({'state': 'confirmed', 'last_note': 'Getting Confirmation',
                    'pi_note': 'Associate ' + ','.join(pi_numbers) +' PI(s)'})


    def associate_with_lc(self, pi):
        pi.suspend_security().write({'lc_id': self.id})

        sale_obj = pi.env['sale.order'].search([('pi_id', '=', pi.id)])
        if sale_obj:
            for s_order in sale_obj:
                s_order.write({'lc_id': self.id})  # update lc_id

                # Update 100 MT logic
                da_obj = self.env['delivery.authorization'].search([('sale_order_id', '=', s_order.id)])

                for d in da_obj:
                    d.sudo().update_lc_id_for_houndred_mt()
        return


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
    def action_lc_done_export(self):
        self.write({'state': 'done', 'last_note': 'Close/Done the LC'})





