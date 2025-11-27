from odoo import models

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def fields_get(self, allfields=None, attributes=None):
        fields = super().fields_get(allfields, attributes)
        if not self._context.get("studio") and self.env['account.analytic.plan'].check_access_rights('read', raise_exception=False):
            project_plan, other_plans = self.env['account.analytic.plan']._get_all_plans()
            for plan in project_plan + other_plans:
                fname = plan._column_name()
                if fname in fields:
                    fields[fname]['string'] = plan.name
                    fields[fname]['domain'] = f"[('plan_id', 'child_of', {plan.id})]"
                    fields[fname]['readonly'] = True
        return fields