from odoo.addons.web_pjms.hooks import _ensure_categories
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    website = env['website'].search([('name', '=', 'PJMS')], limit=1)
    if website:
        _ensure_categories(env, website)
