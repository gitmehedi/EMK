from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class IrSequenceOperatingUnit(models.Model):
    _inherit = 'ir.sequence'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.model
    def next_by_code(self, sequence_code):
        """ Draw an interpolated string using a sequence with the requested code.
            If several sequences with the correct code are available to the user
            (multi-company cases), the one from the user's current company will
            be used.

            :param dict context: context dictionary may contain a
                ``force_company`` key with the ID of the company to
                use instead of the user's current company for the
                sequence selection. A matching sequence for that
                specific company will get higher priority.
        """
        self.check_access_rights('read')
        force_company = self._context.get('force_company')
        if not force_company:
            force_company = self.env.user.company_id.id

        seq_ids = self.search([('code', '=', sequence_code),
                               ('company_id', 'in', [force_company, False])],
                              order='company_id')
        if not seq_ids:
            _logger.debug(
                "No ir.sequence has been found for code '%s'. Please make sure a sequence is set for current company." % sequence_code)
            return False

        if len(seq_ids) > 1 and self.env.user.default_operating_unit_id:
            new_seq_ids = self.search([('code', '=', sequence_code),
                                       ('company_id', 'in', [force_company, False]),
                                       ('operating_unit_id','=', self.env.user.default_operating_unit_id.id)],
                                      order='company_id')

            if not new_seq_ids:
                seq_ids = new_seq_ids

        seq_id = seq_ids[0]
        res = seq_id._next()
        res_val = res.replace('OU', self.env.user.default_operating_unit_id.code)
        return res_val