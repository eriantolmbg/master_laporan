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

class tbl_report_purchase(models.Model):
    _name = 'tbl_report_purchase'

    name = fields.Char('Name',default='Purchase')
    tgl_awal = fields.Datetime('Tanggal Awal', required=True)
    tgl_akhir = fields.Datetime('Tanggal Akhir', required=True)
    data = fields.Binary(string='File', readonly=True)
    detail = fields.One2many('tbl_report_purchase_detail','details', string='Detail')
    detail1 = fields.One2many('tbl_report_purchase_tmp','details', string='Detail')
    detail2 = fields.One2many('tbl_report_purchase_tmp2','details', string='Detail')

    def act_pr(self):
        detail1_obj = self.env['tbl_report_purchase_tmp']

        if self.detail1:
           self.detail1.unlink()
        pr=0
        self.env.cr.execute('Select id, request_id, product_id, name, product_qty, product_uom_id, analytic_account_id, date_required, estimated_cost, currency_id From \
                            purchase_request_line\
                            where date_required >=%s and date_required <=%s', (self.tgl_awal, self.tgl_akhir))# and purchase_lines is null
        for row in self.env.cr.fetchall():
            pr=row[0]
            cari = self.env['tbl_report_purchase_tmp'].search([('prline_no', '=', pr)], limit=1)
            if not cari:
                # cari2 = self.env['purchase.request.line'].search([('id', '=', pr)], limit=1)
                # if cari2:
                #     if not cari2.purchase_lines:
                data_line2 = detail1_obj.create({
                            'details': self.id,
                            'name': row[1],
                            'prline_no': row[0],
                            'product_id': row[2],
                            'desc': row[3],
                            'product_qty': row[4],
                            'product_uom_id': row[5],
                            'analytic_account_id': row[6],
                            'date_required': row[7],
                            'estimated_cost': row[8],
                            'currency_id': row[9],
                })
            else:
                raise UserError(_('%s sudah di Get Sebelumnya' % (cari.name.name, )))

    def act_po(self):
        detail1_obj = self.env['tbl_report_purchase_tmp2']

        if self.detail2:
           self.detail2.unlink()
        po=0
        self.env.cr.execute('Select id, order_id, product_id, product_qty, price_unit, price_total, account_analytic_id From \
                            purchase_order_line\
                            where date_planned >=%s and date_planned <=%s', (self.tgl_awal, self.tgl_akhir))# and purchase_lines is null
        for row in self.env.cr.fetchall():
            po=row[0]
            cari = self.env['tbl_report_purchase_tmp2'].search([('poline_id', '=', po)], limit=1)
            if not cari:
                cari2 = self.env['purchase.order.line'].search([('id', '=', po)], limit=1)
                if cari2:
                    if not cari2.purchase_request_lines:
                        data_line2 = detail1_obj.create({
                            'details': self.id,
                            'po_id': row[1],
                            'poline_id': row[0],
                            'product_id': row[2],
                            'product_qty_po': row[3],
                            'price_unit': row[4],
                            'amount_total': row[5],
                            'analytic_account_po_id': row[6],
                        })
            else:
                raise UserError(_('%s sudah di Get Sebelumnya' % (cari.po_id.name, )))

    def act_get_data(self):
        detail_obj = self.env['tbl_report_purchase_detail']

        if self.detail:
           self.detail.unlink()
        if self.detail1:
          for line in self.detail1:
            if not line.prline_no.purchase_lines:
                data_line2 = detail_obj.create({
                            'details': self.id,
                            'name': line.name.id,
                            'product_id': line.product_id.id,
                            'desc': line.desc,
                            'product_qty': line.product_qty,
                            'product_uom_id': line.product_uom_id.id,
                            'analytic_account_id': line.analytic_account_id.id,
                            'date_required': line.date_required,
                            'estimated_cost': line.estimated_cost,
                            'currency_id': line.currency_id.id,
                })
            else:
                for line1 in line.prline_no.purchase_lines:
                    if not line1.move_ids and not line1.invoice_lines:
                        data_line2 = detail_obj.create({
                            'details': self.id,
                            'name': line.name.id,
                            'product_id': line.product_id.id,
                            'desc': line.desc,
                            'product_qty': line.product_qty,
                            'product_uom_id': line.product_uom_id.id,
                            'analytic_account_id': line.analytic_account_id.id,
                            'date_required': line.date_required,
                            'estimated_cost': line.estimated_cost,
                            'currency_id': line.currency_id.id,
                            'po_id': line1.order_id.id,
                            'product_qty_po': line1.product_qty,
                            'price_unit': line1.price_unit,
                            'amount_total': line1.price_total,
                            'analytic_account_po_id': line1.account_analytic_id.id,
                        })
                    if line1.move_ids and not line1.invoice_lines:
                        for move in line1.move_ids:
                            data_line2 = detail_obj.create({
                                'details': self.id,
                                'name': line.name.id,
                                'product_id': line.product_id.id,
                                'desc': line.desc,
                                'product_qty': line.product_qty,
                                'product_uom_id': line.product_uom_id.id,
                                'analytic_account_id': line.analytic_account_id.id,
                                'date_required': line.date_required,
                                'estimated_cost': line.estimated_cost,
                                'currency_id': line.currency_id.id,
                                'po_id': line1.order_id.id,
                                'product_qty_po': line1.product_qty,
                                'price_unit': line1.price_unit,
                                'amount_total': line1.price_total,
                                'analytic_account_po_id': line1.account_analytic_id.id,
                                'receipt_number': move.picking_id.id,
                                'qty_done': move.product_uom_qty,
                            })
                    if not line1.move_ids and line1.invoice_lines:
                        for bill in line1.invoice_lines:
                            data_line2 = detail_obj.create({
                                'details': self.id,
                                'name': line.name.id,
                                'product_id': line.product_id.id,
                                'desc': line.desc,
                                'product_qty': line.product_qty,
                                'product_uom_id': line.product_uom_id.id,
                                'analytic_account_id': line.analytic_account_id.id,
                                'date_required': line.date_required,
                                'estimated_cost': line.estimated_cost,
                                'currency_id': line.currency_id.id,
                                'po_id': line1.order_id.id,
                                'product_qty_po': line1.product_qty,
                                'price_unit': line1.price_unit,
                                'amount_total': line1.price_total,
                                'analytic_account_po_id': line1.account_analytic_id.id,
                                'number': bill.invoice_id.id,
                                'quantity': bill.quantity,
                                'price_unitinv': bill.price_unit,
                                'amount_totalinv': bill.price_subtotal,
                                'amount_totaltax': bill.price_tax,
                            })
                    if line1.move_ids and line1.invoice_lines:
                        for move in line1.move_ids:
                            cari_inv_line = self.env['account.invoice.line'].search([('purchase_line_id', '=', move.purchase_line_id.id)], limit=1)
                            if cari_inv_line:
                                for bill in cari_inv_line:
                                    data_line2 = detail_obj.create({
                                        'details': self.id,
                                        'name': line.name.id,
                                        'product_id': line.product_id.id,
                                        'desc': line.desc,
                                        'product_qty': line.product_qty,
                                        'product_uom_id': line.product_uom_id.id,
                                        'analytic_account_id': line.analytic_account_id.id,
                                        'date_required': line.date_required,
                                        'estimated_cost': line.estimated_cost,
                                        'currency_id': line.currency_id.id,
                                        'po_id': line1.order_id.id,
                                        'product_qty_po': line1.product_qty,
                                        'price_unit': line1.price_unit,
                                        'amount_total': line1.price_total,
                                        'analytic_account_po_id': line1.account_analytic_id.id,
                                        'receipt_number': move.picking_id.id,
                                        'qty_done': move.product_uom_qty,
                                        'number': bill.invoice_id.id,
                                        'quantity': bill.quantity,
                                        'price_unitinv': bill.price_unit,
                                        'amount_totalinv': bill.price_subtotal,
                                        'amount_totaltax': bill.price_tax,
                                    })
        if self.detail2:
            for detail in self.detail2:
                for line1 in detail.poline_id:
                    if not line1.move_ids and not line1.invoice_lines:
                        data_line2 = detail_obj.create({
                            'details': self.id,
                            'name': detail.name.id,
                            'product_id': detail.product_id.id,
                            'desc': detail.desc,
                            'product_qty': detail.product_qty,
                            'product_uom_id': detail.product_uom_id.id,
                            'analytic_account_id': detail.analytic_account_id.id,
                            'date_required': detail.date_required,
                            'estimated_cost': detail.estimated_cost,
                            'currency_id': detail.currency_id.id,
                            'po_id': detail.po_id.id,
                            'product_qty_po': line1.product_qty,
                            'price_unit': line1.price_unit,
                            'amount_total': line1.price_total,
                            'analytic_account_po_id': line1.account_analytic_id.id,
                        })
                    if line1.move_ids and not line1.invoice_lines:
                        for move in line1.move_ids:
                            data_line2 = detail_obj.create({
                                'details': self.id,
                                'name': detail.name.id,
                                'product_id': detail.product_id.id,
                                'desc': detail.desc,
                                'product_qty': detail.product_qty,
                                'product_uom_id': detail.product_uom_id.id,
                                'analytic_account_id': detail.analytic_account_id.id,
                                'date_required': detail.date_required,
                                'estimated_cost': detail.estimated_cost,
                                'currency_id': detail.currency_id.id,
                                'po_id': line1.order_id.id,
                                'product_qty_po': line1.product_qty,
                                'price_unit': line1.price_unit,
                                'amount_total': line1.price_total,
                                'analytic_account_po_id': line1.account_analytic_id.id,
                                'receipt_number': move.picking_id.id,
                                'qty_done': move.product_uom_qty,
                            })
                    if not line1.move_ids and line1.invoice_lines:
                        for bill in line1.invoice_lines:
                            data_line2 = detail_obj.create({
                                'details': self.id,
                                'name': detail.name.id,
                                'product_id': detail.product_id.id,
                                'desc': detail.desc,
                                'product_qty': detail.product_qty,
                                'product_uom_id': detail.product_uom_id.id,
                                'analytic_account_id': detail.analytic_account_id.id,
                                'date_required': detail.date_required,
                                'estimated_cost': detail.estimated_cost,
                                'currency_id': detail.currency_id.id,
                                'po_id': line1.order_id.id,
                                'product_qty_po': line1.product_qty,
                                'price_unit': line1.price_unit,
                                'amount_total': line1.price_total,
                                'analytic_account_po_id': line1.account_analytic_id.id,
                                'number': bill.invoice_id.id,
                                'quantity': bill.quantity,
                                'price_unitinv': bill.price_unit,
                                'amount_totalinv': bill.price_subtotal,
                                'amount_totaltax': bill.price_tax,
                            })
                    if line1.move_ids and line1.invoice_lines:
                        for move in line1.move_ids:
                            cari_inv_line = self.env['account.invoice.line'].search([('purchase_line_id', '=', move.purchase_line_id.id)], limit=1)
                            if cari_inv_line:
                                for bill in cari_inv_line:
                                    data_line2 = detail_obj.create({
                                        'details': self.id,
                                        'name': line.name.id,
                                        'product_id': line.product_id.id,
                                        'desc': line.desc,
                                        'product_qty': line.product_qty,
                                        'product_uom_id': line.product_uom_id.id,
                                        'analytic_account_id': line.analytic_account_id.id,
                                        'date_required': line.date_required,
                                        'estimated_cost': line.estimated_cost,
                                        'currency_id': line.currency_id.id,
                                        'po_id': line1.order_id.id,
                                        'product_qty_po': line1.product_qty,
                                        'price_unit': line1.price_unit,
                                        'amount_total': line1.price_total,
                                        'analytic_account_po_id': line1.account_analytic_id.id,
                                        'receipt_number': move.picking_id.id,
                                        'qty_done': move.product_uom_qty,
                                        'number': bill.invoice_id.id,
                                        'quantity': bill.quantity,
                                        'price_unitinv': bill.price_unit,
                                        'amount_totalinv': bill.price_subtotal,
                                        'amount_totaltax': bill.price_tax,
                                    })

    @api.multi
    def print_xls_report(self):
        xls_filename = 'Purchase End to End '+str(self.tgl_awal)+' - '+str(self.tgl_akhir)+'.xlsx'
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
            worksheet.write(0, 0, 'No PR', header_merge_format)
            worksheet.write(0, 1, 'Nama Product', header_merge_format)
            worksheet.write(0, 2, 'Description', header_merge_format)
            worksheet.write(0, 3, 'Quantity', header_merge_format)
            worksheet.write(0, 4, 'Product Unit of Measure', header_merge_format)
            worksheet.write(0, 5, 'Analytic Account', header_merge_format)
            worksheet.write(0, 6, 'Request Date', header_merge_format)
            worksheet.write(0, 7, 'Estimated Cost', header_merge_format)
            worksheet.write(0, 8, 'Currency', header_merge_format)
            worksheet.write(0, 9, 'No PO', header_merge_format)
            worksheet.write(0, 10, 'Nama Warehouse', header_merge_format)
            worksheet.write(0, 11, 'Vendor', header_merge_format)
            worksheet.write(0, 12, 'Qty Order', header_merge_format)
            worksheet.write(0, 13, 'Unit Price', header_merge_format)
            worksheet.write(0, 14, 'Total Price', header_merge_format)
            worksheet.write(0, 15, 'Tgl PO', header_merge_format)
            worksheet.write(0, 16, 'Status', header_merge_format)
            worksheet.write(0, 17, 'Picking Type', header_merge_format)
            worksheet.write(0, 18, 'Analytic Account', header_merge_format)
            worksheet.write(0, 19, 'Currency (PO)', header_merge_format)
            worksheet.write(0, 20, 'Scheduled Date', header_merge_format)
            worksheet.write(0, 21, 'Receipt Number', header_merge_format)
            worksheet.write(0, 22, 'Done Qty', header_merge_format)
            worksheet.write(0, 23, 'Number Vendor Bill', header_merge_format)
            worksheet.write(0, 24, 'Bill Date', header_merge_format)
            worksheet.write(0, 25, 'Currency (Bill)', header_merge_format)
            worksheet.write(0, 26, 'Quantity', header_merge_format)
            worksheet.write(0, 27, 'Unit Price Bill', header_merge_format)
            worksheet.write(0, 28, 'Total Price Bill', header_merge_format)
            worksheet.write(0, 29, 'Total Price Tax', header_merge_format)
            worksheet.write(0, 30, 'Purchase Representative', header_merge_format)
            # worksheet.write(0, 31, 'No Plat Kendaraan So', header_merge_format)
            # worksheet.write(0, 32, 'Driver So', header_merge_format)
            # worksheet.write(0, 33, 'Unit Price(SO)', header_merge_format)
            # worksheet.write(0, 34, 'Total Price(SO)', header_merge_format)
            # worksheet.write(0, 35, 'Number INV', header_merge_format)
            # worksheet.write(0, 36, 'Product', header_merge_format)
            # worksheet.write(0, 37, 'Billing Date', header_merge_format)
            # worksheet.write(0, 38, 'Due Date', header_merge_format)
            # worksheet.write(0, 39, 'Unit Price Invoice', header_merge_format)
            # worksheet.write(0, 40, 'Total Price Invoice', header_merge_format)
            # worksheet.write(0, 41, 'Total Price Tax', header_merge_format)

            worksheet.write(rows, 0, line.name.name, header_data_format)
            worksheet.write(rows, 1, line.product_id.name, header_data_format)
            worksheet.write(rows, 2, line.desc, header_data_format)
            worksheet.write(rows, 3, line.product_qty, header_data_format)
            worksheet.write(rows, 4, line.product_uom_id.name, header_data_format)
            worksheet.write(rows, 5, line.analytic_account_id.name, header_data_format)
            worksheet.write(rows, 6, str(line.date_required), header_data_format)
            worksheet.write(rows, 7, line.estimated_cost, header_data_format)
            worksheet.write(rows, 8, line.currency_id.name, header_data_format)
            worksheet.write(rows, 9, line.po_id.name, header_data_format)
            worksheet.write(rows, 10, line.warehouse_id.name, header_data_format)
            worksheet.write(rows, 11, line.supplier_id.name, header_data_format)
            worksheet.write(rows, 12, line.product_qty_po, header_data_format)
            worksheet.write(rows, 13, line.price_unit, header_data_format)
            worksheet.write(rows, 14, line.amount_total, header_data_format)
            worksheet.write(rows, 15, str(line.date_order), header_data_format)
            worksheet.write(rows, 16, line.state, header_data_format)
            worksheet.write(rows, 17, line.picking_type_id.name, header_data_format)
            worksheet.write(rows, 18, line.analytic_account_po_id.name, header_data_format)
            worksheet.write(rows, 19, line.currency_po.name, header_data_format)
            worksheet.write(rows, 20, str(line.date_planned), header_data_format)
            worksheet.write(rows, 21, line.receipt_number.name, header_data_format)
            worksheet.write(rows, 22, line.qty_done, header_data_format)
            worksheet.write(rows, 23, line.number.number, header_data_format)
            worksheet.write(rows, 24, str(line.bill_date), header_data_format)
            worksheet.write(rows, 25, line.currency_inv.name, header_data_format)
            worksheet.write(rows, 26, line.quantity, header_data_format)
            worksheet.write(rows, 27, line.price_unitinv, header_data_format)
            worksheet.write(rows, 28, line.amount_totalinv, header_data_format)
            worksheet.write(rows, 29, line.amount_totaltax, header_data_format)
            worksheet.write(rows, 30, line.user_id.name, header_data_format)
            # worksheet.write(rows, 31, line.plat_idso, header_data_format)
            # worksheet.write(rows, 32, line.driver_idso, header_data_format)
            # worksheet.write(rows, 33, line.price_unit, header_data_format)
            # worksheet.write(rows, 34, line.amount_total, header_data_format)
            # worksheet.write(rows, 35, line.number.number, header_data_format)
            # worksheet.write(rows, 36, line.product_id.name, header_data_format)
            # worksheet.write(rows, 37, str(line.date_invoice), header_data_format)
            # worksheet.write(rows, 38, str(line.date_due), header_data_format)
            # worksheet.write(rows, 39, line.price_unitinv, header_data_format)
            # worksheet.write(rows, 40, line.amount_totalinv, header_data_format)
            # worksheet.write(rows, 41, line.amount_totaltax, header_data_format)
            rows += 1
        workbook.close()
        self.write({
            # 'state': 'get',
            'data': base64.b64encode(open('/tmp/' + xls_filename, 'rb').read()),
            # 'name': xls_filename
        })

    @api.one
    def unlink(self):
        for rec in self:
            if self.detail:
                self.detail.unlink()
            if self.detail1:
                self.detail1.unlink()
            if self.detail2:
                self.detail2.unlink()
        return super(tbl_report_purchase, self).unlink()

