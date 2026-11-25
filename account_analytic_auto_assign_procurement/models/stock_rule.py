# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_auto_assign_sale_order(self, values):
        return self.env["sale.order.line"].browse(values.get("sale_line_id")).order_id

    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        project = self._get_auto_assign_sale_order(values).analytic_account_id
        return domain + (("analytic_account_id", "=", project.id),)

    def _prepare_purchase_order(self, company_id, origins, values):
        vals = super()._prepare_purchase_order(company_id, origins, values)
        sale = self._get_auto_assign_sale_order(values[0])
        vals["analytic_account_id"] = sale.analytic_account_id.id
        # Only when sale_operating_unit and purchase_operating_unit are there.
        if "operating_unit_id" in sale._fields and sale.operating_unit_id:
            vals["operating_unit_id"] = sale.operating_unit_id.id
        return vals
