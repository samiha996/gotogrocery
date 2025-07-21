# -*- coding: utf-8 -*-
{
    'name': "Product Package Price",
    'author': "Hassan Alwan",
    'category': 'Package',
    'version': '1.0',
    'depends': ['product', 'purchase', 'sale'],
    'data':[
        'security/ir.model.access.csv',
        'views/product_package.xml',
        'views/purchase_order_view.xml',
        'views/product_template.xml',
        'views/product_product.xml',
        'views/purchase_order_view.xml',
        'views/sale_order_view.xml',
        'views/product_packaging_tree_view2.xml',
        'views/stock_move.xml',
        'views/account_move_line.xml',
        'wizard/purchase_order_discount.xml',
    ],
}

