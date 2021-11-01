# -*- coding: utf-8 -*-
from odoo import models,fields,api 
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    _description = 'Abstract Archive'

    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active

class LibraryBook(models.Model):
    _name = 'library.book'
    _inherit = ['base.archive']

    _description = 'Library Book'

    _order = 'date_release desc, name'

    _sql_constraints = [
        ('name_uniq',' UNIQUE(name)','Nama Buku mesti Unik'),
        ('positive_page','CHECK(pages > 0','No of pages must be positive')
    ]

    name = fields.Char('Judul',required=True, index=True)
    short_name = fields.Char('Judul Pendek',translate=True, index=True)
    notes= fields.Text('Catatan Pribadi')
    state = fields.Selection([('ketersediaan','Tidak Tersedia'),('tersedia','Tersedia'),('terpinjam', 'Terpinjam'),('hilang','Hilang'),('terjual','Terjual')],'Ketersediaan', default='ketersediaan')
    description = fields.Html('Description',sanitize=True, strip_style=False)
    cover = fields.Binary('Cover Buku')
    date_release = fields.Date('Tanggal Rilis')
    date_updated = fields.Datetime('Update Terakhir', copy=False)
    pages = fields.Integer('Jumlah Halaman',
        groups='base.group_user',
        states={'lost': [('readonly', True)]},
        help='Total book page count', company_dependent=False)
    reader_rating = fields.Float(
        'Rating Pembaca',
        digits=(14,2),       # Optional precision (total, decimals)
    )

    author_ids = fields.Many2many('res.partner',string='Pengarang')
    cost_price = fields.Monetary('Harga Buku', digits='Book Price')
    currency_id = fields.Many2one('res.currency',string='Mata Uang')
    retail_price = fields.Monetary('Harga Pasar') # optional attribute: currency_field='currency_id' incase currency field have another name then 'currency_id'
    publisher_id = fields.Many2one('res.partner',string='Penerbit', 
        # optional
        ondelete='set null', context={}, domain=[],)
    
    publisher_city = fields.Char('Kota Penerbit', related='publisher_id.city', readonly=True)
    category_id = fields.Many2one('library.book.category', string='Kategori')
    age_days = fields.Float(
        string='Hari Semenjak Rilis',
        compute='_compute_age', inverse='_inverse_age', search='_search_age',
        store=False,
        compute_sudo=True,
    )

    ref_doc_id = fields.Reference(selection='_referencable_models', string='Dokumen Referensi')

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('ketersediaan', 'tersedia'),
                   ('tersedia', 'terpinjam'),
                   ('terpinjam', 'tersedia'),
                   ('tersedia', 'hilang'),
                   ('terpinjam', 'hilang'),
                   ('hilang', 'tersedia'),
                   ('terjual', 'tersedia'),
                   ('tersedia', 'terjual')]
        return (old_state, new_state) in allowed
    
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                message = _('Pindah dari %s ke %s tidak diperbolehkan') % (book.state, new_state)
                raise UserError(message)

    def make_available(self):
        self.change_state('tersedia')

    def make_borrowed(self):
        self.change_state('terpinjam')

    def make_lost(self):
        self.change_state('hilang')
    
    def make_sold(self):
        self.change_state('terjual')

    @api.model
    def books_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
            return False
        return all_books.filtered(predicate)

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'

    published_book_ids = fields.One2many(
        'library.book','publisher_id',
        string='Published Books',
    )
    authored_book_ids = fields.Many2many(
        'library.book',string='Authored Books',
        # relation='library_book_res_partner_rel'  # optional
    )
    count_books = fields.Integer('Number of Authored Books',
        compute = '_compute_count_books'
    )

@api.depends('authored_book_ids')
def _compute_count_books(self):
    for r in self:
        r.count_books = len(r.authored_book_ids)


class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}
    _description = "Library Member"

    partner_id = fields.Many2one(
        'res.partner',
        ondelete = 'cascade'
    )

    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of Birth')



