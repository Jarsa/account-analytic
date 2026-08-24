# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticAutoAssignRule(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_obj = cls.env["account.analytic.auto.assign.rule"]
        cls.plan_obj = cls.env["account.analytic.plan"]
        cls.account_obj = cls.env["account.analytic.account"]
        cls.distribution_model_obj = cls.env["account.analytic.distribution.model"]

        cls.plan_line = cls.plan_obj.create({"name": "Product Line Test"})
        cls.plan_brand = cls.plan_obj.create({"name": "Brand Test"})

        cls.analytic_line = cls.account_obj.create(
            {"name": "Telemetry Line Test", "plan_id": cls.plan_line.id}
        )
        cls.analytic_line_other = cls.account_obj.create(
            {"name": "Other Line Test", "plan_id": cls.plan_line.id}
        )
        cls.analytic_brand = cls.account_obj.create(
            {"name": "ACME Brand Test", "plan_id": cls.plan_brand.id}
        )

        cls.product_categ = cls.env["product.category"].create(
            {"name": "Category Test"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Product Test", "categ_id": cls.product_categ.id}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Customer Test"})

    def test_sync_from_source_creates_then_updates(self):
        count_before = self.rule_obj.search_count([])
        rule_id = self.rule_obj._sync_from_source(
            False,
            {"product_categ_id": self.product_categ.id},
            self.analytic_line.id,
        )
        rule = self.rule_obj.browse(rule_id)
        self.assertEqual(
            rule.analytic_distribution, {str(self.analytic_line.id): 100.0}
        )
        self.assertEqual(self.rule_obj.search_count([]), count_before + 1)

        updated_id = self.rule_obj._sync_from_source(
            rule_id,
            {"product_categ_id": self.product_categ.id},
            self.analytic_line_other.id,
        )
        self.assertEqual(updated_id, rule_id)
        self.assertEqual(self.rule_obj.search_count([]), count_before + 1)
        self.assertEqual(
            rule.analytic_distribution, {str(self.analytic_line_other.id): 100.0}
        )

    def test_no_match_returns_empty(self):
        result = self.rule_obj._get_distribution(
            {"product_id": self.product.id, "company_id": self.env.company.id}
        )
        self.assertFalse(result)

    def test_match_by_product_category(self):
        self.rule_obj.create(
            {
                "product_categ_id": self.product_categ.id,
                "analytic_distribution": {str(self.analytic_line.id): 100.0},
            }
        )
        result = self.rule_obj._get_distribution(
            {
                "product_id": self.product.id,
                "product_categ_id": self.product_categ.id,
                "company_id": self.env.company.id,
            }
        )
        self.assertEqual(result, {str(self.analytic_line.id): 100.0})

    def test_merge_different_plans(self):
        self.rule_obj.create(
            {
                "product_categ_id": self.product_categ.id,
                "analytic_distribution": {str(self.analytic_line.id): 100.0},
            }
        )
        self.rule_obj.create(
            {
                "partner_id": self.partner.id,
                "analytic_distribution": {str(self.analytic_brand.id): 100.0},
            }
        )
        result = self.rule_obj._get_distribution(
            {
                "product_id": self.product.id,
                "product_categ_id": self.product_categ.id,
                "partner_id": self.partner.id,
                "company_id": self.env.company.id,
            }
        )
        self.assertEqual(
            result,
            {
                str(self.analytic_line.id): 100.0,
                str(self.analytic_brand.id): 100.0,
            },
        )

    def test_same_plan_conflict_lowest_sequence_wins(self):
        self.rule_obj.create(
            {
                "sequence": 10,
                "product_categ_id": self.product_categ.id,
                "analytic_distribution": {str(self.analytic_line.id): 100.0},
            }
        )
        self.rule_obj.create(
            {
                "sequence": 20,
                "partner_id": self.partner.id,
                "analytic_distribution": {str(self.analytic_line_other.id): 100.0},
            }
        )
        result = self.rule_obj._get_distribution(
            {
                "product_id": self.product.id,
                "product_categ_id": self.product_categ.id,
                "partner_id": self.partner.id,
                "company_id": self.env.company.id,
            }
        )
        self.assertEqual(result, {str(self.analytic_line.id): 100.0})

    def test_account_prefix_match(self):
        self.rule_obj.create(
            {
                "account_prefix": "60",
                "analytic_distribution": {str(self.analytic_brand.id): 100.0},
            }
        )
        matched = self.rule_obj._get_distribution(
            {"account_prefix": "601.01", "company_id": self.env.company.id}
        )
        not_matched = self.rule_obj._get_distribution(
            {"account_prefix": "115.01", "company_id": self.env.company.id}
        )
        self.assertEqual(matched, {str(self.analytic_brand.id): 100.0})
        self.assertFalse(not_matched)

    def test_native_distribution_model_takes_priority(self):
        self.rule_obj.create(
            {
                "product_categ_id": self.product_categ.id,
                "analytic_distribution": {str(self.analytic_line.id): 100.0},
            }
        )
        self.distribution_model_obj.create(
            {
                "partner_id": self.partner.id,
                "analytic_distribution": {str(self.analytic_brand.id): 100.0},
            }
        )
        result = self.distribution_model_obj._get_distribution(
            {
                "product_id": self.product.id,
                "product_categ_id": self.product_categ.id,
                "partner_id": self.partner.id,
                "company_id": self.env.company.id,
            }
        )
        # Since a native rule exists, Odoo's engine is used (which here
        # only matches by partner_id) and our own engine is ignored.
        self.assertEqual(result, {str(self.analytic_brand.id): 100.0})
