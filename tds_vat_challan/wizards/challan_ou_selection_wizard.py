from itertools import groupby
from odoo import models, fields, api,_


class TDSChallaOUSelectionWizard(models.TransientModel):
    _name = 'tds.challan.ou.selection.wizard'
    _description = 'TDS Challan Operating Unit Wizard'


    operating_unit_id = fields.Many2one('operating.unit', string='Branch')


    @api.multi
    def generate_challan(self):
        # active_ids = self.env.context.get('active_ids')
        account_move_line_objs = self.env['account.move.line'].search([('id', 'in', self.env.context.get('active_ids'))],
                                                                      order='partner_id asc,operating_unit_id asc')
        challan_obj = self.env['tds.vat.challan']
        challan_line_obj = self.env['tds.vat.challan.line']
        challan_objs = []
        tds_challan_list = []

        if self.operating_unit_id:
            account_move_line_objs = account_move_line_objs.filtered(lambda r: r.operating_unit_id.id == self.operating_unit_id.id)

        for account_move_line_obj in account_move_line_objs:
            is_create = False
            for challan_obj in challan_objs:
                if account_move_line_obj.partner_id.id == challan_obj.supplier_id.id and \
                    account_move_line_obj.operating_unit_id.id == challan_obj.operating_unit_id.id:
                    challan_obj.write({'acc_move_line_ids':[(4, account_move_line_obj.id)]})
                    is_create = True
                    break
            if not is_create:
                challan = {
                    'supplier_id': account_move_line_obj.partner_id.id,
                    'operating_unit_id': account_move_line_obj.operating_unit_id.id,
                    'date': fields.Date.today(),
                    'state': 'draft',
                    'acc_move_line_ids':[(4, account_move_line_obj.id)],
                }
                res_challan_obj = challan_obj.create(challan)
                if res_challan_obj:
                    challan_objs.append(res_challan_obj)
                    tds_challan_list.append(res_challan_obj.id)

            account_move_line_obj.write({'is_deposit': True})

        for challan in challan_objs:
            if len(challan.acc_move_line_ids) == 1:
                id_param = "(" + str(challan.acc_move_line_ids.id) + ")"
            else:
                id_param = str(tuple(challan.acc_move_line_ids.ids))
            self.env.cr.execute("""
                                SELECT SUM(credit) as amount,name
                                FROM account_move_line
                                WHERE id in %s
                                group by name"""%(id_param))
            results = self.env.cr.fetchall()
            for amount,name in results:
                line = {
                    'supplier_id': challan.supplier_id.id,
                    'challan_provided': 0.0,
                    'total_bill': amount,
                    'undistributed_bill': amount,
                    'parent_id': challan.id,
                    'state': 'draft',
                    'type_name': name,
                }
                challan_line_obj.create(line)

        vals = [('id', 'in', tds_challan_list)]
        return {
            'name': _('TDS/VAT Challan'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'tds.vat.challan',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': vals,
        }