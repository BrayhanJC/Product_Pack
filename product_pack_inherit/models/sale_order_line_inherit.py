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

from odoo import api, fields, models, _
import time
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)
from odoo import modules
from odoo.addons import decimal_precision as dp


class SaleOrderInherit(models.Model):
	
	_inherit = 'sale.order.line'

	def return_product_pack(self):

		"""
		Funcion que retorna la informacion de los productos que hacen parte del pack
		
		"""

		result = []
		if self.product_id.pack:

			#validamos si el product pack tiene productos hijos
			if len(self.product_id.pack_line_ids) > 0:

				#recorremos los productos que contiene el pack
				for data_product in self.product_id.pack_line_ids:


					product = data_product.product_id.id
					quantity_product = data_product.quantity

					vals = {
					'product_pack_id': self.product_id.id,
					'product_id': product,
					'product_qty': quantity_product
					}

					result.append(vals)

		return result

	pack_aux_ids = fields.One2many('sale.order_pack_aux', 'sale_order_line_id', string="Product Pack")

	@api.depends('pack_aux_ids')
	def return_data_pack_aux(self):

		"""
		Funcion que retorna la informacion de los productos que estan en el pack order line
		
		"""

		data= []

		if self.pack_aux_ids:
			
			for x in self.pack_aux_ids:

				vals = {
							'product_pack_id': x.product_pack_id.id,
							'product_id': x.product_id.id,
							'product_qty': x.product_qty
							}

				data.append(vals)

		return data


	@api.onchange('product_id')
	def load_pack_aux(self):
		"""
		Funcion que permite cargar el pack_aux_ids con los productos que contienen el pack
		"""
		data = []

		if self.product_id:

			result = self.return_product_pack()

			_logger.info(result)

			if len(result) > 0:

				for x in result:
					data.append( (0, 0, x))

		if len(data) > 0:
			self.pack_aux_ids = None
			self.pack_aux_ids = result

	def return_data_update(self, vals):
		if vals:


			if self.pack_aux_ids and self.product_id:

				if self.product_id.pack_line_ids:

					for data_product in vals:

						if self.product_id.id == data_product['product_pack_id']:

							list_price = 0

							for pack_line in self.product_id.pack_line_ids:

								if pack_line.product_id.id == data_product['product_id']:

									product_list_price = pack_line.product_id.list_price

									_logger.info('-----')
									if data_product['product_qty'] > 0:

										list_price += (product_list_price * data_product['product_qty'])
									
									if data_product['product_qty'] < 0:

										list_price -=  product_list_price

									_logger.info('El producto %s tiene un valor de %s y la cantidad a multiplicar es: %s y el list_price es: %s' %(pack_line.product_id.name, pack_line.product_id.list_price, data_product['product_qty'], list_price))
								

							self.write({'price_unit': list_price + self.price_unit})

	def update_order_line_(self):

		data = []

		if self.pack_aux_ids and self.product_id:

			data_product = self.return_data_pack_aux()
			data_product_pack = self.return_product_pack()

			data_product_pack_qty = []

			for product_pack in data_product_pack:

				for product_data in data_product:


					if product_pack['product_id'] == product_data['product_id']:


						_logger.info('La cantidad de data_order es: %s y la cantidad de data_pack es: %s ' %(product_pack['product_qty'] , product_data['product_qty']))
						product_quantity = 0

						#si hay mas cantidades de ese producto a pedir
						if product_pack['product_qty'] < product_data['product_qty']:

							product_quantity =   product_data['product_qty'] - product_pack['product_qty'] 

						#si hay menos cantidades de ese producto a pedir
						if product_pack['product_qty'] > product_data['product_qty']:

							
							product_quantity = product_data['product_qty'] - product_pack['product_qty']



						vals = {
								'product_pack_id': self.product_id.id,
								'product_id': product_data['product_id'],
								'product_qty': product_quantity
								}
						data.append(vals)

			_logger.info(data)

			self.return_data_update(data)

SaleOrderInherit()