from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug


class PjmsSite(http.Controller):

    @http.route(['/pjms'], type='http', auth='public', website=True, sitemap=True)
    def home(self, **kw):
        return request.render('web_pjms.pj_home')

    @http.route(['/contacto-pjms'], type='http', auth='public', website=True, sitemap=True)
    def contacto(self, **kw):
        return request.render('web_pjms.pj_contacto_page')

    @http.route(['/coleccion/<model("product.public.category"):category>'],
                type='http', auth='public', website=True, sitemap=True)
    def category_page(self, category, **kw):
        website = request.website
        if category.website_id and category.website_id.id != website.id:
            return request.redirect('/shop')

        subcategories = request.env['product.public.category'].sudo().search([
            ('parent_id', '=', category.id),
            ('website_id', '=', website.id),
        ], order='sequence asc, name asc')

        cat_ids = [category.id] + subcategories.ids
        products = request.env['product.template'].sudo().search([
            ('is_published', '=', True),
            ('public_categ_ids', 'in', cat_ids),
        ], order='create_date desc')

        pj_currency = (
            request.env['res.currency'].sudo().search([('name', '=', 'CLP')], limit=1)
            or request.env.company.currency_id
        )

        return request.render('web_pjms.pj_category_page', {
            'category': category,
            'subcategories': subcategories,
            'products': products,
            'pj_currency': pj_currency,
            'slug': slug,
        })
