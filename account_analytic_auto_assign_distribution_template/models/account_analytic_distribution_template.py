# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticDistributionTemplate(models.Model):
    _name = "account.analytic.distribution.template"
    _inherit = ["analytic.mixin"]
    _description = "Reusable Analytic Distribution Template"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        ondelete="cascade",
    )
