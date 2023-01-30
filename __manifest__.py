# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Master Laporan',
    'version' : '201221.4.0',
    'summary': 'Master Laporan',
    'sequence': 32,
    'images': [''],
    'depends': ['base','stock','sale','sale_stock','sale_stock_picking_note','stock_secondary_unit','account','purchase','msi_sale_do_inv','msi_product','vit_kelurahan','vit_efaktur','msi_terbilang'],
    'data': [
        'security/data.xml',
        'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/cashflow.xml',
        'views/sales_ete.xml',
        'views/purchase.xml',


    ],
    "application": True,

}
