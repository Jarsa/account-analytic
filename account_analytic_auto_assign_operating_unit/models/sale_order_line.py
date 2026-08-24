# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("operating_unit_id")
    def _compute_analytic_distribution(self):  # pylint: disable=missing-return
        # sale.order.line does not expose an overridable "get matching
        # arguments" method like account.move.line does, so this calls
        # super() first (letting native logic, and any other sibling
        # module's own contribution, run first) and only layers its own
        # operating_unit_id criterion on top. This lets several such
        # modules compose instead of each fully overwriting the field.
        super()._compute_analytic_distribution()
        for line in self:
            if not line.display_type and line.operating_unit_id:
                extra = line.env[
                    "account.analytic.distribution.model"
                ]._get_distribution(
                    {
                        "operating_unit_id": line.operating_unit_id.id,
                        "company_id": line.company_id.id,
                    }
                )
                if extra:
                    line.analytic_distribution = (
                        line.analytic_distribution or {}
                    ) | extra
