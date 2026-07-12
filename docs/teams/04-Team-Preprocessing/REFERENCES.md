# References & Guidelines
### Common Pitfalls to Avoid
- Causing Target Leakage by performing categorical encoding or imputation on targets.
- Crashing when datetime strings cannot be parsed due to wrong date formats.
- One-hot encoding columns with extremely high cardinality, causing memory errors.

### Standards
- Follow logging guidelines instead of raw prints.
- Ensure type contracts remain strictly checked.
