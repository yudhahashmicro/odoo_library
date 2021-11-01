# -*- coding: utf-8 -*-
# from odoo import http


# class YudzLibrary(http.Controller):
#     @http.route('/yudz_library/yudz_library/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/yudz_library/yudz_library/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('yudz_library.listing', {
#             'root': '/yudz_library/yudz_library',
#             'objects': http.request.env['yudz_library.yudz_library'].search([]),
#         })

#     @http.route('/yudz_library/yudz_library/objects/<model("yudz_library.yudz_library"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('yudz_library.object', {
#             'object': obj
#         })
