from odoo import fields, models


class ProductRibbon(models.Model):
    _inherit = 'product.ribbon'

    tipo = fields.Char(
        string='Tipo',
        help='Clasificación interna de la cinta. Usa "nuevo" para que el producto '
             'aparezca en la sección Nuevos Ingresos del sitio PJMS.',
    )
