from openerp import api, exceptions, fields, models

class SalesContractConversionWizard(models.TransientModel):
    """
    Sales Contract Conversion Wizard helps to convert
    sales contract to master lc
    """
    _name="sales.contract.conversion.wizard"

    @api.multi
    def convert_salse_contract(self, context=None):
        default = dict({})
        obj = self.env['sales.contract'].browse(context['active_id'])

        if obj:
            default['buyer_id'] = obj.buyer_id.id
            default['lc_open_bank_id'] = obj.sc_bank_id.id
            default['lc_value'] = obj.sc_value
            default['currency_id'] = obj.sc_currency_id.id
            default['payment_term_id'] = obj.payment_term_id.id
            default['inco_term_id'] = obj.inco_term_id.id
            default['inco_term_place'] = obj.inco_term_place

            res = self.env['master.lc'].create(default)

            for val in obj.so_ids:
                res.so_ids += val

            return {
                'view_type': 'form',
                'view_mode': 'form',
                'src_model': 'master.lc',
                'res_model': 'master.lc',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': res.id,
                'target':'current',
            }