class tbl_report_purchase_detail(models.Model):
    _name = 'tbl_report_purchase_detail'
    _order = 'po_id, name, id'

    details = fields.Many2one('tbl_report_purchase', string='Detail')
 #PR
    name = fields.Many2one('purchase.request','Nomor PR')
    product_id = fields.Many2one('product.product', 'Nama Product')
    desc = fields.Char('Description')
    product_qty = fields.Float('Quantity',digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure')
    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')
    date_required = fields.Date(string='Request Date', required=True,default=fields.Date.context_today)
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one("res.currency", string="Currency")
 #PO
    po_id = fields.Many2one('purchase.order', 'No PO')
    # type_po = fields.Selection([
    #     ('barang', 'Barang'),
    #     ('jasa', 'Jasa'),
    #     ], string='Tipe PO')
    warehouse_id = fields.Many2one('stock.warehouse', 'Nama Warehouse',related='picking_type_id.warehouse_id',store=True)
    supplier_id = fields.Many2one('res.partner',string='Vendor',related='po_id.partner_id',store=True)
    product_qty_po = fields.Float('Qty Order')
    price_unit = fields.Float('Unit Price')
    amount_total = fields.Float('Total Price')
    date_order = fields.Datetime('Tgl PO',related='po_id.date_order',store=True)
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status',related='po_id.state',store=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',related='po_id.picking_type_id',store=True)
    analytic_account_po_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    currency_po = fields.Many2one('res.currency', 'Currency (PO)')
    date_planned = fields.Date('Scheduled Date')
 #RECEIVE
    receipt_number = fields.Many2one('stock.picking', 'Receipt Number')
    qty_done = fields.Float('Done Qty')
 #BILL
    number = fields.Many2one('account.invoice','Number Vendor Bill')
    bill_date = fields.Date('Bill Date')
    currency_inv = fields.Many2one('res.currency', 'Currency (Bill)')
    quantity = fields.Float('Quantity')
    price_unitinv = fields.Float('Unit Price Bill')
    amount_totalinv = fields.Float('Total Price Bill')
    amount_totaltax = fields.Float('Total Price Tax')
    user_id = fields.Many2one('res.users', string='Purchase Representative',related='po_id.user_id',store=True)

