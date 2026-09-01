## Pharma Analytics Engineering Pipeline

An end-to-end analytics engineering project that transforms public pharmaceutical data into tested, analytics-ready datasets using **Snowflake, dbt, and SQL**.

The project demonstrates a layered data architecture, modular SQL transformations, automated data-quality testing, and the creation of a reusable dimensional model for downstream analytics.

---

## Architecture

```text
Public Pharmaceutical Data
            │
            ▼
      Snowflake RAW
            │
            ▼
       dbt Staging
            │
            ▼
        dbt Marts
            │
            ▼
   Analytics / Power BI
```

##The transformation layer follows a simple ELT approach:

-RAW preserves source data.
S-taging standardizes and prepares individual datasets.
-Marts combines validated staging models into analytics-ready structures.

## Tech Stack
```text
Snowflake — cloud data warehouse
dbt — transformation, testing, and dependency management
SQL — data modeling and transformation
Python — data ingestion and supporting automation
Power BI — downstream analytics and visualization
```

## dbt Project Structure
```text
dbt_pharma/
│
├── models/
│   ├── staging/
│   │   ├── stg_ndc_products.sql
│   │   ├── stg_ndc_packaging.sql
│   │   ├── stg_ndc_active_ingredients.sql
│   │   └── stg_ndc_routes.sql
│   │
│   └── marts/
│       └── dim_drug_package.sql
│
├── seeds/
├── macros/
├── dbt_project.yml
├── packages.yml
└── README.md
```

Generated dbt artifacts such as target/, logs/, and dbt_packages/
are excluded from version control.

## Staging Layer

The staging layer creates standardized representations of the source datasets.

Current staging models include:

Products
Packaging
Active ingredients
Administration routes

These models isolate source-specific transformations from downstream analytical logic.

## Analytics Mart
dim_drug_package

The dimensional model combines product-level information with package-level attributes to create a reusable analytical dataset.

It includes attributes such as:

Product identifiers
Brand and generic names
Labeler information
Dosage form
Product type
Marketing category
Package description
Sample indicator
Marketing start and end dates

This model is materialized as a table for downstream analytical consumption.

## Data Quality

Data quality is validated automatically during the dbt build.

Tests include:

not_null checks for required fields
relationships tests for referential integrity
Business-rule validation using dbt_utils

A build is considered successful only when both transformations and their associated tests complete successfully.

## Dependency Management

External dbt packages are declared in packages.yml.

Install dependencies with:

dbt deps

This project currently uses dbt-utils for reusable testing functionality.

## Running the Project

After configuring the Snowflake connection in your dbt profile:

dbt deps
dbt build

dbt build executes the project DAG, builds the models, and runs the associated data-quality tests.

## Lineage

dbt manages dependencies between staging models and downstream marts through ref().

Conceptually:
```text
stg_ndc_products ──────────────┐
                              │
stg_ndc_packaging ────────────┤
                              │
stg_ndc_active_ingredients ───┼──► dim_drug_package
                              │
stg_ndc_routes ───────────────┘
```

This makes transformation dependencies explicit and allows dbt to determine the correct execution order.

## Downstream Analytics

The curated dimensional model is designed to serve as the analytical layer for a Power BI dashboard.

The dashboard represents the final consumption layer of the pipeline rather than performing the core data transformation itself.

## Project Goal

This project was built as a practical demonstration of analytics engineering concepts:

ELT architecture
Cloud data warehousing
Layered data modeling
Modular SQL development
Data lineage
Automated data-quality testing
Reproducible builds
BI consumption

The emphasis is not only on producing a dataset, but on building a transformation workflow that is testable, modular, and reproducible.