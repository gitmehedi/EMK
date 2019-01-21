from odoo import models, fields, api,_


class TDSChallaOUSelectionWizard(models.TransientModel):
    _name = 'tds.challan.ou.selection.wizard'
    _description = 'TDS Challan Operating Unit Wizard'


    operating_unit_id = fields.Many2one('operating.unit', string='Branch')


    @api.multi
    def generate_challan(self):
        # active_ids = self.env.context.get('active_ids')
        account_move_line_objs = self.env['account.move.line'].search([('id', 'in', self.env.context.get('active_ids'))])
        challan_obj = self.env['tds.vendor.challan']
        challan_line_obj = self.env['tds.vendor.challan.line']
        challan_id = False
        pre_supplier_list = []
        for account_move_line_obj in account_move_line_objs:

            if account_move_line_obj.partner_id.id in pre_supplier_list:
                pass
            else:
                challan = {
                    'supplier_id': account_move_line_obj.partner_id.id,
                    # 'operating_unit_id': account_move_line_obj,
                    'state': 'draft',
                }

                res_challan_obj = challan_obj.create(challan)
                if res_challan_obj:
                    challan_id = res_challan_obj.id
                    pre_supplier_list.append(res_challan_obj.supplier_id.id)

            line = {
                'supplier_id': account_move_line_obj.partner_id.id,
                'challan_provided': 0.0,
                'total_bill': account_move_line_obj.debit,
                'undistributed_bill': account_move_line_obj.debit,
                'parent_id': challan_id,
                'acc_move_line_id': account_move_line_obj.id,
                'state': 'draft',

            }
            challan_line_obj.create(line)

        return {'type': 'ir.actions.act_window_close'}

