# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import xlsxwriter
import base64
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp

class tbl_report_sales_ete(models.Model):
    _name = 'tbl.report.sales.ete'

    name = fields.Char('Name',default=' Sales End to End')
    tgl_awal = fields.Datetime('Tanggal Awal', required=True)
    tgl_akhir = fields.Datetime('Tanggal Akhir', required=True)
    data = fields.Binary(string='File', readonly=True)
    # detail = fields.One2many('tbl.report.sales.ete.detail','details', string='Detail')
    # detail2 = fields.One2many('tbl.report.sales.ete.tmp','details', string='Detail')
    # detail3 = fields.One2many('tbl.report.sales.ete.tmp2','details', string='Detail')
    
    def act_get_so(self):
        # detail_obj = self.env['tbl_report_sales_ete_detail']
        detail2_obj = self.env['tbl_report_sales_ete_tmp']
        
        # if self.detail:
        #    self.detail.unlink()
        
        if self.detail2:
           self.detail2.unlink()
        so=0
        self.env.cr.execute('Select order_id, product_uom_qty, product_uom, price_unit, price_subtotal, product_id, id From \
                            sale_order_line\
                            where date_order >=%s and date_order <=%s', (self.tgl_awal, self.tgl_akhir))
        for row in self.env.cr.fetchall():
            so=row[6]
            cari = self.env['tbl_report_sales_ete_tmp'].search([('so_line_id', '=', so),('details', '!=', self.id)], limit=1)
            # if cari:
            #     raise UserError(_('%s sudah di Get Sebelumnya' % (cari.so_line_id.id, )))
            # else:
            data_line2 = detail2_obj.create({
                    'details': self.id,
                    'name': row[0],
                    # 'contract_name': row[1],
                    'order_qty': row[1],
                    'uom_id': row[2],
                    'price_unit': row[3],
                    'amount_total': row[4],
                    'product_id': row[5],
                    'so_line_id': row[6],
                    # 'tax_exclude': row[7],
                    # 'tax': row[8],
                    # 'amount_total': row[9],
                    # 'amount_due': row[10],
                    # 'state': row[11],
            })

    def act_get_data(self):
        detail_obj = self.env['tbl_report_sales_ete_detail']

        if self.detail:
           self.detail.unlink()
        for line in self.detail2:
            if line.so_line_id.invoice_lines and line.so_line_id.move_ids:
                for line1 in line.so_line_id.invoice_lines:
                    for move in line1.move_line_ids:
                        cari = self.env['stock.move'].search([('id', '=', move.id)], limit=1)
                        caripo = self.env['purchase.order.line'].search([('sale_line_id', '=', move.sale_line_id.id)], limit=1)
                        data_line3 = detail_obj.create({
                            'details': self.id,
                            'name': line.name.id,
                            'order_qty': line.order_qty,
                            'uom_id': line.uom_id.id,
                            'price_unit': line.price_unit,
                            'amount_total': line.amount_total,
                            'product_id': line.product_id.id,
                            'so_line_id': line.so_line_id.id,
                            'do_line_id': cari.id,
                            'qty_delivered': cari.product_uom_qty,
                            'do_number': cari.picking_id.id,
                            'product_uom_qty': cari.product_uom_qty,
                            'product_uom': cari.product_uom.id,
                            'inv_line_id': line1.id,
                            'number': line1.invoice_id.id,
                            'price_unitinv': line1.price_unit,
                            'amount_totalinv': line1.price_subtotal,
                            'amount_totaltax': line1.price_tax,
                            'po_line_id': caripo.id,
                            'po_id': caripo.order_id.id,
                        })
            if line.so_line_id.invoice_lines and not line.so_line_id.move_ids:
                for line1 in line.so_line_id.invoice_lines:
                    # for move in line1.move_line_ids:
                        # cari = self.env['stock.move'].search([('id', '=', move.id)], limit=1)
                        caripo = self.env['purchase.order.line'].search([('sale_line_id', '=', line.so_line_id.id)], limit=1)
                        data_line3 = detail_obj.create({
                            'details': self.id,
                            'name': line.name.id,
                            'order_qty': line.order_qty,
                            'uom_id': line.uom_id.id,
                            'price_unit': line.price_unit,
                            'amount_total': line.amount_total,
                            'product_id': line.product_id.id,
                            'so_line_id': line.so_line_id.id,
                            # 'qty_delivered': cari.product_uom_qty,
                            # 'do_number': cari.picking_id.id,
                            # 'product_uom_qty': cari.product_uom_qty,
                            # 'product_uom': cari.product_uom.id,
                            'inv_line_id': line1.id,
                            'number': line1.invoice_id.id,
                            'price_unitinv': line1.price_unit,
                            'amount_totalinv': line1.price_subtotal,
                            'amount_totaltax': line1.price_tax,
                            'po_line_id': caripo.id,
                            'po_id': caripo.order_id.id,
                        })
            if not line.so_line_id.invoice_lines and line.so_line_id.move_ids:
                # for line1 in line.so_line_id.invoice_lines:
                    for move in line.so_line_id.move_ids:
                        # cari = self.env['stock.move'].search([('id', '=', move.id)], limit=1)
                        caripo = self.env['purchase.order.line'].search([('sale_line_id', '=', move.sale_line_id.id)], limit=1)
                        data_line3 = detail_obj.create({
                            'details': self.id,
                            'name': line.name.id,
                            'order_qty': line.order_qty,
                            'uom_id': line.uom_id.id,
                            'price_unit': line.price_unit,
                            'amount_total': line.amount_total,
                            'product_id': line.product_id.id,
                            'so_line_id': line.so_line_id.id,
                            'do_line_id': move.id,
                            'qty_delivered': move.product_uom_qty,
                            'do_number': move.picking_id.id,
                            'product_uom_qty': move.product_uom_qty,
                            'product_uom': move.product_uom.id,
                            'po_line_id': caripo.id,
                            'po_id': caripo.order_id.id,
                            # 'number': line1.invoice_id.id,
                            # 'price_unitinv': line1.price_unit,
                            # 'amount_totalinv': line1.price_subtotal,
                            # 'amount_totaltax': line1.price_tax,
                        })
            if not line.so_line_id.invoice_lines and not line.so_line_id.move_ids:
                # for line1 in line.so_line_id.invoice_lines:
                    # for move in line.so_line_id.move_ids:
                        # cari = self.env['stock.move'].search([('id', '=', move.id)], limit=1)
                        caripo = self.env['purchase.order.line'].search([('sale_line_id', '=', line.so_line_id.id)], limit=1)
                        data_line3 = detail_obj.create({
                            'details': self.id,
                            'name': line.name.id,
                            'order_qty': line.order_qty,
                            'uom_id': line.uom_id.id,
                            'price_unit': line.price_unit,
                            'amount_total': line.amount_total,
                            'product_id': line.product_id.id,
                            'so_line_id': line.so_line_id.id,
                            'po_line_id': caripo.id,
                            'po_id': caripo.order_id.id,
                            # 'qty_delivered': move.product_uom_qty,
                            # 'do_number': move.picking_id.id,
                            # 'product_uom_qty': move.product_uom_qty,
                            # 'product_uom': move.product_uom.id,
                            # 'number': line1.invoice_id.id,
                            # 'price_unitinv': line1.price_unit,
                            # 'amount_totalinv': line1.price_subtotal,
                            # 'amount_totaltax': line1.price_tax,
                        })

    @api.one
    def unlink(self):
        for rec in self:
            if rec.detail:
                rec.detail.unlink()
            if rec.detail2:
                rec.detail2.unlink()
        return super(tbl_report_sales_ete, self).unlink()

    @api.multi
    def print_xls_report(self):
        xls_filename = 'Sales End to End '+str(self.tgl_awal)+' - '+str(self.tgl_akhir)+'.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + xls_filename)
        # report_sales_ete_detail_obj = self.env['report.eq_inventory_valuation_report.inventory_valuation_report']
        header_merge_format = workbook.add_format({'bold':True, 'align':'center', 'valign':'vcenter', \
                                            'font_size':10, 'bg_color':'#D3D3D3', 'border':1})

        header_data_format = workbook.add_format({'align':'center', 'valign':'vcenter', \
                                                   'font_size':10, 'border':1})
        product_header_format = workbook.add_format({'valign':'vcenter', 'font_size':10, 'border':1})
        rows = 1
        worksheet = workbook.add_worksheet(self.name)
        for line in self.detail:
            worksheet.write(0, 0, 'No SO', header_merge_format)
            worksheet.write(0, 1, 'Warehouse', header_merge_format)
            worksheet.write(0, 2, 'Tipe Barang', header_merge_format)
            worksheet.write(0, 3, 'Schedule Date', header_merge_format)
            worksheet.write(0, 4, 'Effective Date', header_merge_format)
            worksheet.write(0, 5, 'Sales Team', header_merge_format)
            worksheet.write(0, 6, 'Salesperson', header_merge_format)
            worksheet.write(0, 7, 'Customer', header_merge_format)
            worksheet.write(0, 8, 'Invoice Address', header_merge_format)
            worksheet.write(0, 9, 'Delivery Address', header_merge_format)
            worksheet.write(0, 10, 'Customer Reference', header_merge_format)
            worksheet.write(0, 11, 'SO Order Date', header_merge_format)
            worksheet.write(0, 12, 'Confirmation Date', header_merge_format)
            worksheet.write(0, 13, 'Customer Reference', header_merge_format)
            worksheet.write(0, 14, 'Product', header_merge_format)
            worksheet.write(0, 15, 'Description', header_merge_format)
            worksheet.write(0, 16, 'Order Quantity', header_merge_format)
            worksheet.write(0, 17, 'Delivered QTY (SO)', header_merge_format)
            worksheet.write(0, 18, 'Open QTY', header_merge_format)
            worksheet.write(0, 19, 'Invoice Qty', header_merge_format)
            worksheet.write(0, 20, 'Unit Of Measure', header_merge_format)
            worksheet.write(0, 21, 'Route', header_merge_format)
            worksheet.write(0, 22, 'Discount', header_merge_format)
            worksheet.write(0, 23, 'Product Category', header_merge_format)
            worksheet.write(0, 24, 'Order Quantity', header_merge_format)
            worksheet.write(0, 25, 'Sales Unit', header_merge_format)
            worksheet.write(0, 26, 'Ship to Name', header_merge_format)
            worksheet.write(0, 27, 'Tipe Customer', header_merge_format)
            worksheet.write(0, 28, 'Province Desc', header_merge_format)
            worksheet.write(0, 29, 'Kota/Kab', header_merge_format)
            worksheet.write(0, 30, 'Kecamatan', header_merge_format)
            worksheet.write(0, 31, 'Telephone', header_merge_format)
            worksheet.write(0, 32, 'Payment Terms', header_merge_format)
            worksheet.write(0, 33, 'Price List Type', header_merge_format)
            worksheet.write(0, 34, 'Incoterm', header_merge_format)
            worksheet.write(0, 35, 'Currency', header_merge_format)
            worksheet.write(0, 36, 'Discount', header_merge_format)
            worksheet.write(0, 37, 'Sub total SO', header_merge_format)
            worksheet.write(0, 38, 'Term and Condition', header_merge_format)
            worksheet.write(0, 39, 'Shipping Policy', header_merge_format)
            worksheet.write(0, 40, 'Expected Date', header_merge_format)
            worksheet.write(0, 41, 'Effective Date', header_merge_format)
            worksheet.write(0, 42, 'Picking Note', header_merge_format)
            worksheet.write(0, 43, 'Analytic Account', header_merge_format)
            worksheet.write(0, 44, 'No Plat Kendaraan So', header_merge_format)
            worksheet.write(0, 45, 'Driver So', header_merge_format)
            worksheet.write(0, 46, 'Unit Price(SO)', header_merge_format)
            worksheet.write(0, 47, 'Total Price(SO)', header_merge_format)
            worksheet.write(0, 48, 'Do Number', header_merge_format)
            worksheet.write(0, 49, 'Source Location Desc', header_merge_format)
            worksheet.write(0, 50, 'Quantitiy', header_merge_format)
            worksheet.write(0, 51, 'UOM', header_merge_format)
            worksheet.write(0, 52, 'Effective Date', header_merge_format)
            worksheet.write(0, 53, 'No Plat Kendaraan Do', header_merge_format)
            worksheet.write(0, 54, 'Driver Do', header_merge_format)
            worksheet.write(0, 55, 'Partner', header_merge_format)
            worksheet.write(0, 56, 'Source Location', header_merge_format)
            worksheet.write(0, 57, 'Operation Type', header_merge_format)
            worksheet.write(0, 58, 'Scheduled Date', header_merge_format)
            worksheet.write(0, 59, 'Effective Date', header_merge_format)
            worksheet.write(0, 60, 'Source Document', header_merge_format)
            worksheet.write(0, 61, 'Product', header_merge_format)
            worksheet.write(0, 62, 'Secondary Qty', header_merge_format)
            worksheet.write(0, 63, 'Second Unit', header_merge_format)
            worksheet.write(0, 64, 'Initial Demand', header_merge_format)
            worksheet.write(0, 65, 'Done', header_merge_format)
            worksheet.write(0, 66, 'Unit Of Measure', header_merge_format)
            worksheet.write(0, 67, 'Shipping Policy', header_merge_format)
            worksheet.write(0, 68, 'Priority', header_merge_format)
            worksheet.write(0, 69, 'Number INV', header_merge_format)
            worksheet.write(0, 70, 'Customer', header_merge_format)
            worksheet.write(0, 71, 'Nomor Seri Faktur Pajak', header_merge_format)
            worksheet.write(0, 72, 'Kawasan Berikat?', header_merge_format)
            worksheet.write(0, 73, 'Delivery Address', header_merge_format)
            worksheet.write(0, 74, 'Payment Terms', header_merge_format)
            worksheet.write(0, 75, 'Tipe Barang', header_merge_format)
            worksheet.write(0, 76, 'Customer Reference', header_merge_format)
            worksheet.write(0, 77, 'SO Order Date', header_merge_format)
            worksheet.write(0, 78, 'Warehouse', header_merge_format)
            worksheet.write(0, 79, 'Invoice Date', header_merge_format)
            worksheet.write(0, 80, 'Due Date', header_merge_format)
            worksheet.write(0, 81, 'Salesperson', header_merge_format)
            worksheet.write(0, 82, 'Sales Team', header_merge_format)
            worksheet.write(0, 83, 'Currency', header_merge_format)
            worksheet.write(0, 84, 'Product', header_merge_format)
            worksheet.write(0, 85, 'Description', header_merge_format)
            worksheet.write(0, 86, 'Account', header_merge_format)
            worksheet.write(0, 87, 'Analytic Account', header_merge_format)
            worksheet.write(0, 88, 'Deferred Revenue', header_merge_format)
            worksheet.write(0, 89, 'Quantity', header_merge_format)
            worksheet.write(0, 90, 'UOM', header_merge_format)
            worksheet.write(0, 91, 'Price', header_merge_format)
            worksheet.write(0, 92, 'Disc', header_merge_format)
            worksheet.write(0, 93, 'Subtotal', header_merge_format)
            worksheet.write(0, 94, 'Total', header_merge_format)
            worksheet.write(0, 95, 'Amount Due', header_merge_format)
            worksheet.write(0, 96, 'Terbilang', header_merge_format)
            worksheet.write(0, 97, 'Billing Date', header_merge_format)
            worksheet.write(0, 98, 'Due Date', header_merge_format)
            worksheet.write(0, 99, 'Unit Price Invoice', header_merge_format)
            worksheet.write(0, 100, 'Total Price Invoice', header_merge_format)
            worksheet.write(0, 101, 'Total Price Tax', header_merge_format)
            worksheet.write(0, 102, 'PO Number ', header_merge_format)

            worksheet.write(rows, 0, line.name.name, header_data_format)
            worksheet.write(rows, 1, line.warehouse_id.name, header_data_format)
            worksheet.write(rows, 2, line.tipe_barang, header_data_format)
            worksheet.write(rows, 3, str(line.scheduled_date), header_data_format)
            worksheet.write(rows, 4, str(line.date_done), header_data_format)
            worksheet.write(rows, 5, line.team_id.name, header_data_format)
            worksheet.write(rows, 6, line.user_id.name, header_data_format)
            worksheet.write(rows, 7, line.partner_id.name, header_data_format)
            worksheet.write(rows, 8, line.partner_invoice_id.name, header_data_format)
            worksheet.write(rows, 9, line.partner_shipping_id.name, header_data_format)
            worksheet.write(rows, 10, line.client_order_ref, header_data_format)
            worksheet.write(rows, 11, str(line.date_order), header_data_format)
            worksheet.write(rows, 12, str(line.confirmation_date), header_data_format)
            worksheet.write(rows, 13, line.client_order_ref, header_data_format)
            worksheet.write(rows, 14, line.productso_id.name, header_data_format)
            worksheet.write(rows, 15, line.name_soline, header_data_format)
            worksheet.write(rows, 16, line.order_qty, header_data_format)
            worksheet.write(rows, 17, line.qty_delivered, header_data_format)
            worksheet.write(rows, 18, line.open_qty, header_data_format)
            worksheet.write(rows, 19, line.qty_invoiced, header_data_format)
            worksheet.write(rows, 20, line.product_uomso.name, header_data_format)
            worksheet.write(rows, 21, line.route_id.name, header_data_format)
            worksheet.write(rows, 22, line.discount, header_data_format)
            worksheet.write(rows, 23, line.categ_id.name, header_data_format)
            worksheet.write(rows, 24, line.order_qty, header_data_format)
            worksheet.write(rows, 25, line.uom_id.name, header_data_format)
            worksheet.write(rows, 26, line.partner_ids.name, header_data_format)
            worksheet.write(rows, 27, line.tipe_cust, header_data_format)
            worksheet.write(rows, 28, line.provinsi.name, header_data_format)
            worksheet.write(rows, 29, line.kabupaten_kota.name, header_data_format)
            worksheet.write(rows, 30, line.kecamatan.name, header_data_format)
            worksheet.write(rows, 31, line.mobile, header_data_format)
            worksheet.write(rows, 32, line.payment_term_id.name, header_data_format)
            worksheet.write(rows, 33, line.pricelist_id.name, header_data_format)
            worksheet.write(rows, 34, line.incoterm_id.name, header_data_format)
            worksheet.write(rows, 35, line.currency_id.name, header_data_format)
            worksheet.write(rows, 36, line.discount, header_data_format)
            worksheet.write(rows, 37, line.price_subtotalso, header_data_format)
            worksheet.write(rows, 38, line.note, header_data_format)
            worksheet.write(rows, 39, line.picking_policy, header_data_format)
            worksheet.write(rows, 40, str(line.expected_date), header_data_format)
            worksheet.write(rows, 41, str(line.effective_date), header_data_format)
            worksheet.write(rows, 42, line.picking_note, header_data_format)
            worksheet.write(rows, 43, str(line.analytic_account_id.name), header_data_format)
            worksheet.write(rows, 44, line.plat_idso, header_data_format)
            worksheet.write(rows, 45, str(line.driver_idso), header_data_format)
            worksheet.write(rows, 46, line.price_unit, header_data_format)
            worksheet.write(rows, 47, line.amount_total, header_data_format)
            worksheet.write(rows, 48, line.do_number.name, header_data_format)
            worksheet.write(rows, 49, line.location_id.name, header_data_format)
            worksheet.write(rows, 50, line.product_uom_qty, header_data_format)
            worksheet.write(rows, 51, line.product_uom.name, header_data_format)
            worksheet.write(rows, 52, str(line.date_dones), header_data_format)
            worksheet.write(rows, 53, line.plat_id, header_data_format)
            worksheet.write(rows, 54, line.driver_id, header_data_format)
            worksheet.write(rows, 55, line.partner_iddo.name, header_data_format)
            worksheet.write(rows, 56, line.location_id.name, header_data_format)
            worksheet.write(rows, 57, line.picking_type_id.name, header_data_format)
            worksheet.write(rows, 58, str(line.scheduled_date), header_data_format)
            worksheet.write(rows, 59, str(line.date_done), header_data_format)
            worksheet.write(rows, 60, line.origin, header_data_format)
            worksheet.write(rows, 61, line.productdo_id.name, header_data_format)
            worksheet.write(rows, 62, line.secondary_uom_id.name, header_data_format)
            worksheet.write(rows, 63, line.secondary_uom_qty, header_data_format)
            worksheet.write(rows, 64, line.product_uom_qtydo, header_data_format)
            worksheet.write(rows, 65, line.quantity_done, header_data_format)
            worksheet.write(rows, 66, line.product_uom.name, header_data_format)
            worksheet.write(rows, 67, line.move_type, header_data_format)
            worksheet.write(rows, 68, line.priority, header_data_format)
            worksheet.write(rows, 69, line.number.number, header_data_format)
            worksheet.write(rows, 70, line.partner_idinv.name, header_data_format)
            worksheet.write(rows, 71, line.efaktur_id.name, header_data_format)
            worksheet.write(rows, 72, line.is_berikat, header_data_format)
            worksheet.write(rows, 73, line.partner_iddo.name, header_data_format)
            worksheet.write(rows, 74, line.payment_term_idinv.name, header_data_format)
            worksheet.write(rows, 75, line.tipe_baranginv, header_data_format)
            worksheet.write(rows, 76, line.client_order_ref, header_data_format)
            worksheet.write(rows, 77, str(line.so_confirmation_date), header_data_format)
            worksheet.write(rows, 78, line.warehouse_id.name, header_data_format)
            worksheet.write(rows, 79, str(line.date_invoice), header_data_format)
            worksheet.write(rows, 80, str(line.date_due), header_data_format)
            worksheet.write(rows, 81, line.user_idinv.name, header_data_format)
            worksheet.write(rows, 82, line.team_idinv.name, header_data_format)
            worksheet.write(rows, 83, line.currency_id.name, header_data_format)
            worksheet.write(rows, 84, line.product_id.name, header_data_format)
            worksheet.write(rows, 85, line.name_invline, header_data_format)
            worksheet.write(rows, 86, line.account_id.name, header_data_format)
            worksheet.write(rows, 87, line.account_analytic_id.name, header_data_format)
            worksheet.write(rows, 88, '', header_data_format)
            worksheet.write(rows, 89, line.quantity, header_data_format)
            worksheet.write(rows, 90, line.uom_id.name, header_data_format)
            worksheet.write(rows, 91, line.price_unitinv, header_data_format)
            worksheet.write(rows, 92, line.discount, header_data_format)
            worksheet.write(rows, 93, line.amount_totalinv, header_data_format)
            worksheet.write(rows, 94, line.amount_totalinv, header_data_format)
            worksheet.write(rows, 95, '', header_data_format)
            worksheet.write(rows, 96, line.terbilang, header_data_format)
            worksheet.write(rows, 97, str(line.date_invoice), header_data_format)
            worksheet.write(rows, 98, str(line.date_due), header_data_format)
            worksheet.write(rows, 99, line.price_unitinv, header_data_format)
            worksheet.write(rows, 100, line.amount_totalinv, header_data_format)
            worksheet.write(rows, 101, line.amount_totaltax, header_data_format)
            worksheet.write(rows, 102, line.po_id.name, header_data_format)
            rows += 1
        workbook.close()
        self.write({
            # 'state': 'get',
            'data': base64.b64encode(open('/tmp/' + xls_filename, 'rb').read()),
            # 'name': xls_filename
        })

