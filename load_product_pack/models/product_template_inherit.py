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
import re
import csv
import os

import logging
_logger = logging.getLogger(__name__)



class ProductTemplateInherit(models.Model):

	_inherit = 'product.template'

	def leer_csv(self):
		
		dir_path = os.path.dirname(os.path.realpath(__file__))
		dir_path = dir_path[0: len(dir_path) - 6]
		dir_path = dir_path + "data/plantilla.csv"

		data = []

		with open(dir_path) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:

				_logger.info(row)

				vals={
				'name': row['name'] or '', 
				'type': row['tipo_producto'] or '', 
				'pack': row['is_pack'] or '',
				'pack_price_type': row['pack_price_type'] or '', 
				'pack_line_ids': row['pack_line_ids'] or '', 
				'quantity': row['cantidad'] or 0, 
				'discount': row['discount'] or 0,
				'list_price': row['precio_venta'] or 0,
				'standard_price ': row['costo'] or 0,
				'id_producto': row['id_producto']
				}

				data.append(vals)

		return data

	def create_product_pack(self, vals, produt_product_model):

		if vals:

			create_pack = produt_product_model.create({'name': vals['name'], 'default_code': vals['id_producto'], 'type': vals['type'], 'pack': True, 'pack_price_type': 'totalice_price'})



	def return_product_product(self, product_temp_id, produt_template_model, produt_product_model):

		product_product_id = produt_product_model.search([('default_code', '=', str(product_temp_id) )]).id

		return product_product_id



	def search_product_pack(self, vals, produt_template_model, produt_product_model, produt_pack_line_model, parent_product_id):
		
		if vals:

			product_product_id = self.return_product_product(vals['pack_line_ids'], produt_template_model, produt_product_model)


			product_product_pack_id = self.return_product_product(parent_product_id, produt_template_model, produt_product_model)

			pack_product_line_id = produt_pack_line_model.search([('parent_product_id', '=', product_product_pack_id), ('product_id', '=', product_product_id)])

			if len(pack_product_line_id) == 0:

				produt_template_model.search([('default_code', '=', parent_product_id)]).write({'pack_line_ids': [(0,0, {'parent_product_id': product_product_pack_id, 'product_id': product_product_id, 'quantity': vals['quantity'], 'discount': vals['discount'] })] })


	@api.model
	def loaf_information_product(self):

		vals = self.leer_csv()

		_logger.info(vals)

		produt_product_model = self.env['product.product']
		produt_template_model = self.env['product.template']
		produt_pack_line_model = self.env['product.pack.line']

		product_template_ids = produt_template_model.search([])


		vals_products = []
		for x in product_template_ids:
			vals_products.append(x.default_code)

		pack_product = ''

		for data in vals:
	
			if len(data['id_producto']) > 0:
				pack_product = data['id_producto']

				if str(data['id_producto']) not in vals_products:
				
					self.create_product_pack(data, produt_product_model)
			else:

				if 'pack_line_ids' in data:

					if str(data['pack_line_ids']) in vals_products:

						self.search_product_pack(data, produt_template_model, produt_product_model, produt_pack_line_model, pack_product)

		

ProductTemplateInherit()