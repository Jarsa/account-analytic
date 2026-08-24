# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAnalyticAutoAssignRule(models.Model):
    _name = "account.analytic.auto.assign.rule"
    _inherit = ["analytic.mixin"]
    _description = "Analytic Auto Assign Rule"
    _order = "sequence, id"
    _check_company_auto = True

    name = fields.Char(compute="_compute_name", store=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="cascade",
        help="Only applies to documents for this customer/vendor.",
    )
    partner_category_id = fields.Many2one(
        comodel_name="res.partner.category",
        ondelete="cascade",
        help="Applies to documents for contacts with this tag.",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        ondelete="cascade",
        check_company=True,
        help="Only applies to lines with this product.",
    )
    product_categ_id = fields.Many2one(
        comodel_name="product.category",
        ondelete="cascade",
        help="Applies to lines with products from this category.",
    )
    account_prefix = fields.Char(
        help="Applies to journal items whose account code starts with this prefix.",
    )

    @api.depends(
        "product_id",
        "product_categ_id",
        "partner_id",
        "partner_category_id",
        "account_prefix",
    )
    def _compute_name(self):
        for rule in self:
            parts = [
                rule.product_id.display_name,
                rule.product_categ_id.display_name,
                rule.partner_id.display_name,
                rule.partner_category_id.display_name,
                rule.account_prefix,
            ]
            rule.name = " / ".join(part for part in parts if part) or self.env._(
                "New Rule"
            )

    @api.model
    def _get_default_search_domain_vals(self):
        """Extension point: child modules (product category, brand,
        operating unit...) add their own search criteria here."""
        return {
            "company_id": False,
            "partner_id": False,
            "partner_category_id": [],
            "product_id": False,
            "product_categ_id": False,
        }

    def _create_domain(self, fname, value):
        if fname == "partner_category_id":
            return [(fname, "in", value + [False])]
        return [(fname, "in", [value, False])]

    @api.model
    def _get_applicable_rules(self, vals):
        default_vals = self._get_default_search_domain_vals()
        search_vals = default_vals | {
            key: value for key, value in vals.items() if key in default_vals
        }
        domain = []
        for fname, value in search_vals.items():
            domain += self._create_domain(fname, value)
        # All matching rules are needed here, there is no sensible limit to
        # apply for a rules-matching engine.
        rules = self.sudo().search(domain)  # pylint: disable=no-search-all
        prefix = vals.get("account_prefix") or ""
        return rules.filtered(
            lambda rule: not rule.account_prefix
            or prefix.startswith(rule.account_prefix)
        )

    @api.model
    def _sync_from_source(self, rule_id, match_vals, analytic_account_id):
        """Create or update the rule linked to a source record.

        Child modules that expose a single required analytic account field
        directly on a source record (product category, operating unit...)
        call this instead of letting users manage rules by hand. `rule_id`
        is whatever the caller has stored so far in its own invisible link
        field (False the first time). Returns the rule id to store back.
        """
        vals = {
            **match_vals,
            "analytic_distribution": {str(analytic_account_id): 100.0},
        }
        if rule_id:
            self.browse(rule_id).write(vals)
            return rule_id
        return self.create(vals).id

    @api.model
    def _get_distribution(self, vals):
        """Merge the distribution of every rule that applies.

        Unlike ``account.analytic.distribution.model``, a matching rule is
        never discarded as a whole just because it touches a plan that was
        already covered: by convention, each source (product category,
        brand, operating unit, project...) lives in its own analytic plan,
        so they are not expected to collide and everything gets merged. If
        two rules do end up touching the same plan due to a configuration
        mistake, the one with the lowest `sequence` wins, same as the
        native engine.
        """
        rules = self._get_applicable_rules(vals)
        result = {}
        applied_plans = (
            vals.get("related_root_plan_ids") or self.env["account.analytic.plan"]
        )
        for rule in rules:
            rule_plans = rule.distribution_analytic_account_ids.root_plan_id
            if rule_plans and (rule_plans & applied_plans):
                continue
            applied_plans |= rule_plans
            result.update(rule.analytic_distribution or {})
        return result
