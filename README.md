# Jobo Enterprise Python Client

Official Python client library for the [Jobo Enterprise Jobs API](https://api.jobo.ai). Access millions of job listings from 15+ ATS platforms including Greenhouse, Lever, Workday, SmartRecruiters, and more.

[![PyPI](https://img.shields.io/pypi/v/jobo-enterprise)](https://pypi.org/project/jobo-enterprise/)
[![Python](https://img.shields.io/pypi/pyversions/jobo-enterprise)](https://pypi.org/project/jobo-enterprise/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Installation

```bash
pip install jobo-enterprise
```

## Quick Start

```python
from jobo_enterprise import JoboClient

client = JoboClient(api_key="your-api-key")

# Search for jobs
results = client.search_jobs(q="software engineer", location="San Francisco")
for job in results.jobs:
    print(f"{job.title} at {job.company.name}")
```

## Authentication

All API requests require an API key passed via the `X-Api-Key` header. The client handles this automatically:

```python
client = JoboClient(api_key="your-api-key")
```

You can also configure the base URL for self-hosted deployments:

```python
client = JoboClient(api_key="your-api-key", base_url="https://your-instance.example.com")
```

## Usage

### Job Search (Simple)

Search jobs with simple query parameters:

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

### Job Search (Advanced)

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

### Jobs Feed (Bulk)

Fetch large batches of active jobs using cursor-based pagination:

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
    process_job(job)
```

### Expired Job IDs

Sync expired jobs to keep your data fresh:

```python
from datetime import datetime, timedelta

expired_since = datetime.utcnow() - timedelta(days=1)

for job_id in client.iter_expired_job_ids(expired_since=expired_since):
    mark_as_expired(job_id)
```

## Async Support

Every method has an async equivalent:

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
    print("Invalid API key")
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

## Supported Sources

| Category | Sources |
|---|---|
| **Tech/Startup** | `greenhouse`, `lever`, `ashby`, `workable`, `rippling`, `polymer` |
| **Enterprise** | `workday`, `smartrecruiters` |
| **SMB** | `bamboohr`, `breezy`, `jazzhr`, `recruitee`, `personio` |

## Configuration

| Parameter | Default | Description |
|---|---|---|
| `api_key` | *required* | Your Jobo Enterprise API key |
| `base_url` | `https://api.jobo.ai` | API base URL |
| `timeout` | `30.0` | Request timeout in seconds |
| `httpx_client` | `None` | Custom `httpx.Client` / `httpx.AsyncClient` |

## Development

```bash
git clone https://github.com/jobo-ai/jobo-python.git
cd jobo-python
pip install -e ".[dev]"

# Run tests
pytest

# Lint & type check
ruff check .
mypy jobo_enterprise
```

## License

MIT — see [LICENSE](LICENSE).
