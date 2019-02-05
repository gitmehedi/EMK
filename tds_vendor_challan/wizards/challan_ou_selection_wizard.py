from odoo import models, fields, api,_


class TDSChallaOUSelectionWizard(models.TransientModel):
    _name = 'tds.challan.ou.selection.wizard'
    _description = 'TDS Challan Operating Unit Wizard'


    operating_unit_id = fields.Many2one('operating.unit', string='Branch')


    @api.multi
    def generate_challan(self):
        # active_ids = self.env.context.get('active_ids')
        account_move_line_objs = self.env['account.move.line'].search([('id', 'in', self.env.context.get('active_ids'))], order='partner_id asc')
        challan_obj = self.env['tds.vendor.challan']
        challan_line_obj = self.env['tds.vendor.challan.line']
        challan_id = False
        pre_supplier_list = []
        pre_op_unit_list = []
        tds_challan_list = []

        if self.operating_unit_id:
            account_move_line_objs = account_move_line_objs.filtered(lambda r: r.operating_unit_id.id == self.operating_unit_id.id)

        for account_move_line_obj in account_move_line_objs:

            if account_move_line_obj.partner_id.id in pre_supplier_list and account_move_line_obj.operating_unit_id.id in pre_op_unit_list:
                pass
            else:
                challan = {
                    'supplier_id': account_move_line_obj.partner_id.id,
                    'operating_unit_id': account_move_line_obj.operating_unit_id.id,
                    'date': fields.Date.today(),
                    'state': 'draft',
                }

                res_challan_obj = challan_obj.create(challan)
                if res_challan_obj:
                    challan_id = res_challan_obj.id
                    tds_challan_list.append(res_challan_obj.id)
                    pre_supplier_list.append(res_challan_obj.supplier_id.id)
                    pre_op_unit_list.append(res_challan_obj.operating_unit_id.id)

            line = {
                'supplier_id': account_move_line_obj.partner_id.id,
                'challan_provided': 0.0,
                'total_bill': account_move_line_obj.credit,
                'undistributed_bill': account_move_line_obj.credit,
                'parent_id': challan_id,
                'acc_move_line_id': account_move_line_obj.id,
                'state': 'draft',

            }
            challan_line_obj.create(line)

            account_move_line_obj.write({'is_deposit': True})

        vals = [('id', 'in', tds_challan_list)]
        return {
            'name': _('TDS/VAT Challan'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'tds.vendor.challan',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': vals,
        }

