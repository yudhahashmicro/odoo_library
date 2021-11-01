from odoo import models, fields, api
from odoo.exceptions import ValidationError 


class BookCategory(models.Model):
    _name = 'library.book.category'
    _description = 'Library Book Category'

    _parent_store = True
    _parent_name = "parent_id"  # optional if field is 'parent_id'

    name = fields.Char('Kategori')
    description = fields.Text('Deskripsi')
    parent_id = fields.Many2one(
        'library.book.category',
        string = 'Parent Category',
        ondelete = 'restrict',
        index=True)
    parent_path = fields.Char(index=True)
