from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSalePjms(WebsiteSale):
    """Override del shop para filtrar productos por ribbon_tipo via ?ribbon_tipo=<valor>."""

    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        """Necesario para que Odoo use esta clase como handler de /shop."""
        return super().shop(
            page=page, category=category, search=search,
            min_price=min_price, max_price=max_price, ppg=ppg, **post,
        )

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domain = super()._get_search_domain(search, category, attrib_values, search_in_description)
        ribbon_tipo = request.httprequest.args.get('ribbon_tipo')
        if ribbon_tipo:
            domain += [('website_ribbon_id.tipo', '=', ribbon_tipo)]
        return domain

    def _shop_get_query_url_kwargs(self, category, search, min_price, max_price, attrib=None, order=None, **post):
        kwargs = super()._shop_get_query_url_kwargs(
            category, search, min_price, max_price, attrib=attrib, order=order, **post
        )
        ribbon_tipo = request.httprequest.args.get('ribbon_tipo')
        if ribbon_tipo:
            kwargs['ribbon_tipo'] = ribbon_tipo
        return kwargs

    def _get_additional_extra_shop_values(self, values, **post):
        extra = super()._get_additional_extra_shop_values(values, **post)
        extra['ribbon_tipo'] = request.httprequest.args.get('ribbon_tipo', '')
        return extra


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
