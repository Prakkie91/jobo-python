<img src="https://raw.githubusercontent.com/Prakkie91/jobo-python/main/jobo-logo.png" alt="Jobo" width="120" />

# Jobo Enterprise — Python Client

**Access millions of job listings, geocode locations, and automate job applications — all from a single API.**

[![PyPI](https://img.shields.io/pypi/v/jobo-enterprise)](https://pypi.org/project/jobo-enterprise/)
[![Python](https://img.shields.io/pypi/pyversions/jobo-enterprise)](https://pypi.org/project/jobo-enterprise/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Features

| Sub-client          | Property             | Description                                              |
| ------------------- | -------------------- | -------------------------------------------------------- |
| **Jobs Feed**       | `client.feed`        | Bulk job feed with cursor-based pagination (45+ ATS)     |
| **Jobs Search**     | `client.search`      | Full-text search with location, remote, and source filters |
| **Locations**       | `client.locations`   | Geocode location strings into structured coordinates     |
| **Auto Apply**      | `client.auto_apply`  | Automate job applications with form field discovery      |

Both sync (`JoboClient`) and async (`AsyncJoboClient`) are included.

> **Get your API key** → [enterprise.jobo.world/api-keys](https://enterprise.jobo.world/api-keys)

---

## Installation

```bash
pip install jobo-enterprise
```

## Quick Start

```python
from jobo_enterprise import JoboClient

with JoboClient(api_key="your-api-key") as client:
    # Search for jobs
    results = client.search.search(q="software engineer", location="San Francisco")
    for job in results.jobs:
        print(f"{job.title} at {job.company.name}")

    # Geocode a location
    geo = client.locations.geocode("London, UK")
    print(f"{geo.locations[0].display_name}: {geo.locations[0].latitude}, {geo.locations[0].longitude}")
```

## Authentication

```python
client = JoboClient(api_key="your-api-key")
```

---

## Jobs Feed — `client.feed`

Bulk-sync millions of active jobs using cursor-based pagination.

### Fetch a batch

```python
from jobo_enterprise import LocationFilter

response = client.feed.get_jobs(
    locations=[
        LocationFilter(country="US", region="California"),
        LocationFilter(country="US", city="New York"),
    ],
    sources=["greenhouse", "workday"],
    is_remote=True,
    batch_size=1000,
)

print(f"Got {len(response.jobs)} jobs, has_more={response.has_more}")
```

### Auto-paginate all jobs

```python
for job in client.feed.iter_jobs(batch_size=1000, sources=["greenhouse"]):
    save_to_database(job)
```

### Expired job IDs

```python
from datetime import datetime, timedelta

expired_since = datetime.utcnow() - timedelta(days=1)

for job_id in client.feed.iter_expired_job_ids(expired_since=expired_since):
    mark_as_expired(job_id)
```

---

## Jobs Search — `client.search`

Full-text search with filters and page-based pagination.

### Simple search

```python
results = client.search.search(
    q="data scientist",
    location="New York",
    sources="greenhouse,lever",
    remote=True,
    page_size=50,
)

print(f"Found {results.total} jobs across {results.total_pages} pages")
```

### Advanced search (multiple queries & locations)

```python
results = client.search.search_advanced(
    queries=["machine learning engineer", "ML engineer", "AI engineer"],
    locations=["San Francisco", "New York", "Remote"],
    sources=["greenhouse", "lever", "ashby"],
    is_remote=True,
    page_size=100,
)
```

### Auto-paginate all results

```python
for job in client.search.iter_jobs(
    queries=["backend engineer"],
    locations=["London"],
    page_size=100,
):
    print(f"{job.title} — {job.company.name}")
```

---

## Locations — `client.locations`

Geocode location strings into structured data with coordinates.

```python
result = client.locations.geocode("San Francisco, CA")

for location in result.locations:
    print(f"{location.display_name}: {location.latitude}, {location.longitude}")
```

---

## Auto Apply — `client.auto_apply`

Automate job applications with form field discovery and filling.

```python
from jobo_enterprise import FieldAnswer

# Start a session
session = client.auto_apply.start_session(job.apply_url)

print(f"Provider: {session.provider_display_name}")
print(f"Fields: {len(session.fields)}")

# Fill in fields
answers = [
    FieldAnswer(field_id="first_name", value="John"),
    FieldAnswer(field_id="last_name", value="Doe"),
    FieldAnswer(field_id="email", value="john@example.com"),
]

result = client.auto_apply.set_answers(session.session_id, answers)

if result.is_terminal:
    print("Application submitted!")

# Clean up
client.auto_apply.end_session(session.session_id)
```

---

## Async Support

Every sub-client has an async equivalent via `AsyncJoboClient`:

```python
import asyncio
from jobo_enterprise import AsyncJoboClient

async def main():
    async with AsyncJoboClient(api_key="your-api-key") as client:
        # Search
        results = await client.search.search(q="frontend developer")

        # Auto-paginated feed
        async for job in client.feed.iter_jobs(batch_size=500):
            await process_job(job)

        # Geocode
        geo = await client.locations.geocode("Berlin, DE")

asyncio.run(main())
```

---

## Error Handling

```python
from jobo_enterprise import (
    JoboAuthenticationError,
    JoboRateLimitError,
    JoboValidationError,
    JoboServerError,
    JoboError,
)

try:
    results = client.search.search(q="engineer")
except JoboAuthenticationError:
    print("Invalid API key")
except JoboRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except JoboValidationError as e:
    print(f"Bad request: {e.detail}")
except JoboServerError:
    print("Server error — try again later")
```

## Supported ATS Sources (45+)

| Category           | Sources                                                                                                                                       |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Enterprise ATS** | `workday`, `smartrecruiters`, `icims`, `successfactors`, `oraclecloud`, `taleo`, `dayforce`, `csod`, `adp`, `ultipro`, `paycom`               |
| **Tech & Startup** | `greenhouse`, `lever_co`, `ashby`, `workable`, `workable_jobs`, `rippling`, `polymer`, `gem`, `pinpoint`, `homerun`                           |
| **Mid-Market**     | `bamboohr`, `breezy`, `jazzhr`, `recruitee`, `personio`, `jobvite`, `teamtailor`, `comeet`, `trakstar`, `zoho`                                |
| **SMB & Niche**    | `gohire`, `recooty`, `applicantpro`, `hiringthing`, `careerplug`, `hirehive`, `kula`, `careerpuck`, `talnet`, `jobscore`                      |
| **Specialized**    | `freshteam`, `isolved`, `joincom`, `eightfold`, `phenompeople`                                                                                |

## Configuration

| Parameter      | Default                       | Description                  |
| -------------- | ----------------------------- | ---------------------------- |
| `api_key`      | _required_                    | Your API key                 |
| `base_url`     | `https://jobs-api.jobo.world` | API base URL                 |
| `timeout`      | `30.0`                        | Request timeout (seconds)    |
| `httpx_client` | `None`                        | Custom httpx client          |

## Use Cases

- **Build a job board** — Search and display jobs from 45+ ATS platforms
- **Job aggregator** — Bulk-sync millions of listings with the feed endpoint
- **ATS data pipeline** — Pull jobs from Greenhouse, Lever, Workday, etc. into your data warehouse
- **Recruitment tools** — Power candidate-facing job search experiences
- **Auto-apply automation** — Automate job applications at scale
- **Location intelligence** — Geocode and normalize job locations

## Links

- **Website** — [jobo.world/enterprise](https://jobo.world/enterprise/)
- **Get API Key** — [enterprise.jobo.world/api-keys](https://enterprise.jobo.world/api-keys)
- **GitHub** — [github.com/Prakkie91/jobo-python](https://github.com/Prakkie91/jobo-python)
- **PyPI** — [pypi.org/project/jobo-enterprise](https://pypi.org/project/jobo-enterprise/)

## License

MIT — see [LICENSE](LICENSE).
