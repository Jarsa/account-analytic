# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, exceptions

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticAutoAssignProductCategory(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_obj = cls.env["account.analytic.auto.assign.rule"]

        cls.plan = cls.env["account.analytic.plan"].create(
            {"name": "Product Category Plan Test"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Categ Account Test", "plan_id": cls.plan.id}
        )
        cls.product_categ = cls.env["product.category"].create(
            {"name": "Categ Test", "analytic_account_id": cls.analytic_account.id}
        )
        cls.other_analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Other Categ Account Test", "plan_id": cls.plan.id}
        )
        cls.other_product_categ = cls.env["product.category"].create(
            {
                "name": "Other Categ Test",
                "analytic_account_id": cls.other_analytic_account.id,
            }
        )

    def test_analytic_account_is_required(self):
        with self.assertRaises(exceptions.ValidationError):
            self.env["product.category"].create({"name": "No Account Categ Test"})

    def test_creating_category_syncs_a_rule(self):
        self.assertTrue(self.product_categ.auto_assign_rule_id)
        self.assertEqual(
            self.product_categ.auto_assign_rule_id.product_categ_id,
            self.product_categ,
        )
        self.assertEqual(
            self.product_categ.auto_assign_rule_id.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )

    def test_changing_analytic_account_updates_the_same_rule(self):
        rule = self.product_categ.auto_assign_rule_id
        self.product_categ.analytic_account_id = self.other_analytic_account
        self.assertEqual(self.product_categ.auto_assign_rule_id, rule)
        self.assertEqual(
            rule.analytic_distribution,
            {str(self.other_analytic_account.id): 100.0},
        )

    def test_different_categories_do_not_mix_accounts(self):
        result = self.rule_obj._get_distribution(
            {
                "product_categ_id": self.other_product_categ.id,
                "company_id": self.env.company.id,
            }
        )
        self.assertEqual(result, {str(self.other_analytic_account.id): 100.0})

    def test_invoice_line_auto_assign(self):
        product = self.env["product.product"].create(
            {"name": "Categ Product Test", "categ_id": self.product_categ.id}
        )
        journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.env.company.id)],
            limit=1,
        )
        partner = self.env["res.partner"].create({"name": "Categ Invoice Partner Test"})
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "journal_id": journal.id,
                "invoice_line_ids": [
                    Command.create(
                        {"product_id": product.id, "quantity": 1, "price_unit": 10.0}
                    )
                ],
            }
        )
        line = move.invoice_line_ids.filtered(
            lambda line: line.display_type == "product"
        )
        self.assertEqual(
            line.analytic_distribution, {str(self.analytic_account.id): 100.0}
        )
