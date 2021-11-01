# -*- coding: utf-8 -*-
from odoo import models,fields,api
from odoo.exceptions import ValidationError
from datetime import timedelta


class OrderBook(models.Model):
    _name = 'library.book.order'
    _description = 'Daftar Order Buku Yudz Library'
    _inherit = 'library.book'

    buyer = fields.Char('Nama Pemesan',required=True, index=True)
    tanggal_masuk = fields.Datetime(
        default=fields.Datetime.now,
        )
    name_id = fields.Many2many(
        comodel_name = 'library.book', 
        string = 'Judul Buku')

    pesanan = fields.Char(
        compute='_compute_jml_pesanan', 
        string='Jumlah Pesanan')
    
    @api.depends('name_id')
    def _compute_jml_pesanan(self):        
        for record in self:
            record.pesanan +=len(record.name_id)
    
    total_harga = fields.Integer(compute='_compute_total_harga', string='Total Tagihan')
   
    @api.model
    def _compute_total_harga(self):        
        for record in self:           
                total = sum(self.env['library.book.order'].mapped('jmlh_id'))
                record.total_harga = total
