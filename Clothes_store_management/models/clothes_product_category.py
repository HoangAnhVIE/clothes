from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ClothesProductCategory(models.Model):
    _name = 'clothes.product.category'
    _description = 'Clothes Product Category'

    name = fields.Char(string='Name', required=True)
    categories_id = fields.Many2one('clothes.category', string='Category')
    product_ids = fields.One2many('clothes.product','category_id', string="Products", readonly =True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]).id,
                                  readonly=True)
    price = fields.Monetary(string='Price', currency_field='currency_id')
    discount = fields.Float(string="Discount %", widget="product_discount")
    fixed_price = fields.Monetary(string='Price Fixed', currency_field='currency_id', )
    sold = fields.Integer(string='Sold', compute='_compute_sold')
    image = fields.Binary(string='Image', attachment=True, help='Image')

    @api.onchange('price', 'discount')
    def _onchange_fixed_price(self):
        for rec in self:
            rec.fixed_price = 0
            if rec.discount != 0:
                rec.fixed_price = ((100 - rec.discount) / 100) * rec.price
            else:
                rec.fixed_price = rec.price

    @api.depends('product_ids.sold')
    def _compute_sold(self):
        for rec in self:
            if rec.product_ids:
                rec.sold = sum(rec.sold for rec in rec.product_ids)
            else:
                rec.sold = 0
