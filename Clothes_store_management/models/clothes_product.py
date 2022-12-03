from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ClothesProduct(models.Model):
    _name = 'clothes.product'
    _description = 'Clothes Product'
    _rec_name = 'product_code'

    product_code = fields.Char(string='Product Code', compute="_compute_product_code")
    category_id = fields.Many2one('clothes.product.category', string='Product', required =True)
    warehouse_ids = fields.One2many('clothes.warehouse','product_id', string="Warehouses")
    bill_details_ids = fields.One2many('clothes.bill.details', 'product_id',string='Bill Details')
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]).id,readonly=True)
    size = fields.Selection([
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL')
    ], string='Size')
    color = fields.Selection([
        ('red', 'Red'),
        ('black', 'Black'),
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('yellow', 'Yellow'),
        ('white', 'White'),
    ], string='Color',)
    image = fields.Binary(string='Image', attachment=True, help='Image', related = 'category_id.image', readonly = False)
    fixed_price = fields.Monetary(string='Price Fixed', currency_field='currency_id', related ='category_id.fixed_price')
    quantity = fields.Integer(string='Warehouse', compute='_compute_quantity',)
    sold = fields.Integer(string='Sold', compute='_compute_sold')
    available = fields.Boolean(default=False, string="Available", compute='_compute_available')

    @api.depends('category_id', 'size', 'color')
    def _compute_product_code(self):
        for rec in self:
            if rec.category_id and rec.size and rec.color:
                rec.product_code = rec.category_id.name+" ("+str(rec.size)+", "+str(rec.color)+")"
            else:
                rec.product_code = rec.category_id.name

    @api.depends('warehouse_ids.inventory')
    def _compute_quantity(self):
        for rec in self:
            if rec.warehouse_ids:
                rec.quantity = rec.warehouse_ids.inventory
            else:
                rec.quantity = 0

    @api.depends('warehouse_ids.export_quantity')
    def _compute_sold(self):
        for rec in self:
            if rec.warehouse_ids:
                rec.sold = rec.warehouse_ids.export_quantity
            else:
                rec.sold = 0

    @api.depends('quantity')
    def _compute_available(self):
        for rec in self:
            if rec.quantity == 0:
                rec.available = False
            else:
                rec.available = True

    _sql_constraints = [
        ('unique_tag_name', 'unique (product_code)', 'Name must be unique')
    ]