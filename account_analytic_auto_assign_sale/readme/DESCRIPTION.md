Uses the native **Analytic Account** of the sale order (the field of the
`sale` module, also filled by the *Services & Materials* flow when analytic
lines are linked to the order) as the project of the order and shows it on
the order header. Every order line gets it in its analytic distribution,
merged with what the native analytic distribution models already put there:
only the plan of that account is replaced, the other columns are kept.

The analytic account is passed to the invoices of the order, see
`account_analytic_auto_assign_account_move`.
