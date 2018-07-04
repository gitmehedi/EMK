from odoo import models, fields, api, exceptions

class ConfigureEmpChecklist(models.Model):
    _name = "hr.emp.master.checklists"

    config_checklist_id = fields.Many2one('hr.exit.configure.checklists','Checklist',required= True)
    employee_id = fields.Many2one('hr.employee',string='Employee', select=True, required= True, invisible=False)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id')
    responsible_userdepartment_id = fields.Many2one('hr.department', string='Responsible Department',related='config_checklist_id.responsible_userdepartment_id')
    responsible_username_id = fields.Many2one('hr.employee', string='Responsible User',related='config_checklist_id.responsible_username_id')
    checklist_status_ids = fields.One2many('hr.checklist.status', 'checklist_status_id')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('send', 'Send'), ('verify', 'Verified')],
                             readonly=True, copy=False,
                             default='draft')
    responsible_type=fields.Selection(selection=[('department', 'Department'),('individual','Individual')],related='config_checklist_id.responsible_type')
    remarks= fields.Text('Remarks',required=True)


    @api.onchange('config_checklist_id')
    def on_change_config_checklist_id(self):
        vals = []
        if self.config_checklist_id:
            confg_checklist_obj = self.env['hr.exit.configure.checklists'].search(
                [('id', '=', self.config_checklist_id.id)])
            for record in confg_checklist_obj:
                for config in record.checklists_ids:
                    vals.append((0, 0, {
                                        'checklist_status_item_id': config.checklist_item_id,
                                        'checklist_type_id': config.checklist_type,


                                        }))
                    self.checklist_status_ids = vals

    @api.multi
    def check_list_verify(self):
        exit_req_obj = self.env['hr.emp.exit.req'].search(
            [('employee_id', '=', self.employee_id.id)])
        for exit_line in exit_req_obj.checklists_ids:
            if exit_line.responsible_department == self.responsible_userdepartment_id or exit_line.responsible_emp == self.responsible_username_id:
                exit_line.remarks = self.remarks
                exit_line.write({'state': 'received'})
        return self.write({'state': 'verify'})

    # @api.onchange('config_checklist_id')
    # def on_change_config_checklist_id(self):
    #     vals = []
    #     # self.required_date = self.indent_ids.required_date
    #     for indent_id in self.indent_ids:
    #         indent_product_line_obj = self.env['indent.product.lines'].search([('indent_id', '=', indent_id.id)])
    #         for indent_product_line in indent_product_line_obj:
    #             vals.append((0, 0, {'product_id': indent_product_line.product_id,
    #                                 'name': indent_product_line.name,
    #                                 'product_uom_id': indent_product_line.product_uom,
    #                                 'product_ordered_qty': indent_product_line.product_uom_qty,
    #                                 'product_qty': indent_product_line.qty_available,
    #                                 }))
    #             self.line_ids = vals


    @api.multi
    def check_list_submit(self):
        return self.write({'state': 'done'})

    @api.multi
    def check_list_reset(self):
        return self.write({'state': 'draft'})

    @api.multi
    def check_list_send(self):
        return self.write({'state': 'send'})

    # @api.multi
    # def check_list_verify(self):
    #     return self.write({'state': 'verify'})


    @api.multi
    def _compute_check(self):
        return 1





