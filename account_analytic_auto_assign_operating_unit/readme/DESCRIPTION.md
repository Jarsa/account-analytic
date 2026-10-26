Adds the **Operating Unit** as a criterion of the native analytic
distribution models (Accounting > Configuration > Analytic Distribution
Models).

A model with an operating unit applies to invoice, bill and journal entry
lines and sale order lines of that operating unit (purchase order lines
with `account_analytic_auto_assign_purchase_operating_unit`). It
is merged with the other models that apply, following the native rules: one
model per analytic plan, the first one by sequence wins.
