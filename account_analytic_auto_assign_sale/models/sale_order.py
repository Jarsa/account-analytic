# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # The analytic account of the order is the native field of ``sale`` (also
    # filled by the Services & Materials flow): it is reused on purpose as the
    # project of the order. Only attributes that keep its meaning are added.
    analytic_account_id = fields.Many2one(check_company=True, index="btree_not_null")

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals["analytic_account_id"] = self.analytic_account_id.id
        return vals
