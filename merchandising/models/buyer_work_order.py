from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from Crypto.Util.number import size
from duplicity.tempdir import default
from datetime import date
from curses.has_key import has_key


class BuyerWorkOrder(models.Model):
    _inherit = 'sale.order'
    
    """ Buyer Work Order fields """
    bwo_ref_no = fields.Char(string="Reference No", size=20, required=True)
    epo_date = fields.Date(string="Date", required=True, default=date.today().strftime('%Y-%m-%d'),
                           readonly=True, states={'draft':[('readonly', False)]})
    
    """ Temporary fields """

    production_qty = fields.Float(string='Production Quantity', digits=(15, 2),
                                  readonly=True, states={'draft':[('readonly', False)]})
    delay = fields.Float(string='Delay', digits=(15, 2),
                        readonly=True, states={'draft':[('readonly', False)]})
    color = fields.Char(default='#c7d5ff')

    hs_code = fields.Char(string='HS Code', size=20, required=True,
                          readonly=True, states={'draft':[('readonly', False)]})
    tolerance = fields.Float(string='Tolerance (%)', digits=(3, 2),
                             readonly=True, states={'draft':[('readonly', False)]})
    remarks = fields.Text(string='Remarks',
                          readonly=True, states={'draft':[('readonly', False)]})
    
    """ Relationship fields """
    product_template_id = fields.Many2one('product.template', string='Product', required=True,
                                          readonly=True, states={'draft':[('readonly', False)]}) 
    partner_id = fields.Many2one('res.partner', string="Buyer", required=True,
                               domain=[('customer', '=', 'True')],
                               readonly=True, states={'draft':[('readonly', False)]})
    season_id = fields.Many2one('res.season', string="Season",
                                readonly=True, states={'draft':[('readonly', False)]})  
    year_id = fields.Many2one('account.fiscalyear', string="Year", required=True,
                              readonly=True, states={'draft':[('readonly', False)]})
    style_id = fields.Many2one('product.style', string="Style", required=True,
                              domain=[('version', '=', '1'), ('state', '=', 'confirm')],
                              readonly=True, states={'draft':[('readonly', False)]})
    # style_id = fields.Many2one('product.style', string="Style No", required=True,
    #                             states={'draft': [('readonly', False)]},
    #                            domain=[('visible', '=', 'True'), ('state', '=', 'confirm')])
    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  readonly=True, states={'draft':[('readonly', False)]})
    delivery_term_id = fields.Many2one('delivery.term', string="Delivery Term",
                                       readonly=True, states={'draft':[('readonly', False)]})
    department_id  = fields.Many2one('merchandising.dept', string="Department", required=True,
                                       readonly=True, states={'draft':[('readonly', False)]})
       
    """ All calculative fields in here """

    shipment_date = fields.Date(compute='_compute_com_ship_date', string="Shipment Date")
    buyer_inspection_date = fields.Date(compute='_compute_com_buyer_inspection_date', string="Buyer Inspection Date")
    inhouse_inspection_date = fields.Date(compute='_compute_com_inhouse_inspection_date', string="In House Insspection Date",)
    total_quantity = fields.Float(compute='_compute_com_quantity', string="Order Quantity")
    production_ratio = fields.Float(compute='_compute_production_ratio', store=True)
    style_ref_code = fields.Char(compute='_compute_style_ref_code', store=True)

    shipment_mode = fields.Selection([("sea", "Sea"), ("air", "Air"), ("road", "By Road")], string='Ship Mode', required=True,
                                     readonly=True, states={'draft':[('readonly', False)]})
    
    """ One to Many Relationship """

    bwo_shipment_ids = fields.One2many('bwo.shipment.details', 'bwo_details_id', ondelete='CASCADE',
                                       readonly=True, states={'draft':[('readonly', False)]})

    bwo_destination_ids = fields.Many2many('shipping.destination', string="Destination",
                                           readonly=True, states={'draft':[('readonly', False)]})


    
    """ State fields for containing vaious states """
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    
    """ All kinds of validation message """
    @api.multi
    def _validate_data(self, value):
        msg , filterInt, filterNum, filterChar = {}, {}, {}, {}
        
        filterInt['Tolerance'] = value.get('tolerance', False)
        filterInt['Delay'] = value.get('delay', False)

        msg.update(validator._validate_percentage(filterInt))
        msg.update(validator._validate_number(filterNum))
        validator.validation_msg(msg)
        
        return True
    
    
    """ All function which process data and operation """
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        # vals['name'] = self.env['ir.sequence'].get('mso')
            
        return super(BuyerWorkOrder, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(BuyerWorkOrder, self).write(vals)

    @api.multi
    @api.depends('name', 'bwo_ref_no')
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '[%s] %s' % (record.name, record.bwo_ref_no)))
        return result
    
    """ onchange fields """

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res, ids = {}, []
        self.style_id = 0
        self.department_id = 0

        if self.partner_id:
            for obj in self.partner_id.styles_ids:
                if obj.version==1 and obj.state == 'confirm':
                   ids.append(obj.id)

        res['domain'] = {
                    'style_id':[('id', 'in', ids)],
                }
        
        return res

    @api.onchange('style_id')
    def _onchange_style_id(self):
        res = {'domain': {'season_id':[]}}

        if self.style_id:
            res['domain'] = {
                    'season_id':[('id', 'in', [self.style_id.season_id.id])]
            }
        return res

    """ All computed fields """

    def _compute_com_ship_date(self):
        for record in self:
            if record.bwo_shipment_ids:
                record.shipment_date = min(qty.shipment_date for qty in record.bwo_shipment_ids)
                
    def _compute_com_buyer_inspection_date(self):
        for record in self:
            if record.bwo_shipment_ids:
                record.buyer_inspection_date = min(qty.buyer_inspection_date for qty in record.bwo_shipment_ids)

    @api.depends('style_id')
    def _compute_style_ref_code(self):
        for record in self:
            if record.style_id:
                record.style_ref_code = self.style_id.name

                
    def _compute_com_inhouse_inspection_date(self):
        for record in self:
            if record.bwo_shipment_ids:
                record.inhouse_inspection_date = min(qty.in_house_inspection_date for qty in record.bwo_shipment_ids)
    @api.one            
    def _compute_com_quantity(self):
        
        for record in self:
            if record.order_line:
                record.total_quantity = sum(qty.qty for qty in record.order_line)
            else:
                record.total_quantity = 0.00
                
    def _compute_production_ratio(self):
        for record in self:
            if (record.total_quantity and record.production_qty):
                record.production_ratio = (record.production_qty / record.total_quantity) * 100              
                record.production_ratio = round(record.production_ratio, 2)
            else:     
                record.production_ratio = 0.00
  
    
    def calculate_bwo_prod_attr(self):
        valueList = {}
         
        if self.order_line:
            for prod in self.order_line:
                for id in prod.product_id.attribute_value_ids.ids:
                    if valueList.has_key(id):
                        valueList[id] = valueList[id] + prod.qty
                    else:
                        valueList[id] = prod.qty   
          
  
        for attr_val in valueList:
               
            vals = {
                'bwo_id': self.id,
                'name': 'Bangladesh',
                'attr_ids': attr_val,
                'quantity': valueList[attr_val],
            }
               
            if self.bwo_prod_attr_sum_ids:

                if attr_val in self._get_sum_attr_ids():
                    for wr in self.bwo_prod_attr_sum_ids:
                        if wr.attr_ids.id == attr_val:
                            wr.write({'quantity': vals['quantity'] })
                           
                else:
                    self.bwo_prod_attr_sum_ids.create(vals)    
            else:
                self.bwo_prod_attr_sum_ids.create(vals)
    
    def _get_attr_val_list(self, attr=False):
        prod_attr_val = {}
        prod_attr_obj = self.env['product.attribute']
        
        if self.order_line:
            for prod in self.order_line:
                for id in prod.product_id.attribute_value_ids.ids:
                    if prod_attr_val.has_key(id):
                        prod_attr_val[id] = prod_attr_val[id] + prod.qty
                    else:
                        prod_attr_val[id] = prod.qty
        
        if attr == 'color':
            value_ids = prod_attr_obj.search([('is_color', '=', True)]).value_ids.ids
        elif attr == 'size':    
            value_ids = prod_attr_obj.search([('is_size', '=', True)]).value_ids.ids
        
                
        if value_ids:
            for val in prod_attr_val.keys():
                if val not in value_ids:
                    del prod_attr_val[val]
        
        return prod_attr_val
    
                

    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        res = self.write({'color':'#c7d5ff'})
        
    @api.multi    
    def action_confirm(self):
        res = self.write({'state':'confirm', 'color':'#53F57C'})
        return res
    
    
    def _get_sum_attr_ids(self):
        sum = []
        for val in self.bwo_prod_attr_sum_ids:
            sum.append(val.attr_ids.id)
        
        return sum    



     
    
    


        
        
            
    
