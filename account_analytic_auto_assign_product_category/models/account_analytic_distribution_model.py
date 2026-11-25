# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    def _create_domain(self, fname, value):
        if fname == "product_categ_id" and value:
            return [
                "|",
                ("product_categ_id", "=", False),
                ("product_categ_id", "parent_of", value),
            ]
        return super()._create_domain(fname, value)

    @api.model
    def _get_applicable_models(self, vals):
        # Within the same sequence, the closest category wins over its parents.
        return (
            super()
            ._get_applicable_models(vals)
            .sorted(
                lambda model: (
                    model.sequence,
                    -len(model.product_categ_id.parent_path or ""),
                )
            )
        )
