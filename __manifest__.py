# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Acer Classification Import Using CSV',
    'version': '1.0',
    'author': "Portall Solutions inc.",
    'website': "portall.ca",
    'category': 'Maple',
    'summary':  'Barrels Inventory Import using CSV',
    'depends': ['maple'],
    'description': """
    This module add import barrels inventory CSV File.
    """,
    'data': [
         'wizard/acer_import_wizard.xml', #vue sélection fichier
         'views/acer_import_view.xml', #botuon action
     ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
