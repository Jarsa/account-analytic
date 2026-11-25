# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        ondelete="cascade",
        check_company=True,
        help="Only applies to documents of this operating unit.",
    )

    @api.model
    def _get_default_search_domain_vals(self):
        return super()._get_default_search_domain_vals() | {
            "operating_unit_id": False,
        }

    @api.model
    def _get_distribution(self, vals):
        # Sale and purchase lines build their own fixed arguments, so their
        # operating unit comes through the context (see sale_order_line.py).
        if (
            "operating_unit_id" not in vals
            and "auto_assign_operating_unit_id" in self.env.context
        ):
            vals = vals | {
                "operating_unit_id": self.env.context["auto_assign_operating_unit_id"]
            }
        return super()._get_distribution(vals)
