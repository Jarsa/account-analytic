# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.fields import Domain
from odoo.tools import SQL


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Technical search-only field: lets stock.rule._make_po_get_domain() look
    # for a draft PO holding a line with exactly the same analytic
    # distribution. The value is the distribution serialized as JSON, which
    # keeps the domain hashable (procurements are grouped by domain).
    mto_analytic_distribution_key = fields.Char(
        compute="_compute_mto_analytic_distribution_key",
        search="_search_mto_analytic_distribution_key",
    )

    def _compute_mto_analytic_distribution_key(self):
        self.mto_analytic_distribution_key = False

    def _search_mto_analytic_distribution_key(self, operator, value):
        if operator not in ("=", "in"):
            return NotImplemented
        values = [value] if operator == "=" else list(value)
        values = [v for v in values if v]
        if not values:
            return Domain.FALSE
        return Domain(
            "order_line",
            "any",
            Domain.custom(
                to_sql=lambda table: SQL(
                    "%s = ANY(%s::jsonb[])", table.analytic_distribution, values
                )
            ),
        )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _find_candidate(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        # Never merge a procurement into a PO line that has another analytic
        # distribution.
        lines = self
        if values.get("analytic_distribution"):
            lines = self.filtered(
                lambda line: (
                    line.analytic_distribution == values["analytic_distribution"]
                )
            )
        return super(PurchaseOrderLine, lines)._find_candidate(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
