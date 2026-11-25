Glue module between the `account_analytic_auto_assign_*` modules and
`account_analytic_distribution_model_recalculate`, installed automatically
with both:

- the project of the journal entry header is applied after the
  distribution computed by `account_analytic_distribution_model_recalculate`;
- the criteria added to the analytic distribution models (operating unit,
  product brand...) are taken into account when checking that two models
  do not overlap.
