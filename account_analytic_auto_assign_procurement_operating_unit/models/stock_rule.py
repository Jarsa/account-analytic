# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        vals = super()._prepare_purchase_order(company_id, origins, values)
        sale = self._get_auto_assign_sale_order(values[0])
        if sale.operating_unit_id:
            vals["operating_unit_id"] = sale.operating_unit_id.id
            vals["requesting_operating_unit_id"] = sale.operating_unit_id.id
        return vals
