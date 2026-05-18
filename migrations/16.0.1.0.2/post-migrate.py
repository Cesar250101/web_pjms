from odoo.addons.web_pjms.hooks import _ensure_categories, _ensure_category_menus
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    website = env['website'].search([('name', '=', 'PJMS')], limit=1)
    if not website:
        return

    _ensure_categories(env, website)
    _ensure_category_menus(env, website)

    # Fijar keys de vistas de páginas PJMS para que coincidan con sus xmlids
    page_keys = {
        'pj_contacto_page': 'web_pjms.pj_contacto_page',
        'pj_home': 'web_pjms.pj_home',
    }
    for xml_name, correct_key in page_keys.items():
        data = env['ir.model.data'].search([
            ('module', '=', 'web_pjms'),
            ('name', '=', xml_name),
            ('model', '=', 'ir.ui.view'),
        ], limit=1)
        if data:
            view = env['ir.ui.view'].browse(data.res_id)
            if view.key != correct_key:
                cr.execute("UPDATE ir_ui_view SET key=%s WHERE id=%s", (correct_key, view.id))
            if view.website_id.id != website.id:
                cr.execute("UPDATE ir_ui_view SET website_id=NULL WHERE id=%s", (view.id,))
