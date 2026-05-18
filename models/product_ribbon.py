from odoo import fields, models


class ProductRibbon(models.Model):
    _inherit = 'product.ribbon'

    tipo = fields.Selection(
        selection_add=[
            ('mas_vendidos', 'Más Vendidos'),
            ('especial',     'Especial'),
            ('en_descuento', 'En Descuento'),
            ('otros',        'Otros'),
        ],
        ondelete={
            'mas_vendidos': 'set null',
            'especial':     'set null',
            'en_descuento': 'set null',
            'otros':        'set null',
        },
    )
