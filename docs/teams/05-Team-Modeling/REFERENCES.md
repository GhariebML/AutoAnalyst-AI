# References & Guidelines
### Common Pitfalls to Avoid
- Fitting models on dataset arrays that contain object data types or null values.
- Omitting class stratification when labels have skewed ratios, causing training bias.
- Calling train/test splits inside loops, leaking prediction data.

### Standards
- Follow logging guidelines instead of raw prints.
- Ensure type contracts remain strictly checked.
