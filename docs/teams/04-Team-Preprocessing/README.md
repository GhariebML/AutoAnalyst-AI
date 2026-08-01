# Team 4: Preprocessing Engine - Specification README
- **Members**: Basma Mansour, Bothaina Elqady
- **Git Branch Namespace**: `feature/preprocessing-features`
- **Role**: Data Processing & Feature Engineers

### Module Responsibilities
- Clean duplicate rows using index-reset wrappers.
- Impute null cells with configurable parameters: mean, median, mode, or drop.
- Impute string and categorical nulls with modes or default labels.
- One-hot encode categorical features, dropping first value to avoid collinearity.
- Build date features (year, month, day-of-week) from datetimes.
