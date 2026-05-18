import base64
import os
from odoo import api, SUPERUSER_ID

# Directorio de imágenes de categorías (relativo al módulo)
_IMG_DIR = os.path.join(os.path.dirname(__file__), 'static', 'src', 'img', 'categories')


def _load_image(filename):
    """Lee una imagen del módulo y la devuelve en base64, o None si no existe."""
    path = os.path.join(_IMG_DIR, filename)
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return None


# Estructura de categorías PJMS extraída de pjms.cl
# Formato: (nombre, secuencia, imagen, [(nombre_hijo, secuencia), ...])
PJMS_CATEGORIES = [
    ('Básicos',      10, 'basicos.jpg',  [
        ('Dos piezas',       1),
        ('Camisas de Dormir', 2),
    ]),
    ("Verano '24",   20, 'verano.jpg',   [
        ('Short y Polera',            1),
        ('Short y camisas manga corta', 2),
        ('Pantalón y polera',          3),
        ('Camisas de dormir',          4),
    ]),
    ("Invierno '23", 30, 'invierno.jpg', [
        ('Camisolas',  1),
        ('Dos piezas', 2),
    ]),
    ('Material',     40, 'material.jpg', [
        ('Algodón Pima',   1),
        ('Viscosa',        2),
        ('Modal',          3),
        ('Viscosa Lino',   4),
        ('Piel de Durazno', 5),
    ]),
    ('SALE',         50, 'sale.jpg',     []),
]


def _ensure_categories(env, website):
    """Crea categorías PJMS con imagen si no existen. No duplica."""
    Cat = env['product.public.category']
    # Si ya existen categorías padre para este website, no tocar nada
    existing = Cat.search([('parent_id', '=', False), ('website_id', '=', website.id)], limit=1)
    if existing:
        return

    for parent_name, parent_seq, img_file, children in PJMS_CATEGORIES:
        parent = Cat.search([
            ('name', '=', parent_name),
            ('parent_id', '=', False),
            ('website_id', '=', website.id),
        ], limit=1)

        img_b64 = _load_image(img_file)
        parent_vals = {'sequence': parent_seq}
        if img_b64:
            parent_vals['image_1920'] = img_b64

        if not parent:
            parent_vals.update({
                'name': parent_name,
                'website_id': website.id,
            })
            parent = Cat.create(parent_vals)
        else:
            parent.write(parent_vals)

        for child_name, child_seq in children:
            child = Cat.search([
                ('name', '=', child_name),
                ('parent_id', '=', parent.id),
                ('website_id', '=', website.id),
            ], limit=1)
            if not child:
                Cat.create({
                    'name': child_name,
                    'sequence': child_seq,
                    'parent_id': parent.id,
                    'website_id': website.id,
                })
            else:
                child.write({'sequence': child_seq})


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    website = env['website'].search([('name', '=', 'PJMS')], limit=1)
    if not website:
        return

    lang_es_cl = env['res.lang'].search([('code', '=', 'es_CL')], limit=1) \
        or env['res.lang'].search([('code', '=', 'es')], limit=1)
    vals = {'homepage_url': '/pjms'}
    if lang_es_cl:
        vals['language_ids'] = [(6, 0, [lang_es_cl.id])]
        vals['default_lang_id'] = lang_es_cl.id
    website.write(vals)

    Menu = env['website.menu']
    top_menu = website.menu_id
    for label, url, seq in [
        ('Tienda', '/shop', 10),
        ('Contacto', '/contactus', 90),
    ]:
        if top_menu and not Menu.search([
            ('website_id', '=', website.id),
            ('url', '=', url),
        ], limit=1):
            Menu.create({
                'name': label,
                'url': url,
                'parent_id': top_menu.id,
                'website_id': website.id,
                'sequence': seq,
            })

    _ensure_categories(env, website)
    _ensure_category_menus(env, website)


def _ensure_category_menus(env, website):
    """Crea ítems de menú para cada categoría padre. No duplica."""
    Menu = env['website.menu']
    Cat = env['product.public.category']
    top_menu = website.menu_id
    if not top_menu:
        return

    # Si ya existen menús de categorías (/coleccion/), no crear más
    existing_cat_menus = Menu.search([
        ('website_id', '=', website.id),
        ('url', 'like', '/coleccion/'),
    ], limit=1)
    if existing_cat_menus:
        return

    # No crear menús base fijos extra — los menús nativos de Odoo (Home, Tienda, Contacto)
    # ya existen en website_menu y se gestionan desde el backend de Website.

    # Un ítem por cada categoría padre
    cats = Cat.search([
        ('parent_id', '=', False),
        ('website_id', '=', website.id),
    ], order='sequence asc')

    for idx, cat in enumerate(cats):
        cat_url = '/coleccion/%s' % cat.id
        parent_menu = Menu.search([
            ('website_id', '=', website.id),
            ('url', '=', cat_url),
        ], limit=1)
        if not parent_menu:
            parent_menu = Menu.create({
                'name': cat.name,
                'url': cat_url,
                'parent_id': top_menu.id,
                'website_id': website.id,
                'sequence': 20 + idx,
            })

        # Subcategorías como submenús
        children = Cat.search([
            ('parent_id', '=', cat.id),
            ('website_id', '=', website.id),
        ], order='sequence asc')
        for child in children:
            child_url = '/shop?category=%s' % child.id
            if not Menu.search([
                ('website_id', '=', website.id),
                ('parent_id', '=', parent_menu.id),
                ('url', '=', child_url),
            ], limit=1):
                Menu.create({
                    'name': child.name,
                    'url': child_url,
                    'parent_id': parent_menu.id,
                    'website_id': website.id,
                    'sequence': child.sequence,
                })

    # Contacto al final (apunta a /contactus nativo de Odoo con estilos PJMS)
    if not Menu.search([('website_id', '=', website.id), ('url', '=', '/contactus')], limit=1):
        Menu.create({
            'name': 'Contacto',
            'url': '/contactus',
            'parent_id': top_menu.id,
            'website_id': website.id,
            'sequence': 99,
        })


def uninstall_hook(cr, registry):
    """Limpia categorías PJMS al desinstalar."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    website = env['website'].search([('name', '=', 'PJMS')], limit=1)
    if website:
        env['product.public.category'].search([
            ('website_id', '=', website.id),
        ]).unlink()
