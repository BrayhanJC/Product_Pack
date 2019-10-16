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
	
	_inherit = 'sale.order'


	@api.onchange('sale_order_template_id')
	def onchange_sale_order_template_id(self):
		if not self.sale_order_template_id:
			self.require_signature = self._get_default_require_signature()
			self.require_payment = self._get_default_require_payment()
			return
		template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)

		order_lines = [(5, 0, 0)]
		for line in template.sale_order_template_line_ids:
			data = self._compute_line_data_for_template_change(line)
			if line.product_id:
				discount = 0
				if self.pricelist_id:
					price = self.pricelist_id.with_context(uom=line.product_uom_id.id).get_product_price(line.product_id, 1, False)
					if self.pricelist_id.discount_policy == 'without_discount' and line.price_unit:
						discount = (line.price_unit - price) / line.price_unit * 100
						price = line.price_unit

				else:
					price = line.price_unit

				data_pack = []
				if line.product_id.pack:
					print('es un pack')
					for x in line.product_id.pack_line_ids:
						vals={
							'product_pack_id': line.product_id.id,
							'product_id': x.product_id.id,
							'product_qty': x.quantity
						}
						data_pack.append((0, 0, vals))

				else:
					print('no es un pack')

				data.update({
					'price_unit': price,
					'discount': 100 - ((100 - discount) * (100 - line.discount) / 100),
					'product_uom_qty': line.product_uom_qty,
					'product_id': line.product_id.id,
					'product_uom': line.product_uom_id.id,
					'pack_aux_ids': data_pack,
					'customer_lead': self._get_customer_lead(line.product_id.product_tmpl_id),
				})
				if self.pricelist_id:
					data.update(self.env['sale.order.line']._get_purchase_price(self.pricelist_id, line.product_id, line.product_uom_id, fields.Date.context_today(self)))
			order_lines.append((0, 0, data))

		self.order_line = order_lines
		self.order_line._compute_tax_id()

		option_lines = []
		for option in template.sale_order_template_option_ids:
			data = self._compute_option_data_for_template_change(option)
			option_lines.append((0, 0, data))
		self.sale_order_option_ids = option_lines

		if template.number_of_days > 0:
			self.validity_date = fields.Date.to_string(datetime.now() + timedelta(template.number_of_days))

		self.require_signature = template.require_signature
		self.require_payment = template.require_payment

		if template.note:
			self.note = template.note



	def data_pack_complete(self, order_line):

		data_pack = []
		product_alternative = []
		data_product_pack = []


		contador_pack = 1
		

		for x in order_line:

			contador_pack_line = 1
			if x.product_id:

				if x.product_id.pack:

					_logger.info('agregando pack')
					_logger.info(x.product_id.name)

					vals = {

					'product_id': x.product_id.id,
					'name': x.product_id.name,
					'product_uom_qty': x.product_uom_qty,
					'product_uom': x.product_id.uom_id.name,
					'price_unit': x.price_unit,
					'tax_id': x.tax_id,
					'sequence_ref': str(contador_pack),
					'price_subtotal': x.price_unit,
					'price_total': x.price_unit,
					'amount': x.price_unit * x.product_uom_qty,
					'product_ids': [x.product_id.id for x in x.pack_aux_ids],
					'is_pack': 1,


					}
					data_pack.append(vals)

					for product_pack in x.pack_aux_ids:

						vals = {
						'pack_id': x.product_id.id,
						'product_id': product_pack.product_id.id,
						'name': product_pack.product_id.name,
						'product_uom_qty': product_pack.product_qty,
						'product_uom': product_pack.product_id.uom_id.name,
						'price_unit': product_pack.product_id.list_price,
						'tax_id': x.tax_id,
						'sequence_ref': str(contador_pack) + '.' + str(contador_pack_line),
						'price_subtotal': product_pack.product_id.list_price,
						'price_total': product_pack.product_id.list_price,
						'amount': product_pack.product_id.list_price * product_pack.product_qty,
						'is_pack': 0

						}

						data_product_pack.append(vals)

		data_result = []

		for pack in data_pack:

			data_result.append(pack)

			for data_product in data_product_pack:

				if data_product['pack_id'] == pack['product_id']:

					data_result.append(data_product)


		for x in product_alternative:
			data_result.append(x)


		for x in data_result:
			_logger.info(x)
			_logger.info('.')

		return data_result


	def return_pack_line(self, pack_line_ids, sale_order,sequence_number):

		data = []
		if pack_line_ids:

			product_ids = [x.product_id.id for x in pack_line_ids]

			contador = 1

			if self.state not in 'sale':
				for x in sale_order:
					if x.product_id.pack:
						if x.product_id.pack_price_type in ['none_detailed_assited_price', 'none_detailed_totaliced_price']:

							if x.pack_aux_ids:
								for product in x.pack_aux_ids:


									vals = {
										'display_type': x.display_type,
										'name': product.product_id.name,
										'product_uom_qty': product.product_qty,
										'product_uom': product.product_id.uom_id.name,
										'price_unit': product.product_id.list_price,
										#'discount': x.discount,
										'tax_id': x.tax_id,
										'sequence_ref': str(sequence_number) + '.' + str(contador),
										#', '.join(map(lambda x: (x.description or x.name), line.tax_id)),
										'price_subtotal': 0,
										'price_total': 0,
										'amount': 0
									}

									data.append(vals)

									contador+=1
			else:

				for x in sale_order:
					if x.product_id.id in product_ids:
						vals={
								'display_type': x.display_type,
								'name': x.name,
								'product_uom_qty': x.product_uom_qty,
								'product_uom': x.product_uom.name,
								'price_unit': x.price_unit,
								'discount': x.discount,
								'tax_id': x.tax_id,
								'sequence_ref': str(sequence_number) + '.' + str(contador),
								#', '.join(map(lambda x: (x.description or x.name), line.tax_id)),
								'price_subtotal': x.price_subtotal,
								'price_total': x.price_total,
								'amount': x.price_total
						} 
						data.append(vals)

						contador+=1

		self.data_pack_complete(sale_order)


		return data


	@api.multi
	def action_confirm(self):

		_logger.info('confirmando la venta')
		data_product = []
		data_aux = []
		if self.order_line:
			for x in self.order_line:
				
				if x.product_id.pack:

					if x.product_id.pack_price_type in ['none_detailed_assited_price', 'none_detailed_totaliced_price']:

						if len(x.pack_aux_ids) > 0:
							#_logger.info('los productos del pack son:')
							for value in x.pack_aux_ids:
								data_product.append( (0, 0, {'product_id': value.product_id.id, 'product_uom_qty': value.product_qty, 'price_unit':0}) )
					
				else:
					pass

		self.order_line = data_product

		if self._get_forbidden_state_confirm() & set(self.mapped('state')):
			raise UserError(_(
				'It is not allowed to confirm an order in the following states: %s'
			) % (', '.join(self._get_forbidden_state_confirm())))

		for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
			order.message_subscribe([order.partner_id.id])
		self.write({
			'state': 'sale',
			'confirmation_date': fields.Datetime.now()
		})
		self._action_confirm()
		if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
			self.action_done()
		return True


SaleOrderInherit()