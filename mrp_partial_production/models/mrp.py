# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Jose Morales <jose@vauxoo.com>
#    Planned by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Jose Morales <jose@vauxoo.com>
############################################################################
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
from collections import defaultdict
import math

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    @api.depends('availability', 'state', 'move_raw_ids')
    def _compute_qty_to_produce(self):
        """Used to shown the quantity available to produce considering the
        reserves in the moves related
        """
        for record in self:
            total = record.get_qty_available_to_produce()
            record.qty_available_to_produce = total

    qty_available_to_produce = fields.Float(
        string='Quantity Available to Produce',
        compute='_compute_qty_to_produce', readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help='Quantity available to produce considering the quantities '
        'reserved by the order')

    @api.multi
    def test_ready(self):
        res = super(MrpProduction, self).test_ready()
        for record in self:
            if record.qty_available_to_produce > 0:
                res = True
        return res

    @api.multi
    def get_qty_available_to_produce(self):
        """Compute the total available to produce considering
        the lines reserved
        """
        self.ensure_one()

        quantity = self.product_uom_id._compute_quantity(
            self.product_qty, self.bom_id.product_uom_id)
        if not quantity:
            return 0

        lines = self.bom_id.explode(self.product_id, quantity)[1]

        result, lines_dict = defaultdict(int), defaultdict(int)
        for res in self.move_raw_ids.filtered(lambda move: not move.is_done):
            result[res.product_id.id] += (res.reserved_availability -
                                          res.quantity_done)

        for line, line_data in lines:
            lines_dict[line.product_id.id] += line_data['qty'] / quantity

        qty = [(result[key] / val) for key, val in lines_dict.items()
               if val]
        res = 0
        if qty and min(qty) > 0:
            res = math.floor(min(qty) * self.bom_id.product_qty)
        return res
