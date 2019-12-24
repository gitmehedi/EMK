import os, base64, re

from random import randint
from odoo import api, models, fields, _
from datetime import datetime
from odoo.exceptions import ValidationError


class GBSFileImport(models.Model):
    _name = 'gbs.file.import'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _description = "Import File"
    _rec_name = 'code'
    _order = 'id desc'

    code = fields.Char(string='Code', track_visibility='onchange', readonly=True)
    date = fields.Date(string='Date', default=fields.Datetime.now, track_visibility='onchange')
    debit = fields.Float(compute='_compute_debit', string='Debit', track_visibility='onchange')
    credit = fields.Float(compute='_compute_debit', string='Credit', track_visibility='onchange')
    mismatch_amount = fields.Float(compute='_compute_debit', string='Mismatch Values',
                                   track_visibility='onchange')
    import_lines = fields.One2many('gbs.file.import.line', 'import_id', readonly=True,
                                   states={'draft': [('readonly', False)]})
    file_name = fields.Char(string='File Path')
    upload_file = fields.Binary(string="Generated File", attachment=True)
    state = fields.Selection([('draft', 'Draft'), ('processed', 'Processed')], default='draft', string='Status')

    @api.multi
    @api.depends('import_lines')
    def _compute_debit(self):
        for rec in self:
            rec.debit = float(sum([val.debit for val in rec.import_lines]))
            rec.credit = float(sum([val.credit for val in rec.import_lines]))
            rec.mismatch_amount = float(rec.debit - rec.credit)

    @api.multi
    def action_process(self):
        if not self.code:
            self.code = self.env['ir.sequence'].next_by_code('salary.file.sequence') or ''

        if self.mismatch_amount != 0:
            debit = format(self.debit, '.2f')
            credit = format(self.credit, '.2f')
            raise ValidationError(_(
                'Debit and Credit value must be same\n - Debit: {0} \n - Credit: {1}'.format(debit, credit)))

        filename = self.generate_filename()

        def generate_file(record):
            file_path = os.path.join(record.source_path, filename)
            with open(file_path, "w+") as file:
                for val in self.import_lines:
                    if len(val.account_no) == 13:
                        trn_type = '01' if val.type_journal == 'cr' else '51'
                    elif len(val.account_no) == 16:
                        trn_type = '04' if val.type_journal == 'cr' else '54'
                    else:
                        raise (_("Account contains invalid value"))

                    account_no = str(val.account_no).zfill(17)
                    amount = format(val.debit, '.2f') if val.debit > 0 else format(val.credit, '.2f')
                    amount = ''.join(amount.split('.')).zfill(16)
                    narration = re.sub(r'[|\n||\r|?|$|.|!]', r' ', val.narration[:50])
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

        for rec in self.env['server.file.process'].search(
                [('method', '=', 'dest_sftp'), ('type', '=', 'batch'), ('status', '=', True)], limit=1):
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

                        # success = self.env['generate.cbs.journal.success'].create({'name': filename,
                        #                                                            'start_date': start_date,
                        #                                                            'stop_date': stop_date,
                        #                                                            'upload_file': encoded_file,
                        #                                                            'file_name': filename,
                        #                                                            })
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
        return super(GBSFileImport, self).unlink()

    def generate_filename(self):
        rec_date = self.env.user.company_id.batch_date.split('-')
        record_date = "{0}{1}{2}_".format(rec_date[2], rec_date[1], rec_date[0]) + datetime.strftime(datetime.now(),
                                                                                                     "%H%M%S_")
        process_date = "{0}{1}{2}_".format(rec_date[2], rec_date[1], rec_date[0])
        unique = str(randint(100, 999))
        return "MDC_00001_" + record_date + process_date + unique + ".txt"


class GBSFileImportLine(models.Model):
    _name = 'gbs.file.import.line'

    name = fields.Char(string='Name')
    account_no = fields.Char(string='Account No', required=True)
    narration = fields.Char(string='Narration', required=True)
    date = fields.Date(string='Date', default=fields.Datetime.now, readonly=True)
    debit = fields.Float(string='Debit', )
    credit = fields.Float(string='Credit')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft', string='Status')
    type_journal = fields.Selection([
        ('cr', 'CR'),
        ('dr', 'DR'),
    ], string='Type', required=True)

    import_id = fields.Many2one('gbs.file.import', 'Import Id', ondelete='cascade')

    @api.constrains('account_no', 'type_journal', 'debit', 'credit')
    def _check_unique_constrain(self):
        if self.account_no or self.debit or self.credit:
            if not self.account_no.isdigit():
                raise ValidationError('Account No should be number!')
            if len(self.account_no) not in [13, 16]:
                raise ValidationError(
                    "Account [{0}] has invalid value. Account will be 13 or 16 digit.".format(self.account_no))
