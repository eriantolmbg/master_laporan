# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode

import math


class tbl_cashflow(models.Model):
    _name = 'tbl_cashflow'


    name = fields.Many2one('tbl_cashflow_template','Name')
    tgl_awal1 = fields.Date('Tanggal Awal')
    tgl_akhir1 = fields.Date('Tanggal Akhir')
    tgl_awal2 = fields.Date('Tanggal Awal')
    tgl_akhir2 = fields.Date('Tanggal Akhir')
    prioritas =  fields.Selection([
        (0, 'Zero'),
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Med'),
        (4, 'High'),
        (5, 'Very High'),
    ], string='Priority', default='0')
    detail = fields.One2many('tbl_cashflow_line','details', 'Detail')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('get', 'Proses'),
        ('calculate', 'Kalkulasi'),
        ('done', 'Done'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    @api.one
    def action_get(self):
        if not self.name:
           raise UserError(_('Nama Template tidak boleh kosong'))
        
        for param in self.name.detail:
            if param.name.parent:
                self.env.cr.execute("INSERT into tbl_cashflow_line (details, parameter_id, name, parent_id, baris ) \
                                                                          values (%s,%s,%s,%s,%s)\
                                                                         ",(self.id, param.name.id, param.name.desc, param.name.parent.id, param.baris))
            else:
                self.env.cr.execute("INSERT into tbl_cashflow_line (details, parameter_id, name, baris ) \
                                                                          values (%s,%s,%s,%s)\
                                                                         ",(self.id, param.name.id, param.name.desc, param.baris))
        self.state = 'get'

    @api.one
    def action_hitung(self):
        hasil_posted=0 
        hasil_reconciled=0 
        hasil_posted2=0 
        hasil_reconciled2=0 

        if self.tgl_awal1 and self.tgl_akhir1:
          for get in self.detail:
             self.env.cr.execute("select sum(amount) from account_payment where cashflow_id = %s and payment_date >= %s and payment_date <= %s and state = %s", (get.parameter_id.id,self.tgl_awal1,self.tgl_akhir1,'posted'))
             for posted in self.env.cr.fetchall():
                 get.nominal_v11 = posted[0]
             self.env.cr.execute("select sum(amount) from account_payment where cashflow_id = %s and payment_date >= %s and payment_date <= %s and state = %s", (get.parameter_id.id,self.tgl_awal1,self.tgl_akhir1,'reconciled'))
             for recon in self.env.cr.fetchall():
                 get.nominal_v12 = recon[0]

        if self.tgl_awal2 and self.tgl_akhir2:
        
          for get in self.detail:
             self.env.cr.execute("select sum(amount) from account_payment where cashflow_id = %s and payment_date >= %s and payment_date <= %s and state = %s", (get.parameter_id.id,self.tgl_awal2,self.tgl_akhir2,'posted'))
             for posted in self.env.cr.fetchall():
                 get.nominal_v21 = posted[0]
             self.env.cr.execute("select sum(amount) from account_payment where cashflow_id = %s and payment_date >= %s and payment_date <= %s and state = %s", (get.parameter_id.id,self.tgl_awal2,self.tgl_akhir2,'reconciled'))
             for recon in self.env.cr.fetchall():
                 get.nominal_v22 = recon[0]

        self.state = 'calculate'

    @api.one
    def action_calculate(self):
        for get in self.detail:
             self.env.cr.execute("select sum(nominal_v11) from tbl_cashflow_line where parent_id = %s and details = %s", (get.parameter_id.id,self.id))
             hasil = self.env.cr.fetchall()
             if hasil:
               for posted in hasil:
                   if posted[0]:
                       get.nominal_v11 = posted[0]
             self.env.cr.execute("select sum(nominal_v12) from tbl_cashflow_line where parent_id = %s and details = %s", (get.parameter_id.id,self.id))
             hasil2 = self.env.cr.fetchall()
             if hasil2:
               for posted in hasil2:
                 get.nominal_v12 = posted[0]

        self.state = 'done'







class tbl_cashflow_line(models.Model):
    _name = 'tbl_cashflow_line'
    _order = 'baris'

    details = fields.Many2one('tbl_cashflow', 'Detail')
    baris = fields.Integer('Baris')
    parameter_id = fields.Many2one('tbl_cashflow_parameter','Parameter Id')
    parent_id = fields.Many2one('tbl_cashflow_parameter','Parent Id')
    name = fields.Char(' ')
    nominal_v11 = fields.Float('Nominal Float')
    nominal_v12 = fields.Float('Nominal Float')
    nominal = fields.Char(' ', compute='_comp_nominal_v')
    nominal_v21 = fields.Float('Nominal Float')
    nominal_v22 = fields.Float('Nominal Float')
    nominal2 = fields.Char(' ', compute='_comp_nominal_v')

    @api.one
    @api.depends('nominal_v11','nominal_v12','nominal_v21','nominal_v22')
    def _comp_nominal_v(self):
        self.nominal = str(self.nominal_v11 + self.nominal_v12)
        self.nominal2 = str(self.nominal_v21 + self.nominal_v22)


class tbl_cashflow_template(models.Model):
    _name = 'tbl_cashflow_template'

    name = fields.Char('Name')
    detail = fields.One2many('tbl_cashflow_template_detail','details','Detail Template')

class tbl_cashflow_template_detail(models.Model):
    _name = 'tbl_cashflow_template_detail'
    _order = 'baris'

    details = fields.Many2one('tbl_cashflow_template','Detail')
    baris = fields.Integer('Baris')
    name = fields.Many2one('tbl_cashflow_parameter', 'Deskripsi')
    nominal = fields.Char('')

class tbl_cashflow_parameter(models.Model):
    _name = 'tbl_cashflow_parameter'

    parent = fields.Many2one('tbl_cashflow_parameter','Parent')
    name = fields.Char('Name')
    desc = fields.Char('Descriptiom')
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type', required=True)
    link = fields.Boolean('Link')

class tbl_cashflow_payment(models.Model):
    _inherit = 'account.payment'

    cashflow_id = fields.Many2one('tbl_cashflow_parameter', 'Cashflow')
    set_cashflow = fields.Boolean('Set Cashflow')

    def action_set_cashflow(self):
        self.set_cashflow = True

    def action_cancel_cashflow(self):
        self.set_cashflow = False