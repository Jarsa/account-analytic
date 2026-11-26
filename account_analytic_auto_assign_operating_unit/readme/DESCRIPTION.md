Adds the **Operating Unit** as a criterion of the native analytic
distribution models (Accounting > Configuration > Analytic Distribution
Models).

A model with an operating unit applies to invoice, bill and journal entry
lines of that operating unit (sale order lines with
`account_analytic_auto_assign_sale_operating_unit`, purchase order lines
with `account_analytic_auto_assign_purchase_operating_unit`). It
is merged with the other models that apply, following the native rules: one
model per analytic plan, the first one by sequence wins.
