from odoo import models, api, _, fields
from odoo.tools.misc import formatLang


class report_account_aged_partner(models.AbstractModel):
    _inherit = "account.aged.partner"

    @api.model
    def _lines(self, context, line_id=None):
        # check if vendor advance aged payable
        if not self.env.context.get('advance_aged_payable', False):
            return super(report_account_aged_partner, self)._lines(context, line_id)

        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(include_nullified_amount=True)._get_partner_move_lines([self._context['account_type']], self._context['date_to'], 'posted', 29)
        for values in results:
            if line_id and values['partner_id'] != line_id:
                continue
            vals = {
                'id': values['partner_id'] and values['partner_id'] or -1,
                'name': values['name'],
                'level': 0 if values['partner_id'] else 2,
                'type': values['partner_id'] and 'partner_id' or 'line',
                'footnotes': context._get_footnotes('partner_id', values['partner_id']),
                'columns': [values['direction'], values['6'], values['5'], values['4'], values['3'], values['2'], values['1'], values['0'], values['total']],
                'trust': values['trust'],
                'unfoldable': values['partner_id'] and True or False,
                'unfolded': values['partner_id'] and (values['partner_id'] in context.unfolded_partners.ids) or False,
            }
            vals['columns'] = [self._format(sign * t) for t in vals['columns']]
            lines.append(vals)
            if values['partner_id'] in context.unfolded_partners.ids:
                for line in amls[values['partner_id']]:
                    aml = line['line']
                    vals = {
                        'id': aml.id,
                        'name': aml.move_id.name if aml.move_id.name else '/',
                        'move_id': aml.move_id.id,
                        'action': aml.get_model_id_and_name(),
                        'level': 1,
                        'type': 'move_line_id',
                        'footnotes': context._get_footnotes('move_line_id', aml.id),
                        'columns': [line['period'] == 8 - i and self._format(sign * line['amount']) or '' for i in range(9)],
                    }
                    lines.append(vals)
                vals = {
                    'id': values['partner_id'],
                    'type': 'o_account_reports_domain_total',
                    'name': _('Total '),
                    'footnotes': self.env.context['context_id']._get_footnotes('o_account_reports_domain_total', values['partner_id']),
                    'columns': [values['direction'], values['6'], values['5'], values['4'], values['3'], values['2'], values['1'], values['0'], values['total']],
                    'level': 1,
                }
                vals['columns'] = [self._format(sign * t) for t in vals['columns']]
                lines.append(vals)
        if total and not line_id:
            total_line = {
                'id': 0,
                'name': _('Total'),
                'level': 0,
                'type': 'o_account_reports_domain_total',
                'footnotes': context._get_footnotes('o_account_reports_domain_total', 0),
                'columns': [total[8], total[6], total[5], total[4], total[3], total[2], total[1], total[0], total[7]],
            }
            total_line['columns'] = [self._format(sign * t) for t in total_line['columns']]
            lines.append(total_line)
        return lines


class report_account_advance_aged_payable(models.AbstractModel):
    _name = "account.advance.aged.payable"
    _description = "Aged Payable"
    _inherit = "account.aged.partner"

    @api.model
    def get_lines(self, context_id, line_id=None):
        if type(context_id) == int:
            context_id = self.env['account.context.advance.aged.payable'].search([['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
            'date_to': context_id.date_to,
            'aged_balance': True,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
            'account_type': 'payable',
            'advance_aged_payable': True,
        })
        return self.with_context(new_context)._lines(context_id, line_id)

    @api.model
    def get_title(self):
        return _("Advance Aged Payable")

    @api.model
    def get_name(self):
        return 'advance_aged_payable'

    @api.model
    def get_report_type(self):
        return self.env.ref('account_reports.account_report_type_nothing')

    def get_template(self):
        return 'account_reports.report_financial'


class account_context_advance_aged_payable(models.TransientModel):
    _name = "account.context.advance.aged.payable"
    _description = "A particular context for the aged payable"
    _inherit = "account.report.context.common"

    fold_field = 'unfolded_partners'
    unfolded_partners = fields.Many2many('res.partner', 'advance_aged_payable_context_to_partner', string='Unfolded lines')

    def get_report_obj(self):
        return self.env['account.advance.aged.payable']

    def get_columns_names(self):
        return [_(u"Not\N{NO-BREAK SPACE}due\N{NO-BREAK SPACE}on %s") % self.date_to,
                u"0\N{NO-BREAK SPACE}-\N{NO-BREAK SPACE}30",
                u"31\N{NO-BREAK SPACE}-\N{NO-BREAK SPACE}60",
                u"61\N{NO-BREAK SPACE}-\N{NO-BREAK SPACE}90",
                u"91\N{NO-BREAK SPACE}-\N{NO-BREAK SPACE}120",
                u"121\N{NO-BREAK SPACE}-\N{NO-BREAK SPACE}150",
                u"151\N{NO-BREAK SPACE}-\N{NO-BREAK SPACE}180",
                _(u"Older"),
                _(u"Total")]

    @api.multi
    def get_columns_types(self):
        return ["number", "number", "number", "number", "number", "number", "number", "number", "number"]
