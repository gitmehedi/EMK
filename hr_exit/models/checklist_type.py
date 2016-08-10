from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ChecklistType(models.Model):
    _name = 'hr.exit.checklist.type'

    # Model Fields
    code = fields.Char(string='Code', size=10, help='Please enter code.', required=True)
    name = fields.Char(string='Name', size=100, required=True, help='Please enter name.')
    description = fields.Text(string='Description', size=500, help='Please enter description')
    is_active = fields.Boolean(string='Active', default=True)

    @api.multi
    def _check_illegal_char(self, value):
        values = {}
        if (value.get('name', False)):
            values['Size'] = (value.get('name', False))

        check_space = validator._check_space(self, values, validator.msg)
        check_special_char = validator._check_special_char(self, values, validator.msg)
        validator.generate_validation_msg(check_space, check_special_char)
        return True

    @api.multi
    def check_duplicate(self, value):
        records = self.search_read([], ['name'])
        check_val = {}
        field_val = ''
        field_name = ''

        if (value.get('name', False)):
            check_val['name'] = (value.get('name', False))

        for value in check_val:
            field_val = check_val[value]
            field_name = value

        check_duplicate = validator._check_duplicate_data(self, field_val, field_name, records, validator.msg)
        validator.generate_validation_msg(check_duplicate, "")
        return True

    @api.model
    def create(self, vals):
        self._check_illegal_char(vals)
        self.check_duplicate(vals)
        name_value = vals.get('name', False)
        if name_value:
            vals['name'] = name_value.strip()
        return super(ChecklistType, self).create(vals)

    @api.multi
    def write(self, vals):
        self._check_illegal_char(vals)
        self.check_duplicate(vals)
        name_value = vals.get('name', False)
        if name_value:
            vals['name'] = name_value.strip()
        return super(ChecklistType, self).write(vals)

    _sql_constraints = [
        ('_check_code_uniq', 'unique(code)', "Code already exists!"),
    ]
