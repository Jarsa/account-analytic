# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticAutoAssignRule(models.Model):
    _inherit = "account.analytic.auto.assign.rule"

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        ondelete="cascade",
        check_company=True,
        help="Only applies to documents for this operating unit.",
    )

    def _get_default_search_domain_vals(self):
        return super()._get_default_search_domain_vals() | {
            "operating_unit_id": False,
        }
