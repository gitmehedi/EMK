from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class IrSequenceOperatingUnit(models.Model):
    _inherit = 'ir.sequence'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

    @api.model
    def next_by_code_new(self, sequence_code):
        self.check_access_rights('read')
        force_company = self._context.get('force_company')
        if not force_company:
            force_company = self.env.user.company_id.id

        seq_ids = self.search([('code', '=', sequence_code),
                               ('company_id', 'in', [force_company, False]),
                               ('operating_unit_id', '=', self.env.user.default_operating_unit_id.id)],
                              order='company_id')
        if not seq_ids:
            _logger.debug(
                "No ir.sequence has been found for code '%s'. Please make sure a sequence is set for current company." % sequence_code)
            return False

        if len(seq_ids) > 1:
            new_seq_ids = self.search([('code', '=', sequence_code),
                                       ('company_id', 'in', [force_company, False]),
                                       ('operating_unit_id','=', self.env.user.default_operating_unit_id.id)],
                                      order='company_id')

            if not new_seq_ids:
                seq_ids = new_seq_ids

        seq_id = seq_ids[0]
        res = seq_id._next()
        # res_val = res.replace('OU', self.env.user.default_operating_unit_id.code)
        return res