# -*- coding: utf-8 -*-

from odoo import api, fields, models
import base64
from io import  BytesIO
from dateutil import parser
import datetime 
from datetime import datetime, timedelta
from odoo.exceptions import  Warning

try:
	import xlwt
	from xlwt import Borders
except ImportError:
	xlwt = None

import logging
_logger = logging.getLogger(__name__)

class YWTExportSaleOrder(models.TransientModel):
	
	# Model Name     
	_name = "ywt.export.sale.order"
	

	# Field Declaration
	datas = fields.Binary(string='File')
	filter_product = fields.Selection([('pack', 'Pack'), ('pack_line', 'Pack Line')])
	
	def return_pack_line(self, order):

		data_pack = []
		product_alternative = []
		data_product_pack = []

		for x in order.order_line:

			if x.product_id:

				if x.product_id.pack:

					_logger.info('agregando pack')
					_logger.info(x.product_id.name)

					vals = {
					'product_id': x.product_id.id,
					'product_name': x.product_id.name,
					'product_und': x.product_id.uom_id.name,
					'order_qty': x.product_uom_qty,
					'product_description': x.name,
					'price_unit': x.currency_id.symbol + ' ' + str(x.price_unit),
					'price_subunit': x.currency_id.symbol + ' ' +  str(x.price_subtotal),
					'product_ids': [x.product_id.id for x in x.pack_aux_ids],
					'is_pack': 1

					}
					data_pack.append(vals)

					for product_pack in x.pack_aux_ids:

						vals = {
						'pack_id': x.product_id.id,
						'product_id': product_pack.product_id.id,
						'product_name': product_pack.product_id.name,
						'product_und': product_pack.product_id.uom_id.name,
						'order_qty': product_pack.product_qty,
						'product_description': product_pack.product_id.name,
						'price_unit': x.currency_id.symbol + ' ' + str(0),
						'price_subunit': x.currency_id.symbol + ' ' +  str(0),
						'is_pack': 0

						}

						data_product_pack.append(vals)

					#data_pack.append(x.product_id.id)

				else:
					_logger.info('es un producto del pack o un producto normal')

					vals = {
						'product_id': x.product_id.id,
						'product_name': x.product_id.name,
						'product_und': x.product_id.uom_id.name,
						'product_description': x.name,
						'order_qty': x.product_uom_qty,
						'price_unit': x.currency_id.symbol + ' ' + str(x.price_unit),
						'price_subunit': x.currency_id.symbol + ' ' +  str(x.price_subtotal),
						'is_pack': 0

						}

					#if x.price_unit == 0:

					#	_logger.info('es un producto de un pack')

					#	data_product_pack.append(vals)
						#data_product_pack.append(x.product_id.id)
					if x.price_unit > 0:

						_logger.info('es un producto normal')
						vals['is_pack'] = -1
						product_alternative.append(vals)
						#product_alternative.append(x.product_id.id)


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

		return data_result



	def return_product_data(self, order_line, line):
 
		
		order_line['product_sequence'] = line.sequence_ref                                                                   
		order_line['product_name'] = line.product_id.name
		order_line['product_und'] = line.product_id.uom_id.name      
		order_line['product_description'] = line.name                        
		order_line['order_qty'] = line.product_uom_qty
		#order_line['qty_delivered'] = line.qty_delivered  
		#order_line['qty_invoiced'] = line.qty_invoiced                             
		order_line['price_unit'] = line.currency_id.symbol + ' ' + str(line.price_unit)                      
		order_line['price_subunit'] =  line.currency_id.symbol + ' ' +  str(line.price_subtotal) 
		

		return order_line

	@api.multi
	def ywt_exprot_sale_order(self):

		if self.filter_product:
			if self.filter_product == 'pack':
				_logger.info('solo pack')
			if self.filter_product == 'pack_line':
				_logger.info('pack con las lineas')

		sale_order_obj = self.env['sale.order']
		active_id = self.ids[0]
		
		today = datetime.now().strftime("%Y-%m-%d")
		file_name = 'Export Sale Order' + ' ' + today
		
		sale_order_ids = self._context.get('active_ids', [])
		if not sale_order_ids:
			raise Warning(_('Please Select At least One Sale Order to Export'))
		if sale_order_ids:
			custom_value = {}
			sale_order_ids_ls = sale_order_obj.search([('id', 'in', sale_order_ids)])
			
			workbook, header_bold, value_style, header_bold_data, value_style_left, value_style_right, value_style_header, value_style_right_gray, value_style_right_color, value_style_color, value_style_left_bold = self.ywt_prepare_design()
			
			for order in sale_order_ids_ls:
				sheet = workbook.add_sheet(order.name)
				order_lst = []                                                          
				for line in order.order_line:  
					order_line = {}

					if self.filter_product == 'pack':
						_logger.info('es solo un pack')
						if line.product_id.pack:
							order_line = self.return_product_data(order_line, line)
							order_lst.append(order_line)
					
					elif self.filter_product == 'pack_line':
						_logger.info('el pack con lineas')
						#if line.product_id.pack:
						#	order_line = self.return_product_data(order_line, line)
						#	order_lst.append(order_line)
						order_lst = self.return_pack_line(order)

					else:
						_logger.info('impresion normal')
						order_line = self.return_product_data(order_line, line)
						order_lst.append(order_line)



				_logger.info('esto es lo que va a imprirmir')
				_logger.info(order_lst)

				custom_value['products'] = order_lst               
				custom_value['partner_id'] = order.partner_id.name
				custom_value['partner_street'] = order.partner_id.street or 'Sin dirección'
				custom_value['partner_email'] = order.partner_id.email or 'Sin Email'
				custom_value['partner_city'] = order.partner_id.city or 'Sin Ciudad'
				custom_value['partner_state'] = order.partner_id.state_id.name or 'Sin Departamento'
				custom_value['partner_country'] = order.partner_id and order.partner_id.country_id.name or 'Sin Pais'
				custom_value['partner_mobile'] = order.partner_id.mobile
				custom_value['partner_phone'] = order.partner_id.phone

				custom_value['date_order'] = str(order.confirmation_date)
				custom_value['amount_total'] = order.currency_id.symbol + ' ' + str((order.amount_total + order.amount_surcharge_vale))
				custom_value['amount_untaxed'] = order.currency_id.symbol + ' ' +  str(order.amount_untaxed) 
				custom_value['amount_tax'] = order.currency_id.symbol + ' ' +  str(order.amount_tax) 


				company = self.env.user.company_id

				sheet.col(0).width = 4096
				sheet.col(1).width = 10000
				sheet.col(3).width = 4000
				sheet.col(4).width = 5000
				sheet.col(5).width = 8000

				#información titulo
				sheet.write_merge(2, 2, 4, 5, 'Diseño Electrico ' + company.name, value_style_header)
				

				#información empresa
				sheet.write_merge(5, 5, 0, 1, company.name, header_bold)
				sheet.write_merge(6, 6, 0, 1, company.street, value_style_left)
				sheet.write_merge(7, 7, 0, 1, (company.city or ' ') + ( ' ' + company.state_id.name or ' ') + (' ' + company.country_id.name or ''), value_style_left)
				sheet.write_merge(8, 8, 0, 1, company.phone, value_style_left)
				sheet.write_merge(9, 9, 0, 1, company.email, value_style_left)
				sheet.write_merge(10, 10, 0, 1, company.website, value_style_left)    

				#Información cotización
				sheet.write(5, 4, 'Coización No.', header_bold)
				sheet.write(5, 5, str(order.name), value_style)


				#Informacón del cliente
				sheet.write_merge(12, 12, 0, 1, 'DATOS DEL CLIENTE', header_bold)
				sheet.write(13, 0, 'Nombre:', header_bold_data)
				sheet.write(13, 1, custom_value['partner_id'], value_style_left)
				sheet.write(14, 0, 'Att:', header_bold_data)
				sheet.write(14, 1, 'Arq. ', value_style_left)
				sheet.write(15, 0, 'E-mail', header_bold_data)
				sheet.write(15, 1, custom_value['partner_email'], value_style_left)
				sheet.write(16, 0, 'Direccion', header_bold_data)
				sheet.write(16, 1, custom_value['partner_street'], value_style_left)
				sheet.write(17, 0, 'Ciudad', header_bold_data)
				sheet.write(17, 1, custom_value['partner_state'] + ' - ' + custom_value['partner_city'], value_style_left)
				sheet.write(18, 0, 'Telefono', header_bold_data)
				partner_phone = custom_value['partner_mobile'] or ''
				if custom_value['partner_phone']:
					partner_phone = partner_phone + ' - ' + custom_value['partner_phone']
				sheet.write(18, 1, partner_phone, value_style_left)


				_logger.info('el tipo es:')
				_logger.info(order.validity_date)
				_logger.info(type(order.validity_date))
				#Informacón condiciones comerciales
				sheet.write_merge(12, 12, 4, 5, 'CONDICIONES COMERCIALES', header_bold)
				sheet.write(13, 4, 'Fecha:', header_bold_data)
				sheet.write(13, 5, str(order.date_order), value_style_left)
				sheet.write(14, 4, 'Responsable:', header_bold_data)
				sheet.write(14, 5, order.user_id.name, value_style_left)
				sheet.write(15, 4, 'Condiciones de Pago:', header_bold_data)
				sheet.write(15, 5, order.payment_term_id.name or '', value_style_left)
				sheet.write(16, 4, 'Valida Hasta', header_bold_data)
				sheet.write(16, 5, order.validity_date or '', value_style_left)
				sheet.write(17, 4, 'Plazo Entrega', header_bold_data)
				sheet.write(17, 5, order.expected_date or order.commitment_date, value_style_left)
				sheet.write(18, 4, 'IEN:', header_bold_data)
				sheet.write(18, 5, 'GERMAN MIRANDA O.', value_style_left)
				
				sheet.write(20, 0, "ITEM", header_bold)
				sheet.write(20, 1, "DESCRIPCION", header_bold)
				sheet.write(20, 2, "UND", header_bold)
				sheet.write(20, 3, "CANT.", header_bold)
				sheet.write(20, 4, "VR. UNITARIO", header_bold)            
				sheet.write(20, 5, 'VR. TOTAL', header_bold)

				row = 21
				col = 1
				secuencia_pack = 1
				secuencia = 0
				secuencia_product = 0

				for product in custom_value['products']:  

					color_cell = value_style_left
					color_cell_price = value_style_right
					color_cell_qty = value_style


					if self.filter_product == 'pack_line':

						if product['is_pack'] == -1:
							#secuencia = product['product_sequence']
							secuencia += 1
							sheet.write(row, 0, secuencia, value_style_left)
							

						if product['is_pack'] == 1:
							#secuencia = product['product_sequence']
							secuencia += 1
							secuencia_product = 0
							sheet.write(row, 0, secuencia, value_style_left)
							

						if product['is_pack'] == 0: 
							color_cell = value_style_right_gray
							color_cell_price = value_style_right_color
							color_cell_qty = value_style_color
				
							sheet.write(row, 0, str(secuencia) + '.' + str(secuencia_product), value_style_right_gray)
					else:
						
						sheet.write(row, 0, secuencia_pack, value_style_left)

					sheet.write(row, 1, product['product_name'] + ' - ' + product['product_description'], color_cell)
					sheet.write(row, 2, product['product_und'], color_cell)
					sheet.write(row, 3, float(product['order_qty']), color_cell_qty)      
					sheet.write(row, 4, (product['price_unit']), color_cell_price)
					sheet.write(row, 5, (product['price_subunit']), color_cell_price) 
					
					secuencia_product += 1  

					_logger.info(secuencia_product)                       
					row += 1
					secuencia_pack+= 1

				row += 1
				#total
				sheet.write(row+1, 3, 'SUB TOTAL', value_style_left_bold)
				sheet.write(row+1, 4, '', value_style_right_color)
				sheet.write(row+1, 5, custom_value['amount_untaxed'], value_style_right)
				sheet.write(row+2, 3, 'AIU', value_style_left_bold)
				sheet.write(row+2, 4, '', value_style_right_color)
				sheet.write(row+2, 5, order.amount_surcharge_vale, value_style_right)
				sheet.write(row+3, 3, 'IVA', value_style_left_bold)
				sheet.write(row+3, 4, '', value_style)
				sheet.write(row+3, 5, custom_value['amount_tax'], value_style_right)
				sheet.write(row+4, 3, 'TOTAL OFERTA', value_style_left_bold)
				sheet.write(row+4, 4, '', value_style_right_color)
				sheet.write(row+4, 5, custom_value['amount_total'], value_style_right)
					
				#Observaciones
				sheet.write_merge(row, row, 0, 1, 'OBSERVACIONES', value_style_left_bold)
				sheet.write_merge(row+1, row+1, 0, 1, '* No incluye diseños de media tension.', value_style_left_bold)
				sheet.write_merge(row+2, row+2, 0, 1, '* No incluye acompañamiento durante la construccion', value_style_left_bold)
				sheet.write_merge(row+3, row+3, 0, 1, '* No incluye tramites con el operador de red', value_style_left_bold)

				row += 4
				sheet.write_merge(row+1, row+1, 0, 1, 'Jhon Fredy Bogota Mondragon', value_style)
				sheet.write_merge(row+2, row+2, 0, 1, 'john.bogota@ittingenieria.com', value_style)


			fp = BytesIO()            
			workbook.save(fp)
			fp.seek(0)
			sale_file = base64.encodestring(fp.read())
			fp.close()
			self.write({'datas':sale_file})
			if self.datas:
				return {
				'type' : 'ir.actions.act_url',
				'url': 'web/content/?download=1&model=ywt.export.sale.order&field=datas&id=%s&filename=%s.xls' % (active_id, file_name),
				'target': 'self',
				 }
				
	@api.multi
	def ywt_prepare_design(self):
		workbook = xlwt.Workbook()   
		borders = Borders()
		#style = xlwt.XFStyle()
		#style = xlwt.easyxf('font: bold 1, color gray25;')

		header_border = Borders()
		header_border.left, header_border.right, header_border.top, header_border.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THICK
		
		borders.left, borders.right, borders.top, borders.bottom = Borders.THIN, Borders.THIN, Borders.THIN, Borders.THIN
		
		header_bold = xlwt.easyxf("font: bold on, height 200; pattern: pattern solid, fore_colour gray25;alignment: horizontal center ,vertical center")
		header_bold.borders = header_border

		header_bold_data = xlwt.easyxf("font: bold on, height 200; pattern: pattern solid, fore_colour gray25; alignment: horizontal left ,vertical center;  borders: top thin,right thin,bottom thin,left thin")
		header_bold_data.borders = header_border

		value_style = xlwt.easyxf("font: height 200, name Arial; alignment: horizontal center ,vertical center; borders: top thin,right thin,bottom thin,left thin")

		value_style_color = xlwt.easyxf("font: height 200, color gray25, name Arial; alignment: horizontal center ,vertical center; borders: top thin,right thin,bottom thin,left thin")


		value_style_left = xlwt.easyxf("font: height 200, name Arial; alignment: horizontal left ,vertical center; borders: top thin,right thin,bottom thin,left thin")

		value_style_header = xlwt.easyxf("font: bold on, height 300, name Arial; alignment: horizontal center ,vertical center; borders: top thin,right thin,bottom thin,left thin")

		value_style_right = xlwt.easyxf("font: height 200, name Arial; alignment: horizontal right ,vertical center; borders: top thin,right thin,bottom thin,left thin", num_format_str='#,##0.00')

		value_style_right_color = xlwt.easyxf("font: height 200, color gray25, name Arial; alignment: horizontal right ,vertical center; borders: top thin,right thin,bottom thin,left thin", num_format_str='#,##0.00')

		value_style_right_gray = xlwt.easyxf("font: height 200, color gray25, name Arial; alignment: horizontal right ,vertical center;  borders: top thin,right thin,bottom thin,left thin")


		value_style_left_bold = xlwt.easyxf("font: bold on, height 200, name Arial; alignment: horizontal left ,vertical center;  pattern: pattern solid, fore_colour gray25; borders: top thin,right thin,bottom thin,left thin")

		return workbook, header_bold, value_style, header_bold_data, value_style_left, value_style_right, value_style_header, value_style_right_gray, value_style_right_color, value_style_color, value_style_left_bold
