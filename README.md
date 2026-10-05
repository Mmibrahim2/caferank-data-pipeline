# CafeRank Data Pipeline

CafeRank is a small data project that finds cafés in Minneapolis and shows which neighborhoods have the most.

The project automatically:

1. Gets café information from a CSV file or public website.
2. Cleans the information and removes unusable rows.
3. Keeps active coffee shops and cafés.
4. Counts the cafés in each neighborhood.
5. Saves the results in Amazon S3 and PostgreSQL.
6. Runs checks to make sure the information looks correct.

## Why I built it

Public data is often messy. It may contain missing values, duplicate businesses, closed locations, or unexpected changes.

I built CafeRank to practice turning messy public data into useful and trustworthy results. It also shows how a data project can run automatically every day.

## How it works

```text
Minneapolis café data
          ↓
   Python + Pandas
   clean and check it
          ↓
  Rank neighborhoods
          ↓
 Amazon S3 + PostgreSQL
```

- **Python and Pandas** clean and organize the café information.
- **Amazon S3** keeps copies of the original and cleaned files.
- **PostgreSQL** stores the results so they can be searched with SQL.
- **Terraform** sets up the AWS resources.
- **GitHub Actions** tests the project and can run it every day.
- **pytest** checks that the code and data rules work correctly.

## Example result

Using the sample data included in this repository:

| Rank | Neighborhood | Cafés |
|---:|---|---:|
| 1 | North Loop | 2 |
| 2 | Lyndale | 1 |
| 2 | Nicollet Island - East Bank | 1 |
| 2 | Uptown | 1 |

Neighborhoods with the same number of cafés receive the same rank.

## Try it on your computer

You need Python 3.10 or newer.

```bash
git clone https://github.com/Mmibrahim2/caferank-data-pipeline.git
cd caferank-data-pipeline

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

SOURCE_FILE=data/sample_cafes.csv caferank run
```

The results will appear in `data/output/`.

Run the tests with:

```bash
pytest
```

## Project folders

```text
src/caferank/       Python pipeline code
tests/              Automated tests
data/               Sample café data
terraform/          AWS setup files
.github/workflows/  Automatic tests and daily schedule
```

## Using PostgreSQL

Docker can start a local PostgreSQL database for you:

```bash
docker compose up -d postgres
export DATABASE_URL='postgresql+psycopg://caferank:caferank@localhost:5432/caferank'
SOURCE_FILE=data/sample_cafes.csv caferank run
```

Running the pipeline again updates existing café records instead of creating duplicates.

## Using real data and AWS

The repository uses a small sample file so anyone can run it without accounts or secret keys.

For a live version, you can provide:

- `SOURCE_URL` for a current Minneapolis data export
- `S3_BUCKET` for the AWS storage bucket
- `DATABASE_URL` for PostgreSQL
- `AWS_REGION` for the AWS region

The Minneapolis open-data website is changing, so the source address is kept as a setting instead of being permanently written into the code.

## Data checks

The pipeline stops before saving bad results when:

- Important columns are missing.
- A café ID appears more than once.
- Important values are empty.
- Map coordinates are far outside Minneapolis.
- The neighborhood totals do not match the café total.

## Important note

CafeRank ranks neighborhoods by the number of active cafés in the source data. It does not measure coffee quality or customer opinion.

For a detailed explanation of the design and common interview questions, see [INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md).
