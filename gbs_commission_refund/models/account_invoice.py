from collections import defaultdict
import json

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, time, timedelta
from lxml import etree


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    commission_move_id = fields.Many2one('account.move', 'Commission Journal Entry')
    refund_move_id = fields.Many2one('account.move', 'Refund Journal Entry')

    reverse_commission_move_id = fields.Many2one('account.move', 'Reverse Commission Journal Entry')
    reverse_refund_move_id = fields.Many2one('account.move', 'Reverse Refund Journal Entry')

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(AccountInvoice, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            company = self.env.user.company_id
            config = self.env['commission.configuration'].search([('customer_type', 'in', company.customer_types.ids or []), ('functional_unit', 'in', company.branch_ids.ids or [])], limit=1)

            if not config.show_packing_mode:
                doc = etree.XML(result['arch'])
                for field in doc.xpath("//field[@name='pack_type']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

                result['arch'] = etree.tostring(doc)

        return result

    def action_invoice_draft(self):
        super(AccountInvoice, self).action_invoice_draft()
        self.commission_move_id = [(5, 0, 0)]
        self.refund_move_id = [(5, 0, 0)]

    @staticmethod
    def get_move_line_vals(
            name,
            journal_date,
            journal_id,
            account_id,
            operating_unit_id,
            department_id,
            cost_center_id,
            debit,
            credit,
            company_id
    ):
        return {
            'name': name,
            'date': journal_date,
            'journal_id': journal_id,
            'account_id': account_id,
            'operating_unit_id': operating_unit_id,
            'department_id': department_id,
            'cost_center_id': cost_center_id,
            'debit': debit,
            'credit': credit,
            'company_id': company_id,
        }

    def get_move_vals(self, move_type, cr_journal_config):
        operating_unit_id = self.operating_unit_id
        cost_center_id = self.cost_center_id

        temp_acc = None
        label = ""
        department_id = cr_journal_config.department_id
        company_id = cr_journal_config.company_id

        if move_type == 'commission':
            total_amount = 0
            for line in self.invoice_line_ids:
                commission_amount = line.sale_line_ids.filtered(lambda r: r.product_id.id == line.product_id.id).corporate_commission_per_unit
                total_amount += (line.quantity * commission_amount)

                label = "{}: ({} x {})".format(line.product_id.name, line.quantity, commission_amount)

            name_seq = self.env['ir.sequence'].next_by_code('commission.account.move.seq')
            journal_id = self.env['account.journal'].sudo().search([('code', '=', 'COMJNL')], limit=1)

            # if we don't have extra account configurations we will take default account else the configured account matched with cost center and zone type.
            if len(cr_journal_config.commission_account_ids) > 0:
                temp_acc = cr_journal_config.commission_account_ids.filtered(lambda a: a.cost_center_id == cost_center_id and a.zone_type == self.partner_id.supplier_type)

            account_id = temp_acc.account_id if temp_acc else cr_journal_config.commission_account_id
            control_account_id = cr_journal_config.commission_control_account_id
        else:
            # ==== refund ====
            total_amount = 0
            for line in self.invoice_line_ids:
                refund_amount = line.sale_line_ids.filtered(lambda r: r.product_id.id == line.product_id.id).corporate_refund_per_unit
                total_amount += (line.quantity * refund_amount)
                label = "{}: ({} x {})".format(line.product_id.name, line.quantity, refund_amount)

            name_seq = self.env['ir.sequence'].next_by_code('refund.account.move.seq')
            journal_id = self.env['account.journal'].sudo().search([('code', '=', 'REFJNL')], limit=1)

            # if we don't have extra account configurations we will take default account else the configured account matched with cost center and zone type.
            if len(cr_journal_config.refund_account_ids) > 0:
                temp_acc = cr_journal_config.refund_account_ids.filtered(lambda a: a.cost_center_id == cost_center_id and a.zone_type == self.partner_id.supplier_type)

            account_id = temp_acc.account_id if temp_acc else cr_journal_config.refund_account_id
            control_account_id = cr_journal_config.refund_control_account_id

        if total_amount <= 0:
            return

        commission_debit_vals = self.get_move_line_vals(
            label,
            self.date_invoice,
            journal_id.id,
            account_id.id,
            operating_unit_id.id,
            department_id.id,
            cost_center_id.id,
            total_amount,
            0,
            company_id.id
        )

        commission_credit_vals = self.get_move_line_vals(
            label,
            self.date_invoice,
            journal_id.id,
            control_account_id.id,
            operating_unit_id.id,
            department_id.id,
            cost_center_id.id,
            0,
            total_amount,
            company_id.id
        )

        return {
            'name': name_seq,
            'journal_id': journal_id.id,
            'operating_unit_id': operating_unit_id.id,
            'date': self.date_invoice,
            'company_id': company_id.id,
            'partner_id': self.partner_id.id,
            'state': 'draft',
            'line_ids': [(0, 0, commission_debit_vals), (0, 0, commission_credit_vals)],
        }

    @api.multi
    def action_invoice_open(self):
        if self.type == 'out_invoice':
            config = self.env['commission.configuration'].sudo().search(
                [
                    ('customer_type', 'in', self.company_id.customer_types.ids),
                    ('functional_unit', '=', self.partner_id.branch_id.id)
                ],
                limit=1
            )

            if not config:
                if not self.company_id.customer_types:
                    raise UserError(_("Please configure customer type on your company."))

                if not self.partner_id.branch_id:
                    raise UserError(_("Functional Unit not found to the customer."))

            if config.process != 'not_applicable' and config.commission_provision == 'invoice_validation':
                # commission and refund journal config
                cr_journal_config = self.env['commission.refund.acc.config'].sudo().search([['company_id', '=', self.company_id.id]], limit=1)

                if not cr_journal_config:
                    raise UserError(_("Commission and Refund configuration is not found for this company."))

                # commission
                commission_move_vals = self.get_move_vals('commission', cr_journal_config)
                commission_move = self.env['account.move'].sudo().create(commission_move_vals) if commission_move_vals else None
                if commission_move:
                    self.commission_move_id = commission_move.id
                    commission_move.post()

                # refund
                refund_move_vals = self.get_move_vals('refund', cr_journal_config)
                refund_move = self.env['account.move'].sudo().create(refund_move_vals) if refund_move_vals else None
                if refund_move:
                    self.refund_move_id = refund_move.id
                    refund_move.post()

        res = super(AccountInvoice, self).action_invoice_open()
        return res
