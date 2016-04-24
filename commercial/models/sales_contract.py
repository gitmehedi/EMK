from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator,utility
from datetime import date


class SalesContract(models.Model):
    """ Buyer sends sales coantract as a confirmaiton of the export order. 
    Merchandiser receives the sales contract and takes necessary steps """
    
    _name = 'sales.contract'
    
    """ All required and optional fields """
    name = fields.Char(string="Serial", size=30, readonly=True)
    sc_code = fields.Char(string='Code')
    sc_date = fields.Date(string="SC Date", required=True, default=date.today().strftime('%Y-%m-%d'),
                          readonly=True, states={'draft':[('readonly', False)]})
    sc_no = fields.Char(string="SC No", size=30, required=True,
                        readonly=True, states={'draft':[('readonly', False)]})
    sc_value = fields.Float(string='SC Value', digits=(15, 2), required=True,
                            readonly=True, states={'draft':[('readonly', False)]})
    inco_term_place = fields.Char(string="Inco Term Place", size=30,
                                  readonly=True, states={'draft':[('readonly', False)]})
    
    
    remarks = fields.Text(string='Remarks',readonly=True,
                          states={'draft':[('readonly', False)]})
    
    """ Relationship fields """
    buyer_id = fields.Many2one('res.partner', string="Buyer", required=True,domain=[('customer', '=', 'True')],
                               readonly=True, states={'draft':[('readonly', False)]})
    sc_bank_id = fields.Many2one('res.bank', string="SC Bank",required=True,
                                 readonly=True, states={'draft':[('readonly', False)]})
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms/Tenor",required=True,
                                      readonly=True, states={'draft':[('readonly', False)]})
    sc_currency_id = fields.Many2one('res.currency', required=True,
                                     readonly=True, states={'draft':[('readonly', False)]}, default=lambda self: self._set_default_currency('USD'))
    
    inco_term = fields.Many2one('stock.incoterms', string="Inco Term", required=True,
                                readonly=True, states={'draft':[('readonly', False)]})
    
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    """ One2many relationships """
    sales_contract_details_ids = fields.One2many('sales.contract.details', 'sales_contract_id')

    so_ids = fields.Many2many('sale.order','sc_id',  string="Related PO", required=True,
                              readonly=True, states={'draft':[('readonly', False)]})
    
    
    """ All kinds of validation message """
    @api.multi
    def _validate_data(self, value):
        msg , filterChar, filterNum = {}, {}, {}
        filterChar['SC No'] = value.get('sc_no', False)
        filterNum['SC Value'] = value.get('sc_value', False)

        msg.update(validator._validate_number(filterNum))
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
        
        return True

    def _set_default_currency(self, name):
        res = self.env['res.currency'].search([('name', '=like', name)])
        return res and res[0] or False
    
    
    """ All function which process data and operation """
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = self.env['ir.sequence'].get('sc_code')
            
        return super(SalesContract, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(SalesContract, self).write(vals)      

    """ Onchange functionality """

    @api.onchange('buyer_id')
    def _onchange_buyer_id(self):
        res,domain_ids= {},[]
        self.so_ids=0

        if self.buyer_id:
            bwo_obj = self.env['sale.order'].search([('partner_id','=',self.buyer_id.id)])
            sc_obj = self.env['sales.contract'].search([('buyer_id','=',self.buyer_id.id)])

            if sc_obj:
                ids=[]
                for obj in sc_obj:
                    for id in obj.so_ids.ids:
                        ids.append(id)

                domain_ids = list(set(bwo_obj.ids)-set(ids))

        res['domain'] = {
            'so_ids':[('id', 'in', domain_ids)]
        }
        return res

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi    
    def action_confirm(self):
        self.state = 'confirm'
        
      



     
    
    


        
        
            
    
