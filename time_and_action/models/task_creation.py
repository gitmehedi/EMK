from openerp import models, fields, api, exceptions


class TaskCreation(models.Model):
    """
    Task Creation
    """
    _name = 'task.creation'

    """ mandatory and Optional Fields """
    name = fields.Char(string="Serial", size=30, readonly=True)
    tc_code = fields.Char(string='Code')

    task_name = fields.Char(string='Task Name')
    milestone_task = fields.Boolean(string='Milestone Task', default=False)

    remarks = fields.Text(string='Remarks')

    """ many2one relationship """
    related_process_id= fields.Many2one('related.process',string="Related Process")
    related_sub_process_id = fields.Many2one('related.process',string="Related Sub Process")

    task_related_to= fields.Selection([('export_po', "Export PO")], string='Task Related To')
    task_type= fields.Selection([('pre_production', "Pre Production"),('post_production', "Post Production")], string='Task Type')

    """ dependency related fields """
    independent = fields.Selection([('independent', "Independent"), ('pre_defined_event_date', "Predefined Event Date"),
                                    ('pressiding_task_dependent', "Pressiding Task Dependent")])
    independent_standard_duration = fields.Float(string='Standard Duration')

    # pre_defined_event_date = fields.Boolean(string='Predefined Event Date')
    pre_defined_lag_days = fields.Float(string='Lag Days')
    backward_forward = fields.Selection([('backward', "Backward"), ('forward', "Forward")])
    event_date = fields.Selection([('shipment_date', "shipment_date")],string='Event Date')
    pre_defined_standard_duration = fields.Float(string='Standard Duration')

    # pressiding_task_dependent = fields.Boolean(string='Pressiding Task Dependent')
    dependent_lag_days = fields.Float(string='Lag Days')
    dependent_backward_forward = fields.Selection([('ss', "S-S"), ('es', "E-S")])
    dependent_standard_duration = fields.Float(string='Standard Duration')

    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')

    """ One2many relationships """



    """ All function which process data and operation """

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('tc_code')

        return super(TaskCreation, self).create(vals)

    @api.multi
    def write(self, vals):
#         self._validate_data(vals)

        return super(TaskCreation, self).write(vals)


    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirm'














