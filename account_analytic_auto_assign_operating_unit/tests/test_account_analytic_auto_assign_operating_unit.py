# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, exceptions

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticAutoAssignOperatingUnit(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_obj = cls.env["account.analytic.auto.assign.rule"]

        cls.plan = cls.env["account.analytic.plan"].create(
            {"name": "Operating Unit Plan Test"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "OU Account Test", "plan_id": cls.plan.id}
        )
        cls.operating_unit = cls.env["operating.unit"].create(
            {
                "name": "OU Test",
                "code": "OUTEST",
                "company_id": cls.env.company.id,
                "partner_id": cls.env.company.partner_id.id,
                "analytic_account_id": cls.analytic_account.id,
            }
        )
        cls.other_analytic_account = cls.env["account.analytic.account"].create(
            {"name": "OU Other Account Test", "plan_id": cls.plan.id}
        )
        cls.other_operating_unit = cls.env["operating.unit"].create(
            {
                "name": "OU Other Test",
                "code": "OUOTHER",
                "company_id": cls.env.company.id,
                "partner_id": cls.env.company.partner_id.id,
                "analytic_account_id": cls.other_analytic_account.id,
            }
        )

    def test_analytic_account_is_required(self):
        with self.assertRaises(exceptions.ValidationError):
            self.env["operating.unit"].create(
                {
                    "name": "OU No Account Test",
                    "code": "OUNOACC",
                    "company_id": self.env.company.id,
                    "partner_id": self.env.company.partner_id.id,
                }
            )

    def test_creating_operating_unit_syncs_a_rule(self):
        self.assertTrue(self.operating_unit.auto_assign_rule_id)
        self.assertEqual(
            self.operating_unit.auto_assign_rule_id.operating_unit_id,
            self.operating_unit,
        )
        self.assertEqual(
            self.operating_unit.auto_assign_rule_id.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )

    def test_changing_analytic_account_updates_the_same_rule(self):
        rule = self.operating_unit.auto_assign_rule_id
        self.operating_unit.analytic_account_id = self.other_analytic_account
        self.assertEqual(self.operating_unit.auto_assign_rule_id, rule)
        self.assertEqual(
            rule.analytic_distribution,
            {str(self.other_analytic_account.id): 100.0},
        )

    def test_match_by_operating_unit(self):
        result = self.rule_obj._get_distribution(
            {
                "operating_unit_id": self.operating_unit.id,
                "company_id": self.env.company.id,
            }
        )
        self.assertEqual(result, {str(self.analytic_account.id): 100.0})

    def test_different_operating_units_do_not_mix_accounts(self):
        result = self.rule_obj._get_distribution(
            {
                "operating_unit_id": self.other_operating_unit.id,
                "company_id": self.env.company.id,
            }
        )
        self.assertEqual(result, {str(self.other_analytic_account.id): 100.0})

    def test_invoice_line_auto_assign(self):
        journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.env.company.id)],
            limit=1,
        )
        partner = self.env["res.partner"].create({"name": "OU Invoice Partner Test"})
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "journal_id": journal.id,
                "operating_unit_id": self.operating_unit.id,
                "invoice_line_ids": [
                    Command.create({"name": "Line", "quantity": 1, "price_unit": 10.0})
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
        partner = self.env["res.partner"].create({"name": "OU Sale Partner Test"})
        product = self.env["product.product"].create({"name": "OU Product Test"})
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "operating_unit_id": self.operating_unit.id,
                "order_line": [
                    Command.create({"product_id": product.id, "product_uom_qty": 1})
                ],
            }
        )
        self.assertEqual(
            order.order_line.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )
