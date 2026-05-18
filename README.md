# Web PJMS Site

Módulo Odoo 16 que implementa el sitio web completo de **PJMS** — marca chilena de _homewear, sleepwear & funwear_ — con tema visual propio, snippets reutilizables y tienda online integrada.

---

## Características

### Layout y Tema Visual
- **Sistema de diseño propio** con tokens CSS (`primary_variables.scss`, `pj_tokens.scss`) que definen paleta de colores, tipografía y espaciados exactos de la marca.
- **Paleta de marca**: slate `#7890a8`, forest `#003030`, teal `#78c0c0`, blush `#f0d8d8`, mustard `#f0a800` y cream `#faf7f5`.
- **Tipografías**: Italiana (display), Sacramento (script) y Helvetica Neue (body), cargadas desde Google Fonts.
- Clases utilitarias de sección (`pj_section_common.scss`) y override visual de `website_sale` para coherencia visual en toda la tienda.

### Header personalizado (`pj_header`)
- Wordmark centrado con tagline _"homewear · sleepwear · funwear"_.
- Navegación dinámica generada desde las **categorías de productos** (`product.public.category`) del sitio web, con submenús desplegables.
- Acceso directo a Mi Cuenta, Lista de Deseos y Carrito con conteo de ítems.
- Estado activo automático según la ruta actual.

### Footer personalizado (`pj_footer`)
- Override de `website.footer_custom` aplicado sólo al sitio PJMS.
- Grid de cuatro columnas: Tienda, Ayuda, Visítanos y Redes Sociales.
- Datos de contacto: CasaCostanera Nivel 3, horarios y correo `hola@pjms.cl`.
- Enlace directo a Instagram `@pjms.cl`.

### Snippets de Página Web
| Snippet | Descripción |
|---|---|
| `s_pj_hero` | Hero editorial con degradado de marca, foto de colección, CTA principal y secundario. |
| `s_pj_trust_bar` | Barra de confianza con 4 pilares: Envío Gratis, Cambios en Tienda, Hecho a Mano y Showroom. |
| `s_pj_featured` | Grilla de productos destacados de la colección actual. |
| `s_pj_categories` | Tarjetas visuales de categorías principales con imagen. |
| `s_pj_promo_banner` | Banner promocional de ancho completo con CTA. |
| `s_pj_bestsellers` | Carrusel de productos más vendidos. |
| `s_pj_brands` | Strip de logos de marcas o materiales (Algodón Pima, Viscosa, Modal, etc.). |
| `s_pj_newsletter` | Formulario de suscripción al newsletter. |

### Páginas
- **Home** (`/pjms`): Compone todos los snippets en una sola página editorial.
- **Contacto** (`/contacto-pjms`): Formulario integrado con `website.form` de Odoo (crea leads/contactos en CRM). Incluye campos nombre, correo, teléfono, asunto y mensaje.
- **Categoría** (`/coleccion/<id>`): Página dedicada por categoría con listado de subcategorías y productos filtrados, con precio en CLP.

### Categorías de Producto (auto-generadas)
El hook `post_init_hook` crea automáticamente las categorías de PJMS con imágenes si no existen:

| Categoría | Subcategorías |
|---|---|
| Básicos | Dos piezas, Camisas de Dormir |
| Verano '24 | Short y Polera, Short y camisas manga corta, Pantalón y polera, Camisas de dormir |
| Invierno '23 | Camisolas, Dos piezas |
| Material | Algodón Pima, Viscosa, Modal, Viscosa Lino, Piel de Durazno |
| SALE | — |

El hook `uninstall_hook` limpia los datos del sitio al desinstalar.

### Controlador HTTP
- Rutas públicas con soporte de sitemap para `/pjms`, `/contacto-pjms` y `/coleccion/<category>`.
- Filtrado de productos por categoría y subcategorías, solo productos publicados.
- Seguridad: redirige a `/shop` si la categoría pertenece a otro sitio web.

---

## Requisitos

- **Odoo 16 Community o Enterprise**
- Módulos: `website`, `website_sale`

---

## Instalación

1. Copiar la carpeta `web_pjms` en el directorio `extra-addons`.
2. Actualizar la lista de aplicaciones en Odoo.
3. Instalar el módulo **Web PJMS Site**.

El `post_init_hook` creará automáticamente el sitio web PJMS y sus categorías de producto con imágenes.

---

## Estructura del Módulo

```
web_pjms/
├── controllers/
│   └── main.py                 # Rutas HTTP del sitio
├── data/
│   └── website_data.xml        # Registro del sitio web PJMS
├── migrations/                 # Scripts de migración por versión
├── models/
├── security/
│   └── ir.model.access.csv
├── static/src/
│   ├── img/                    # Imágenes hero, banners y categorías
│   ├── js/snippets/            # JS del snippet Hero (carrusel)
│   └── scss/                   # Tokens, layout y estilos por snippet
├── views/
│   ├── layout/                 # Header, Footer y Layout base
│   ├── pages/                  # Home, Contacto, Categoría
│   ├── snippets/               # Un XML por snippet
│   └── website_sale_templates.xml
├── hooks.py                    # post_init_hook / uninstall_hook
└── __manifest__.py
```

---

## Autor

**Method** — `v16.0.1.0.2` · Licencia LGPL-3
