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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, _
from openerp.exceptions import Warning as UserError


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.model
    def default_get(self, fields):
        fields.append('product_qty')
        res = super(MrpProductProduce, self).default_get(fields)
        if self._context.get('active_id') and res.get('product_qty'):
            production = self.env['mrp.production'].browse(
                self._context['active_id'])
            res['product_qty'] = (res['product_qty'] > 0 and
                                  production.qty_available_to_produce)
        return res

    @api.multi
    def do_produce(self):
        self.ensure_one()
        if self.product_qty > self.production_id.qty_available_to_produce:
            raise UserError(_('''You cannot produce more than available to
                                produce for this order'''))
        return super(MrpProductProduce, self).do_produce()