class tbl_report_purchase_tmp(models.Model):
    _name = 'tbl_report_purchase_tmp'

    details = fields.Many2one('tbl_report_purchase', string='Detail')
 #PR
    name = fields.Many2one('purchase.request','Nomor PR')
    prline_no = fields.Many2one('purchase.request.line','Nomor PR Line')
    product_id = fields.Many2one('product.product', 'Nama Product')
    desc = fields.Char('Description')
    product_qty = fields.Float('Quantity',digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure')
    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')
    date_required = fields.Date(string='Request Date', required=True,default=fields.Date.context_today)
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one("res.currency", string="Currency")


class tbl_report_purchase_tmp2(models.Model):
    _name = 'tbl_report_purchase_tmp2'

    details = fields.Many2one('tbl_report_purchase', string='Detail')
#PR
    name = fields.Many2one('purchase.request','Nomor PR')
    prline_no = fields.Many2one('purchase.request.line','Nomor PR Line')
    product_id = fields.Many2one('product.product', 'Nama Product')
    desc = fields.Char('Description')
    product_qty = fields.Float('Quantity',digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure')
    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')
    date_required = fields.Date(string='Request Date', required=True,default=fields.Date.context_today)
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one("res.currency", string="Currency")

#PO
    po_id = fields.Many2one('purchase.order', 'No PO')
    poline_id = fields.Many2one('purchase.order.line', 'No PO Line')
    type_po = fields.Selection([
        ('barang', 'Barang'),
        ('jasa', 'Jasa'),
        ], string='Tipe PO')
    warehouse_id = fields.Many2one('stock.warehouse', 'Nama Warehouse')
    supplier_id = fields.Many2one('res.partner',string='Vendor')
    product_qty_po = fields.Float('Qty Order')
    price_unit = fields.Float('Unit Price')
    amount_total = fields.Float('Total Price')
    date_order = fields.Date('Tgl PO')
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type')
    analytic_account_po_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    currency_po = fields.Many2one('res.currency', 'Currency (PO)')
    date_planned = fields.Date('Scheduled Date')