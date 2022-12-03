from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ClothesSupplier(models.Model):
    _name = 'clothes.supplier'
    _description = 'Clothes Supplier'

    import_product_ids = fields.One2many('clothes.import.product', 'supplier_id', string='Import Products')
    name = fields.Char(string="Name")
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Char(String='Address')
    image = fields.Binary(string='Image', attachment=True, help='Image')