class tbl_report_sales_ete_detail(models.Model):
    _name = 'tbl.report.sales.ete.detail'
    _order = 'name'

    # details = fields.Many2one('tbl.report.sales.ete', string='Detail')

    so_line_id = fields.Many2one('sale.order.line','SO Line ID')
    do_line_id = fields.Many2one('stock.move','DO Line ID')
    inv_line_id = fields.Many2one('account.invoice.line','Inv Line ID')
    po_line_id = fields.Many2one('purchase.order.line','PO Line ID')
    name = fields.Many2one('sale.order','No SO')
    warehouse_id = fields.Many2one('stock.warehouse','Nama Warehouse',related='name.warehouse_id',store=True)#,related='name.warehouse_id',store=True
    tipe_barang = fields.Selection([
        ('barang', 'Barang'),
        ('jasa', 'Jasa'),
        ], string='Tipe Barang',related='name.tipe_barang',store=True)#,related='name.tipe_barang',store=True
    segmen = fields.Selection([
        ('g_trading', 'General Trading'),
        ('c_trading', 'Cement Trading'),
        ('transport', 'Transport'),
        ], string='Segmen', track_visibility='onchange', required=True,store=True)
    state = fields.Selection(string='Status SO',related='name.state', store=True)
    scheduled_date = fields.Datetime('Schedule Date',related='do_number.scheduled_date',store=True)#dari DO
    date_done = fields.Datetime('Effective Date',related='do_number.date_done',store=True)#dari DO
    team_id = fields.Many2one('crm.team', 'Sales Team',related='name.team_id',store=True)
    user_id = fields.Many2one('res.users', 'Salesperson',related='name.user_id',store=True)
    partner_id = fields.Many2one('res.partner', 'Customer Code',related='name.partner_id',store=True)
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address',related='name.partner_invoice_id',store=True)
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address',related='name.partner_shipping_id',store=True)
    client_order_ref = fields.Char(string='Customer Reference', copy=False)
    date_order = fields.Datetime( 'SO Date',related='name.date_order',store=True)
    confirmation_date = fields.Datetime( 'Confirmation Date',related='name.confirmation_date',store=True)
    productso_id = fields.Many2one('product.product', 'Product',related='so_line_id.product_id',store=True)
    name_soline = fields.Text(string='Description',related='so_line_id.name',store=True)
    qty_invoiced = fields.Float(string='Invoiced Quantity',related='so_line_id.qty_invoiced',store=True)
    product_uomso = fields.Many2one('uom.uom', string='Unit of Measure',related='so_line_id.product_uom',store=True)
    route_id = fields.Many2one('stock.location.route', string='Route',related='so_line_id.route_id',store=True)
    # tax_id = fields.Many2many('account.tax', string='Taxes',related='so_line_id.tax_id',store=True)
    discount = fields.Float(string='Discount (%)',related='so_line_id.discount',store=True)
    categ_id = fields.Many2one('product.category', 'Product Category Desc',related='product_id.categ_id',store=True)
    barcode = fields.Char('Product Barcode',related='product_id.default_code',store=True)
    order_qty = fields.Float('Order Quantity') 
    uom_id = fields.Many2one('uom.uom', 'Sales Unit')
    partner_ids = fields.Many2one('res.partner', 'Ship to Name',related='do_number.partner_id',store=True)#dari DO
    # location_dest_id = fields.Many2one('stock.location', 'Ship to Address')#dari DO
    tipe_cust = fields.Selection([
        ('grosir', 'Barang'),
        ('retail', 'Retail'),
        ('proyek', 'Proyek'),
        ], string='Tipe Customer',store=True)#,related='partner_id.jenis_customer',store=True
    provinsi = fields.Many2one("res.country.state", string='Province Desc',related='partner_id.state_id',store=True)
    kabupaten_kota = fields.Many2one(comodel_name="vit.kota", string="Kota/Kab",related='partner_id.kota_id',store=True)
    kecamatan = fields.Many2one(comodel_name="vit.kecamatan", string="Kecamatan",related='partner_id.kecamatan_id',store=True)
    mobile = fields.Char('Telephone',related='partner_id.mobile',store=True)#,related='partner_id.mobile',store=True
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms',related='name.payment_term_id',store=True)#,related='name.payment_term_id',store=True
    pricelist_id = fields.Many2one('product.pricelist', 'Price List Type',related='name.pricelist_id',store=True)#,related='name.pricelist_id',store=True
    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm',related='name.incoterm',store=True)#,related='name.incoterm',store=True
    currency_id = fields.Many2one('res.currency', 'Currency',related='name.currency_id',store=True)#,related='name.currency_id',store=True
    price_subtotalso = fields.Monetary(string='Subtotal',related='so_line_id.price_subtotal',store=True)
    note = fields.Text('Terms and conditions',related='name.note',store=True)
    picking_policy = fields.Selection([
        ('direct', 'Deliver each product when available'),
        ('one', 'Deliver all products at once')],
        string='Shipping Policy',related='name.picking_policy',store=True)
    expected_date = fields.Datetime("Expected Date",related='name.expected_date',store=True)
    effective_date = fields.Date("Effective Date",related='name.effective_date',store=True)
    picking_note = fields.Text(string="Picking Note",related='name.picking_note',store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',related='name.analytic_account_id',store=True)
    qty_delivered = fields.Float('Delivered Qty')
    open_qty = fields.Float('Open Qty', compute='_compute_open_qty',store=True) #openqty = order qty - deliver qty
    do_number = fields.Many2one('stock.picking', 'DO Number')
    location_id = fields.Many2one('stock.location', 'Source Location Desc',related='do_number.location_id',store=True)
    product_uom_qty = fields.Float('Quantity')
    product_uom = fields.Many2one('uom.uom', ' UOM')
    date_dones = fields.Datetime('Effective Date',related='do_number.date_done',store=True)
    plat_id = fields.Char('No Plat Kendaraan DO',related='do_number.plat_id',store=True)
    driver_id = fields.Char('Driver DO',related='do_number.driver_id',store=True)
    partner_iddo = fields.Many2one(
        'res.partner', 'Partner',related='do_number.partner_id',store=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',related='do_number.picking_type_id',store=True)
    scheduled_date = fields.Datetime(
        'Scheduled Date',related='do_number.scheduled_date',store=True)
    date_done = fields.Datetime('Effective Date',related='do_number.date_done',store=True)
    origin = fields.Char(
        'Source Document',related='do_number.origin',store=True)
    productdo_id = fields.Many2one('product.product', 'Product',related='do_line_id.product_id',store=True)
    secondary_uom_id = fields.Many2one(
        comodel_name='product.secondary.unit',
        string='Second unit',related='do_line_id.secondary_uom_id',store=True)
    secondary_uom_qty = fields.Float(
        string='Secondary Qty',related='do_line_id.secondary_uom_qty',store=True)
    product_uom_qtydo = fields.Float(
        'Initial Demand',related='do_line_id.product_uom_qty',store=True)
    quantity_done = fields.Float('Quantity Done',related='do_line_id.quantity_done',store=True)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure',related='do_line_id.product_uom',store=True)
    move_type = fields.Selection([
        ('direct', 'As soon as possible'), ('one', 'When all products are ready')], 'Shipping Policy',related='do_number.move_type',store=True)
    priority = fields.Selection(string='Priority',related='do_number.priority',store=True)
    plat_idso = fields.Char('No Plat Kendaraan SO',related='name.plat_id',store=True)#,related='name.plat_id',store=True
    driver_idso = fields.Char('Driver SO',related='name.plat_id',store=True)#,related='name.plat_id',store=True
    price_unit = fields.Float('Unit Price (SO)')
    amount_total = fields.Float('Total Price (SO)')
    number = fields.Many2one('account.invoice','Number INV')
    partner_idinv = fields.Many2one('res.partner', string='Customer',related='number.partner_id',store=True)
    efaktur_id  = fields.Many2one(comodel_name="vit.efaktur", string="Nomor Seri Faktur Pajak",related='number.efaktur_id',store=True)
    is_berikat = fields.Boolean(string="Kawasan Berikat?", related="partner_idinv.is_berikat",store=True )
    payment_term_idinv = fields.Many2one('account.payment.term', string='Payment Terms',related='number.payment_term_id',store=True)
    tipe_baranginv = fields.Selection([
        ('barang', 'Barang'),
        ('jasa', 'Jasa'),
        ], string='Tipe Barang',related='number.tipe_barang', store=True)
    client_order_ref = fields.Char(string='Customer Reference',related='number.client_order_ref', store=True)
    so_confirmation_date = fields.Datetime(string='SO Order Date', store=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', store=True)
    product_id = fields.Many2one('product.product', 'Product')
    date_invoice = fields.Date('Billing Date',related='number.date_invoice',store=True)#Invoice Date
    user_idinv = fields.Many2one('res.users', string='Salesperson',related='number.user_id',store=True)
    team_idinv = fields.Many2one('crm.team', 'Sales Team',related='number.team_id',store=True)
    date_due = fields.Date('Due Date',related='number.date_due',store=True)
    currency_id = fields.Many2one('res.currency', 'Currency',related='number.currency_id',store=True)
    name_invline = fields.Text('Description',related='inv_line_id.name',store=True)
    account_id = fields.Many2one('account.account', string='Account',
        readonly=True,related='inv_line_id.account_id',store=True)
    account_analytic_id = fields.Many2one('account.analytic.account',
        string='Analytic Account',related='inv_line_id.account_analytic_id',store=True)
    quantity = fields.Float(string='Quantity',related='inv_line_id.quantity',store=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',related='inv_line_id.uom_id',store=True)
    discount = fields.Float(string='Discount (%)',related='inv_line_id.discount',store=True)
    price_unitinv = fields.Float('Unit Price Invoice')
    amount_totalinv = fields.Float('Total Price Invoice')
    amount_totaltax = fields.Float('Total Price Tax')
    terbilang = fields.Char(string="Terbilang",related='number.terbilang', store=True )
    po_id = fields.Many2one('purchase.order','PO')

    @api.one
    @api.depends('order_qty','qty_delivered')
    def _compute_open_qty(self):
        if self.order_qty and self.qty_delivered:
            cari = self.env['tbl_report_sales_ete_detail'].search([('id', '<', self.id),('name', '=', self.name.id),('product_id', '=', self.product_id.id)], limit=1)
            if cari:
                self.open_qty = cari.open_qty - self.qty_delivered
            else:
                self.open_qty = self.order_qty - self.qty_delivered

class tbl_report_sales_ete_tmp(models.Model):
    _name = 'tbl.report.sales.ete.mp'
    _order = 'name'
    

    # details = fields.Many2one('tbl.report.sales.ete', string='Detail')

    so_line_id = fields.Many2one('sale.order.line','ID')
    name = fields.Many2one('sale.order','No SO')
    order_qty = fields.Float('Order Quantity')
    uom_id = fields.Many2one('uom.uom', 'Sales Unit')
    price_unit = fields.Float('Unit Price (SO)')
    amount_total = fields.Float('Total Price (SO)')
    product_id = fields.Many2one('product.product', 'Product')


class tbl_report_sales_ete_tmp2(models.Model):
    _name = 'tbl.report.sales.ete.tmp2'
    _order = 'name'

    # details = fields.Many2one('tbl.report.sales.ete', string='Detail')

    name = fields.Many2one('sale.order','No SO')
    
    order_qty = fields.Float('Order Quantity')
    uom_id = fields.Many2one('uom.uom', 'Sales Unit')
    
    location_dest_id = fields.Many2one('stock.location', 'Ship to Address')#dari DO
    
    provinsi = fields.Char('Province Desc')
    kabupaten_kota = fields.Char('Kabupaten/Kota')
    kecamatan = fields.Char('kecamatan')
    
    qty_delivered = fields.Float('Delivered Qty')
    open_qty = fields.Float('Open Qty', compute='_compute_open_qty',store=True) #openqty = order qty - deliver qty
    do_number = fields.Many2one('stock.picking', 'DO Number')
    
    product_uom_qty = fields.Float('Quantity')
    product_uom = fields.Many2one('uom.uom', ' UOM')
    
    price_unit = fields.Float('Unit Price (SO)')
    amount_total = fields.Float('Total Price (SO)')
    number = fields.Many2one('account.invoice','Number INV')
    product_id = fields.Many2one('product.product', 'Product')
   
    price_unitinv = fields.Float('Unit Price Invoice')
    amount_totalinv = fields.Float('Total Price Invoice')
    amount_totaltax = fields.Float('Total Price Tax')

    @api.one
    @api.depends('order_qty','qty_delivered')
    def _compute_open_qty(self):
        if self.order_qty and self.qty_delivered:
            self.open_qty = self.order_qty - self.qty_delivered
 

class tbl_so_detail2(models.Model):
    _inherit = 'sale.order.line'

    confirmation_date = fields.Datetime( 'SO Date',related='order_id.confirmation_date',store=True)
    date_order = fields.Datetime( 'Order Date',related='order_id.date_order',store=True)