import os, base64

from random import randint
from odoo import api, models, fields, _
from datetime import datetime
from odoo.exceptions import ValidationError


class GBSDataMigration(models.Model):
    _name = 'gbs.data.migration'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _description = "Import File"
    _rec_name = 'code'
    _order = 'id desc'

    code = fields.Char(string='Code', track_visibility='onchange', readonly=True)
    date = fields.Date(string='Date', default=fields.Datetime.now, track_visibility='onchange')
    mismatch_amount = fields.Float(string='Mismatch Values',
                                   track_visibility='onchange')
    file_name = fields.Char(string='File Path')
    upload_file = fields.Binary(string="Generated File", attachment=True)
    state = fields.Selection([('draft', 'Draft'), ('processed', 'Processed')], default='draft', string='Status')


    @api.multi
    def action_process(self):
        if not self.code:
            self.code = self.env['ir.sequence'].next_by_code('salary.file.sequence') or ''

        if self.mismatch_amount != 0:
            debit = format(self.debit, '.2f')
            credit = format(self.credit, '.2f')
            raise ValidationError(_(
                'Debit and Credit value must be same\n - Debit: {0} \n - Credit: {1}'.format(debit, credit)))

        record_date = datetime.strftime(datetime.now(), "%d%m%Y_%H%M%S_")
        process_date = datetime.strftime(datetime.now(), "%d%m%Y_")
        unique = str(randint(100, 999))
        filename = "MDC_00001_" + record_date + process_date + unique + ".txt"

        def generate_file(record):
            file_path = os.path.join(record.source_path, filename)
            with open(file_path, "w+") as file:
                for val in self:
                    if len(val.account_no) == 13:
                        trn_type = '01' if val.type_journal == 'cr' else '51'
                    elif len(val.account_no) == 16:
                        trn_type = '04' if val.type_journal == 'cr' else '54'
                    else:
                        raise (_("Account contains invalid value"))

                    account_no = str(val.account_no).zfill(17)
                    amount = format(val.debit, '.2f') if val.debit > 0 else format(val.credit, '.2f')
                    amount = ''.join(amount.split('.')).zfill(16)
                    narration = val.narration[:50]
                    trn_ref_no = ''.join(self.code.split('/'))[-8:]
                    date_array = val.date if val.date else fields.Datetime.now()[:10]
                    date_array = date_array.split("-")
                    cost_centre = '0000'
                    if date_array:
                        date = date_array[2] + date_array[1] + date_array[0]
                    record = "{:2s}{:17s}{:16s}{:50s}{:8s}{:8s}{:4s}\r\n".format(trn_type, account_no, amount,
                                                                                 narration,
                                                                                 trn_ref_no, date, cost_centre)
                    file.write(record)
                    val.write({'state': 'done'})
                self.write({'state': 'processed'})

            if os.stat(file_path).st_size == 0:
                os.remove(file_path)
            return True if os.path.exists(file_path) else False

        for rec in self.env['generate.cbs.journal'].search([('method', '=', 'sftp')]):
            with rec.sftp_connection('destination') as destination:
                dirs = [rec.folder, rec.source_path, rec.dest_path]
                self.directory_check(dirs)
                start_date = fields.Datetime.now()
                file = generate_file(rec)

                dest_path = os.path.join(rec.dest_path, filename)
                local_path = os.path.join(rec.source_path, filename)

                if file:
                    if destination.put(local_path, dest_path):
                        with open(local_path, "rb") as cbs_file:
                            encoded_file = base64.b64encode(cbs_file.read())
                        stop_date = fields.Datetime.now()
                        success = self.write({'upload_file': encoded_file,
                                              'file_name': filename})

                        if success:
                            os.remove(local_path)
                        else:
                            continue
                    else:
                        continue

    @api.one
    def directory_check(self, dirs):
        for dir in dirs:
            if not os.path.isdir(dir):
                try:
                    os.makedirs(dir)
                except OSError:
                    pass

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'processed':
                raise ValidationError(_('Processed record can not be deleted.'))
        return super(GBSDataMigration, self).unlink()

