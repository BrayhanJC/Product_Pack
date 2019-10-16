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


from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class SaleOrderPack(models.Model):
	_name = 'sale.order_pack_aux'

	sale_order_line_id = fields.Many2one('sale.order.line', string="Sale Order")
	product_pack_id = fields.Many2one('product.product', string="Product Pack", domain= "[('pack', '=', True)]")
	product_pack_qty = fields.Float(string="Cantidad Pack")
	product_id = fields.Many2one('product.product', string="Product", domain= "[('pack', '=', False)]")
	product_qty = fields.Float(string="Cantidad Producto")
	product_discount = fields.Integer(string="Descuento")

SaleOrderPack()