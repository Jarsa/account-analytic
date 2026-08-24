# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, fields, models


class ProductBrand(models.Model):
    _inherit = "product.brand"

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        required=True,
        help="Analytic account automatically applied to any document for"
        " products of this brand.",
    )
    auto_assign_rule_id = fields.Many2one(
        comodel_name="account.analytic.auto.assign.rule",
        readonly=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Checked before super().create() so the error is always this
        # readable ValidationError, whether or not the NOT NULL constraint
        # ends up applied at the DB level (see write() below for why that
        # cannot be relied on).
        for vals in vals_list:
            self._check_analytic_account_id(vals.get("analytic_account_id"))
        records = super().create(vals_list)
        for record in records:
            record._sync_auto_assign_rule()
        return records

    def write(self, vals):
        # `required=True` does not add a NOT NULL constraint when
        # pre-existing rows (e.g. brands created before this module was
        # installed) already have it empty, so the DB-level constraint
        # alone cannot be trusted to enforce this either way.
        if "analytic_account_id" in vals:
            self._check_analytic_account_id(vals["analytic_account_id"])
        res = super().write(vals)
        if "analytic_account_id" in vals:
            for record in self:
                record._sync_auto_assign_rule()
        return res

    @api.model
    def _check_analytic_account_id(self, analytic_account_id):
        if not analytic_account_id:
            raise exceptions.ValidationError(
                self.env._("The analytic account is required for every product brand.")
            )

    def _sync_auto_assign_rule(self):
        self.ensure_one()
        rule_id = self.env["account.analytic.auto.assign.rule"]._sync_from_source(
            self.auto_assign_rule_id.id,
            {"product_brand_id": self.id},
            self.analytic_account_id.id,
        )
        if rule_id != self.auto_assign_rule_id.id:
            self.auto_assign_rule_id = rule_id
