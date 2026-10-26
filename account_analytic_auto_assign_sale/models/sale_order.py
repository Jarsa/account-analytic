# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Project",
        check_company=True,
        index="btree_not_null",
        help="Applied to every line of this order and to its invoices.",
    )

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals["analytic_account_id"] = self.analytic_account_id.id
        return vals
