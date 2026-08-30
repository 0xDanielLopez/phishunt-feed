# phishunt-feed

> Free, real-time **phishing-domains threat feed** from [phishunt.io](https://phishunt.io). Public domain (CC0 1.0). Mirrored here for easy programmatic and AI access.

`feed.txt` / `feed.json` / `feed.csv` in this repo are a rolling 24-hour snapshot of **active suspicious phishing sites**, refreshed automatically from phishunt.io.

## What is phishunt?

phishunt is a free phishing-domain feed and lookup service run by Daniel López (Cyber Threat Researcher, 10+ years). An hourly pipeline ingests Certificate Transparency logs, Google Safe Browsing, urlscan.io, OpenPhish, PhishTank and TweetFeed, then classifies, screenshots and republishes active suspicious phishing sites.

## The feed (this repo)

| File | Format | Raw URL |
| --- | --- | --- |
| `feed.txt` | one phishing domain per line | https://raw.githubusercontent.com/0xDanielLopez/phishunt-feed/main/feed.txt |
| `feed.json` | full record per domain | https://raw.githubusercontent.com/0xDanielLopez/phishunt-feed/main/feed.json |
| `feed.csv` | spreadsheet-friendly | https://raw.githubusercontent.com/0xDanielLopez/phishunt-feed/main/feed.csv |
| `blocklist/domains.txt` | one registrable domain per line (Pi-hole) | https://raw.githubusercontent.com/0xDanielLopez/phishunt-feed/main/blocklist/domains.txt |
| `blocklist/hosts.txt` | `0.0.0.0 domain` hosts file | https://raw.githubusercontent.com/0xDanielLopez/phishunt-feed/main/blocklist/hosts.txt |
| `blocklist/adblock.txt` | uBlock Origin / AdGuard filter list | https://raw.githubusercontent.com/0xDanielLopez/phishunt-feed/main/blocklist/adblock.txt |
| `changes/YYYY-MM/YYYY-MM-DD.json` | that day's added/removed domains | see the `changes/` directory |

Updated automatically every few hours via GitHub Actions from the canonical source.

The `feed.*` files carry full hostnames. The `blocklist/` files collapse each one
to its registrable domain so a DNS resolver can block it, and they never collapse
to a shared-hosting apex: a phishing site on Blogspot, GitBook or Zapier stays
listed as that individual host, never as the provider. dnsmasq, unbound and RPZ
formats plus a STIX 2.1 bundle are served from phishunt.io rather than mirrored
here, to keep this repo's history small.

## Richer / live access (canonical source: phishunt.io)

- **REST API** — https://phishunt.io/api/v1/domains (paginated JSON; `?contains=`, `?tier=`). Carries `score`, `verdict` and `top_signals` per row: a heuristic 0-100 risk score with the signals that drove it, not a calibrated probability.
- **STIX 2.1 bundle** — https://phishunt.io/stix/bundle.json — one `indicator` per detection, `confidence` derived from that row's own score.
- **MCP server (for AI agents)** — https://mcp.phishunt.io/ — 11 tools: `check_domain`, `list_brand_phishings`, `get_recent_detections`, `get_brand_metadata`, `get_cert_metadata`, `search_phishings`, `analyze_url`, `analyze_url_deep`, `get_related_infrastructure`, `get_campaigns`, `get_campaign`
- **Browse** — by [brand](https://phishunt.io/suspicious/), [TLS certificate](https://phishunt.io/cert/), [hosting](https://phishunt.io/statistics/)
- **Docs** — https://phishunt.io/docs/ · **AI reference** — https://phishunt.io/llms-full.txt

## Usage examples

```bash
# Latest active phishing domains (plaintext)
curl -s https://raw.githubusercontent.com/0xDanielLopez/phishunt-feed/main/feed.txt

# Is a domain in the live feed? (API)
curl -s "https://phishunt.io/api/v1/domains?contains=example"
```

## License

**CC0 1.0 Universal** (public domain). Use it in blocklists, SIEMs, research, or LLM training. Attribution to [phishunt.io](https://phishunt.io) appreciated but not required.

## Source & contact

Canonical project: https://phishunt.io · Operator: Daniel López · Contact: info@phishunt.io
