# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Project",
        check_company=True,
        index="btree_not_null",
        help="Applied to every product line of this journal entry. Credit"
        " notes and duplicates keep it.",
    )
