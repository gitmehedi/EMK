from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VendorBillGenerationWizard(models.TransientModel):
    _name = 'vendor.bill.generation.batch.wizard'

    def _default_agreement(self):
        period_id = self.env.context.get('period_id')
        billing_period = self.env.context.get('billing_period')
        agreement_search = self.env['vendor.bill.generation.line'].search([('state', '!=', 'cancel'),
                                                                           ('period_id', '=', period_id)])
        agreement = set(self.env['vendor.advance'].search([('type', '=', 'multi'),
                                                           ('state', '=', 'approve'),
                                                           ('billing_period', '=', billing_period)]).ids) - set(
            [val.agreement_id.id for val in agreement_search])
        return list(agreement)

    agreement_ids = fields.Many2many('vendor.advance', string='Rent Agreements', required=True,
                                     default=_default_agreement)
    billing_period = fields.Selection([('monthly', "Monthly"), ('yearly', "Yearly")], string="Billing Period",
                                      required=True, readonly=True)
    period_id = fields.Many2one('date.range', string='Period', required=True, readonly=True)

    @api.multi
    def generate_record(self):
        vendor_bill_generation_line_env = self.env['vendor.bill.generation.line']
        active_id = self.env.context.get('active_id')
        if not self.agreement_ids:
            raise UserError(_("You must select agreement(s) to generate this process."))
        for agreement in self.agreement_ids:
            agreement_search = vendor_bill_generation_line_env.search([('agreement_id', '=', agreement.id),
                                                                       ('period_id', '=', self.period_id.id),
                                                                       ('state', '!=', 'cancel')])
            if len(agreement_search) > 0:
                raise ValidationError('This Agreement is already processed under the current Period in another Vendor '
                                      'Bill Generation: {}'.format(agreement.name))
            res = {
                'agreement_id': agreement.id,
                'vbg_id': active_id,
                'state': 'draft',
                'period_id': self.period_id.id
            }
            vendor_bill_generation_line_env.create(res)
        return {'type': 'ir.actions.act_window_close'}
