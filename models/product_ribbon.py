from odoo import fields, models


class ProductRibbon(models.Model):
    _inherit = 'product.ribbon'

    tipo = fields.Selection(
        selection=[
            ('nuevo',        '¡Nuevo!'),
            ('mas_vendidos', 'Más Vendidos'),
            ('especial',     'Especial'),
            ('en_descuento', 'En Descuento'),
            ('otros',        'Otros'),
        ],
        string='Tipo de cinta',
        help='Clasifica la cinta para filtrar productos en secciones del sitio PJMS.',
    )
