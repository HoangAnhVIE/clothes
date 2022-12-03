from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ClothesBillDetails(models.Model):
    _name = 'clothes.bill.details'
    _description = 'Clothes Bill Details'

    product_id = fields.Many2one('clothes.product',string="Products", compute='_compute_product')
    bill_id = fields.Many2one('clothes.bill', string='Bills')
    category_id = fields.Many2one('clothes.product.category', string='Product')
    warehouse_id = fields.Many2one('clothes.warehouse', string='Warehouses')
    quantity = fields.Integer(string="Quantity", default=1)
    image = fields.Binary(related='category_id.image' , compute ='_compute_img')
    sold = fields.Integer(string='Sold', related='category_id.sold')
    size = fields.Selection([
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL')
    ], string='Size', default='m')
    color = fields.Selection([
        ('red', 'Red'),
        ('black', 'Black'),
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('yellow', 'Yellow'),
        ('white', 'White'),
    ], string='Color', default='black')
    warehouse = fields.Integer(string='Warehouse', related='product_id.quantity')
    price = fields.Monetary(string='Price', related='category_id.fixed_price')
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]).id,readonly=True)
    total_bill_details = fields.Monetary(string="Total Price", currency_field='currency_id',compute='_compute_total_bill_details')

    @api.depends('quantity', 'price')
    def _compute_total_bill_details(self):
        for rec in self:
            rec.total_bill_details = rec.quantity * rec.price

    @api.depends('category_id','size', 'color',)
    def _compute_product(self):
        for rec in self:
            rec.product_id = self.env['clothes.product'].search([('category_id', '=', rec.category_id.name), ('size', '=', rec.size), ('color', '=', rec.color),])