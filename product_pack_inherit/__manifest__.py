# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    Autor: Brayhan Andres Jaramillo Castaño
#    Correo: brayhanjaramillo@hotmail.com
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

{
    'name': 'Product Pack Inherit',
    'version': '12.0',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'author': 'Brayhan Jaramillo',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'product_pack', 'sale', 'set_sequence_number', 'surcharge_value'
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/pack_report.xml',
        'report/report.xml',
        'views/sale_order_inherit.xml',
        'views/sale_order_pack_aux_view.xml',


    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
