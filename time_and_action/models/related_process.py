from openerp import models, fields, api, exceptions


class TaskCreation(models.Model):
    """
    Task Creation
    """
    _name = 'related.process'

    """ mandatory and Optional Fields """

    name = fields.Char(string='Name')
    remarks = fields.Text(string='Remarks')

    @api.model
    def create(self, vals):

        return super(TaskCreation, self).create(vals)

    @api.multi
    def write(self, vals):

        return super(TaskCreation, self).write(vals)














