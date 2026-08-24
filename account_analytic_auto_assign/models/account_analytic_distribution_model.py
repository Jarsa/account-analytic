# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    @api.model
    def _get_distribution(self, vals):
        """Global switch: if the business configured native rules in
        Analytic Distribution Models, the standard Odoo behavior is kept
        as-is. If that table is empty, our own engine
        (`account.analytic.auto.assign.rule`) is used instead, which merges
        several sources instead of only keeping the first match.
        """
        if self.sudo().search_count([], limit=1):
            return super()._get_distribution(vals)
        return self.env["account.analytic.auto.assign.rule"]._get_distribution(vals)
