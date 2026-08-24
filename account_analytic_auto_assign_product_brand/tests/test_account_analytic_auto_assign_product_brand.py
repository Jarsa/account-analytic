# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, exceptions

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticAutoAssignProductBrand(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_obj = cls.env["account.analytic.auto.assign.rule"]

        cls.plan = cls.env["account.analytic.plan"].create({"name": "Brand Plan Test"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Brand Account Test", "plan_id": cls.plan.id}
        )
        cls.brand = cls.env["product.brand"].create(
            {"name": "Brand Test", "analytic_account_id": cls.analytic_account.id}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Brand Product Test", "product_brand_id": cls.brand.id}
        )

    def test_analytic_account_is_required(self):
        with self.assertRaises(exceptions.ValidationError):
            self.env["product.brand"].create({"name": "No Account Brand Test"})

    def test_creating_brand_syncs_a_rule(self):
        self.assertTrue(self.brand.auto_assign_rule_id)
        self.assertEqual(self.brand.auto_assign_rule_id.product_brand_id, self.brand)
        self.assertEqual(
            self.brand.auto_assign_rule_id.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )

    def test_match_by_product_brand(self):
        result = self.rule_obj._get_distribution(
            {
                "product_brand_id": self.brand.id,
                "company_id": self.env.company.id,
            }
        )
        self.assertEqual(result, {str(self.analytic_account.id): 100.0})

    def test_invoice_line_auto_assign(self):
        journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.env.company.id)],
            limit=1,
        )
        partner = self.env["res.partner"].create({"name": "Brand Invoice Partner Test"})
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "journal_id": journal.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 10.0,
                        }
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

    def test_sale_line_auto_assign(self):
        partner = self.env["res.partner"].create({"name": "Brand Sale Partner Test"})
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
        self.assertEqual(
            order.order_line.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )

    def test_purchase_line_auto_assign(self):
        partner = self.env["res.partner"].create(
            {"name": "Brand Purchase Partner Test"}
        )
        order = self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 1,
                            "price_unit": 10.0,
                            "name": self.product.name,
                            "date_planned": "2026-01-01",
                        }
                    )
                ],
            }
        )
        self.assertEqual(
            order.order_line.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )

    def test_expense_auto_assign(self):
        employee = self.env["hr.employee"].create({"name": "Brand Employee Test"})
        expense = self.env["hr.expense"].create(
            {
                "name": "Brand Expense Test",
                "employee_id": employee.id,
                "product_id": self.product.id,
                "total_amount_currency": 10.0,
            }
        )
        self.assertEqual(
            expense.analytic_distribution, {str(self.analytic_account.id): 100.0}
        )
