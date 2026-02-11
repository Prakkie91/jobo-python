<img src="https://raw.githubusercontent.com/Prakkie91/jobo-python/main/jobo-logo.png" alt="Jobo" width="120" />

# Jobo Enterprise — Python Client

**Access millions of job listings from 45+ ATS platforms with a single API.**  
Build job boards, power job aggregators, or sync ATS data — Greenhouse, Lever, Workday, iCIMS, and more.

[![PyPI](https://img.shields.io/pypi/v/jobo-enterprise)](https://pypi.org/project/jobo-enterprise/)
[![Python](https://img.shields.io/pypi/pyversions/jobo-enterprise)](https://pypi.org/project/jobo-enterprise/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Why Jobo Enterprise?

- **45+ ATS integrations** — Greenhouse, Lever, Workday, iCIMS, SmartRecruiters, BambooHR, Ashby, and many more
- **Bulk feed endpoint** — Cursor-based pagination to sync millions of jobs efficiently
- **Real-time search** — Full-text search with location, remote, and source filters
- **Expired job sync** — Keep your job board fresh by removing stale listings
- **Sync + Async** — Both `JoboClient` and `AsyncJoboClient` included
- **Fully typed** — Pydantic models with complete type annotations

> **Get your API key** → [enterprise.jobo.world/api-keys](https://enterprise.jobo.world/api-keys)
>
> **Learn more** → [jobo.world/enterprise](https://jobo.world/enterprise/)

---

## Installation

```bash
pip install jobo-enterprise
```

## Quick Start

```python
from jobo_enterprise import JoboClient

client = JoboClient(api_key="your-api-key")

# Search for software engineering jobs from Greenhouse
results = client.search_jobs(
    q="software engineer",
    location="San Francisco",
    sources="greenhouse,lever",
)

for job in results.jobs:
    print(f"{job.title} at {job.company.name} — {job.listing_url}")
```

## Authentication

Get your API key at **[enterprise.jobo.world/api-keys](https://enterprise.jobo.world/api-keys)**.

All requests require an API key passed via the `X-Api-Key` header. The client handles this automatically:

```python
client = JoboClient(api_key="your-api-key")
```

## Usage

### Search Jobs (Simple)

Search jobs with query parameters — ideal for building job board search pages:

```python
from jobo_enterprise import JoboClient

with JoboClient(api_key="your-api-key") as client:
    results = client.search_jobs(
        q="data scientist",
        location="New York",
        sources="greenhouse,lever",
        remote=True,
        page=1,
        page_size=50,
    )

    print(f"Found {results.total} jobs across {results.total_pages} pages")
    for job in results.jobs:
        print(f"  {job.title} at {job.company.name} — {job.listing_url}")
```

### Search Jobs (Advanced)

Use the advanced endpoint for multiple queries and locations:

```python
results = client.search_jobs_advanced(
    queries=["machine learning engineer", "ML engineer", "AI engineer"],
    locations=["San Francisco", "New York", "Remote"],
    sources=["greenhouse", "lever", "ashby"],
    is_remote=True,
    page_size=100,
)
```

### Auto-Paginated Search

Iterate over all matching jobs without managing pagination:

```python
for job in client.iter_search_jobs(
    queries=["backend engineer"],
    locations=["London"],
    page_size=100,
):
    print(f"{job.title} — {job.company.name}")
```

### Bulk Jobs Feed

Fetch large batches of active jobs using cursor-based pagination — perfect for building a job aggregator or syncing to your database:

```python
from jobo_enterprise import JoboClient, LocationFilter

with JoboClient(api_key="your-api-key") as client:
    response = client.get_jobs_feed(
        locations=[
            LocationFilter(country="US", region="California"),
            LocationFilter(country="US", city="New York"),
        ],
        sources=["greenhouse", "workday"],
        is_remote=True,
        batch_size=1000,
    )

    print(f"Got {len(response.jobs)} jobs, has_more={response.has_more}")

    # Continue with cursor
    if response.has_more:
        next_response = client.get_jobs_feed(
            cursor=response.next_cursor,
            batch_size=1000,
        )
```

### Auto-Paginated Feed

Stream all jobs without managing cursors:

```python
for job in client.iter_jobs_feed(batch_size=1000, sources=["greenhouse"]):
    save_to_database(job)
```

### Expired Job IDs

Keep your job board fresh by syncing expired listings:

```python
from datetime import datetime, timedelta

expired_since = datetime.utcnow() - timedelta(days=1)

for job_id in client.iter_expired_job_ids(expired_since=expired_since):
    mark_as_expired(job_id)
```

## Async Support

Every method has an async equivalent via `AsyncJoboClient`:

```python
import asyncio
from jobo_enterprise import AsyncJoboClient

async def main():
    async with AsyncJoboClient(api_key="your-api-key") as client:
        # Search
        results = await client.search_jobs(q="frontend developer")

        # Auto-paginated feed
        async for job in client.iter_jobs_feed(batch_size=500):
            await process_job(job)

        # Expired IDs
        async for job_id in client.iter_expired_job_ids(
            expired_since=datetime.utcnow() - timedelta(days=1)
        ):
            await mark_expired(job_id)

asyncio.run(main())
```

## Error Handling

The client raises typed exceptions for different error scenarios:

```python
from jobo_enterprise import (
    JoboClient,
    JoboAuthenticationError,
    JoboRateLimitError,
    JoboValidationError,
    JoboServerError,
    JoboError,
)

try:
    results = client.search_jobs(q="engineer")
except JoboAuthenticationError:
    print("Invalid API key — get one at https://enterprise.jobo.world/api-keys")
except JoboRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except JoboValidationError as e:
    print(f"Bad request: {e.detail}")
except JoboServerError:
    print("Server error — try again later")
except JoboError as e:
    print(f"Unexpected error: {e}")
```

## Models

All response data is returned as typed Pydantic models:

| Model | Description |
|---|---|
| `Job` | A job listing with title, company, locations, compensation, etc. |
| `JobCompany` | Company ID and name |
| `JobLocation` | City, state, country, coordinates |
| `JobCompensation` | Min/max salary, currency, period |
| `LocationFilter` | Structured filter for feed endpoint |
| `JobFeedResponse` | Feed response with cursor pagination |
| `ExpiredJobIdsResponse` | Expired job IDs with cursor pagination |
| `JobSearchResponse` | Search response with page-based pagination |

## Supported ATS Sources (45+)

Filter jobs by any of these applicant tracking systems:

| Category | Sources |
|---|---|
| **Enterprise ATS** | `workday`, `smartrecruiters`, `icims`, `successfactors`, `oraclecloud`, `taleo`, `dayforce`, `csod` (Cornerstone), `adp`, `ultipro`, `paycom` |
| **Tech & Startup** | `greenhouse`, `lever_co`, `ashby`, `workable`, `workable_jobs`, `rippling`, `polymer`, `gem`, `pinpoint`, `homerun` |
| **Mid-Market** | `bamboohr`, `breezy`, `jazzhr`, `recruitee`, `personio`, `jobvite`, `teamtailor`, `comeet`, `trakstar`, `zoho` |
| **SMB & Niche** | `gohire`, `recooty`, `applicantpro`, `hiringthing`, `careerplug`, `hirehive`, `kula`, `careerpuck`, `talnet`, `jobscore` |
| **Specialized** | `freshteam`, `isolved`, `joincom`, `eightfold`, `phenompeople` (via `eightfold`) |

> Pass source identifiers in the `sources` parameter, e.g. `sources=["greenhouse", "lever_co", "workday"]`

## Configuration

| Parameter | Default | Description |
|---|---|---|
| `api_key` | *required* | Your Jobo Enterprise API key ([get one here](https://enterprise.jobo.world/api-keys)) |
| `base_url` | `https://jobs-api.jobo.world` | API base URL |
| `timeout` | `30.0` | Request timeout in seconds |
| `httpx_client` | `None` | Custom `httpx.Client` / `httpx.AsyncClient` |

## Use Cases

- **Build a job board** — Search and display jobs from 45+ ATS platforms
- **Job aggregator** — Bulk-sync millions of listings with the feed endpoint
- **ATS data pipeline** — Pull jobs from Greenhouse, Lever, Workday, etc. into your data warehouse
- **Recruitment tools** — Power candidate-facing job search experiences
- **Market research** — Analyze hiring trends across companies and industries

## Development

```bash
git clone https://github.com/Prakkie91/jobo-python.git
cd jobo-python
pip install -e ".[dev]"

# Run tests
pytest

# Lint & type check
ruff check .
mypy jobo_enterprise
```

## Publishing to PyPI

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI
twine upload dist/*

# Push tags to GitHub
git tag v$(python -c "from jobo_enterprise import __version__; print(__version__)")
git push origin main --tags
```

## Pushing to GitHub

```bash
# Initial setup (one-time)
git remote set-url origin https://github.com/Prakkie91/jobo-python.git

# Push
git add -A
git commit -m "release: v$(python -c 'from jobo_enterprise import __version__; print(__version__)')"
git push origin main
```

## Links

- **Website** — [jobo.world/enterprise](https://jobo.world/enterprise/)
- **Get API Key** — [enterprise.jobo.world/api-keys](https://enterprise.jobo.world/api-keys)
- **GitHub** — [github.com/Prakkie91/jobo-python](https://github.com/Prakkie91/jobo-python)
- **PyPI** — [pypi.org/project/jobo-enterprise](https://pypi.org/project/jobo-enterprise/)

## License

MIT — see [LICENSE](LICENSE).
