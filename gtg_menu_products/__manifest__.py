{
    'name': 'Products Top Menu',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Moves all product views to a new top-level Products menu',
    'author': 'Samiha',
    'depends': ['product','web'],
    'data': [
        'views/base_menu.xml',
        'views/product_menu.xml',
    ],
    'assets': {
    'web.assets_backend': [
        'gtg_menu_products/static/src/js/product_image_popup.js',
        'gtg_menu_products/static/src/xml/product_image_dialog.xml',
        'gtg_menu_products/static/src/js/product_image_dialog.js',
        'gtg_menu_products/static/src/css/*',
    ],
},
    'installable': True,
    'application': False,
}
