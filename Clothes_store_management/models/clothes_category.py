from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class ClothesCategory(models.Model):
    _name = 'clothes.category'
    _description = 'Clothes Category'

    name = fields.Char(string='Category')