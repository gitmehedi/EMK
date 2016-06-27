from openerp import models, fields, api, exceptions


class ConfigureEmpChecklist(models.Model):
    _name = "hr.checklist.employees"

    checklist_item_ids= fields.Many2many('hr.exit.checklist.item')