from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator

class ChecklistItem(models.Model):
    _name='hr.exit.checklist.item'

    # Model Fields
    name=fields.Char(string='Item Name', size=100, required=True, help='Please enter name.')
    description=fields.Text(string='Description', size=500, help='Please enter description.')
    is_active=fields.Boolean(string='Active', default=True)

    # Relational Fields
    checklist_type=fields.Many2one('hr.exit.checklist.type', ondelete='set null',
                                   string='Checklist Type', required=True, help='Please select checklist type.')
    #checklist_status_item_ids = fields.One2many('hr.checklist.status','checklist_status_item_id', string='Checklist Status')

    checklist_item_id = fields.Many2one('hr.exit.configure.checklists.line')

    # keeper=fields.Many2one('hr.employee', ondelete='set null', string='Item Keeper', required=True,
    #                        help='Please enter item keeper name.')
    #


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
        return super(ChecklistItem, self).create(vals)

    @api.multi
    def write(self, vals):
        self._check_illegal_char(vals)
        self.check_duplicate(vals)
        name_value = vals.get('name', False)
        if name_value:
            vals['name'] = name_value.strip()
        return super(ChecklistItem, self).write(vals)
