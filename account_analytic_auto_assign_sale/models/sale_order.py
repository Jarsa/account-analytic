# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Project",
        check_company=True,
        help="Applied to every line of this order, and carried over to"
        " the resulting invoice.",
    )
