# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    distribution_template_id = fields.Many2one(
        comodel_name="account.analytic.distribution.template",
        help="Pick a saved percentage split to apply to this line's"
        " analytic distribution.",
    )

    @api.onchange("distribution_template_id")
    def _onchange_distribution_template_id(self):
        if self.distribution_template_id:
            self.analytic_distribution = (
                self.distribution_template_id.analytic_distribution
            )
