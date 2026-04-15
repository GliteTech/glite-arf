---
name: "download_paper"
description: "Resolve paper identifiers, fetch the PDF and metadata, and prepare inputs for paper asset creation. Use when you need to download a research paper from partial identifiers."
model: "claude-sonnet-4-6"
---
# Download Research Paper

**Version**: 1

## Goal

Given partial paper identifiers (any combination of title, DOI, authors, year, arXiv ID, PMID),
retrieve the full-text content of the paper in the best available format.

## Inputs

* `{{ title }}` — paper title (optional if DOI or other ID provided)
* `{{ doi }}` — Digital Object Identifier (optional)
* `{{ authors }}` — author names, comma-separated (optional)
* `{{ year }}` — publication year (optional)
* `{{ arxiv_id }}` — arXiv identifier (optional)
* `{{ pmid }}` — PubMed identifier (optional)
* `{{ output_dir }}` — directory to save the downloaded file

At least one of `title`, `doi`, or `arxiv_id` must be provided. More identifiers improve resolution
accuracy.

## Context

Read before starting:

* This skill file (you are reading it now)
* `arf/styleguide/python_styleguide.md` — if writing helper scripts

If any temporary helper scripts are created during execution, delete them before completing the
skill. Do not leave throwaway code in the repository.

## Philosophy

This skill is not a simple downloader. It is a **version-aware scholarly resolver**. The agent
identifies the work precisely, collects every known identifier, then searches for the best
accessible version across all available channels. When the published version is unavailable,
preprints, accepted manuscripts, working papers, and structured XML are all valid and valuable
alternatives.

Prefer machine-readable formats over PDF when available. For an AI agent, structured XML/TEI/JATS or
plain text is more useful than a PDF that requires extraction.

Format preference ranking:

1. Structured XML (JATS, TEI, BioC) or plain text
2. Born-digital PDF
3. Scanned PDF (last resort)

Version preference ranking:

1. Published version (Version of Record)
2. Open publisher copy (hybrid/bronze OA)
3. Repository copy (green OA)
4. Accepted manuscript (post-peer-review, pre-formatting)
5. Submitted manuscript / preprint
6. Working paper / technical report / dissertation chapter
7. Abstract + metadata only (if nothing else available)

* * *

## Steps

### Phase 1: Canonical Identification

Build a complete metadata record before attempting any download. The more identifiers collected, the
higher the success rate in later phases.

1. If DOI is provided, query CrossRef API (`https://api.crossref.org/works/{doi}`) to get full
   metadata: title, authors, year, ISSN, publisher, DOI prefix, and any `relation` fields linking to
   preprints.
2. If DOI is missing, resolve it:
   * Query CrossRef `query.bibliographic` endpoint with title + author + year filter:
     `https://api.crossref.org/works?query.bibliographic={title}+{author}&filter=from-pub-date: {year}-01-01,until-pub-date:{year}-12-31&rows=3`.
     Take the top match. Verify by fuzzy-matching the returned title against the input title
     (similarity > 0.85).
   * In parallel, query Semantic Scholar (`/graph/v1/paper/search?query={title}`) — returns
     `paperId`, DOI, arXiv ID, PMID.
   * In parallel, query OpenAlex
     (`https://api.openalex.org/works?search={title}&filter= publication_year:{year}`) for
     additional ID coverage.
3. From all responses, build a **canonical record** with normalized fields:
   * `title` (normalized: lowercase, stripped punctuation for matching)
   * `doi` and `doi_prefix` (e.g., `10.1371` for PLOS, `10.1016` for Elsevier)
   * `pmid` / `pmcid`
   * `arxiv_id`
   * `openalex_id`
   * `semantic_scholar_id`
   * `authors` (list of names)
   * `year`
   * `venue` (journal or conference name)
   * `publisher` (from CrossRef `member` field — more reliable than DOI prefix for routing)
   * `preprint_doi` (if CrossRef `has-preprint` relation exists)
4. If PMID is known but PMCID is not, use the NCBI ID Converter API
   (`https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={id}&format=json`) to check for a PMC
   version. Batch up to 200 IDs per request.
5. **Validate the DOI is globally resolvable.** Some publishers issue internal pseudo-DOIs that do
   not resolve via doi.org. The most common case: ACM uses the `10.5555` prefix for cross-listed
   materials from other publishers (e.g., IEEE). If the DOI prefix is `10.5555`, do not use it for
   downstream retrieval — instead, search by title to find the real publisher DOI (e.g., an IEEE DOI
   starting with `10.1109`).

**Batch optimization**: When resolving multiple papers, use Semantic Scholar `POST /paper/batch` (up
to 500 IDs per request) and OpenAlex pipe-separated DOI filter
(`GET /works?filter=doi:{doi1}|{doi2}|{doi3}&per_page=100`, up to 50 DOIs).

### Phase 2: Open Access Resolution (Primary Sources)

Query the major OA aggregators. Fire these in parallel — first success with a usable PDF/text URL
wins.

1. **Unpaywall** (DOI required): `GET https://api.unpaywall.org/v2/{doi}?email={your_email}`. Check
   `best_oa_location.url_for_pdf`. If no direct PDF, check all entries in `oa_locations[]` — try
   each URL. Note the `version` field (publishedVersion / acceptedVersion / submittedVersion).
2. **OpenAlex** (DOI or OpenAlex ID): `GET https://api.openalex.org/works/doi:{doi}`. Check
   `open_access.oa_url`, `best_oa_location`, and iterate all `locations[]`. OpenAlex also exposes
   `fulltext_origin` and may provide TEI XML access for some papers.
3. **Semantic Scholar** (any supported ID):
   `GET https://api.semanticscholar.org/graph/v1/paper/{id}?fields=openAccessPdf,isOpenAccess`.
   Check `openAccessPdf.url`.
4. **CrossRef TDM links** (DOI required): From the CrossRef metadata already fetched in Phase 1,
   check `message.link[]` for entries with `intended-application: "text-mining"`. These may provide
   direct full-text access (XML or PDF).
5. **OpenCitations** (DOI required): `GET https://api.opencitations.net/index/v2/metadata/{doi}`.
   Check the `oa_link` field for a direct OA URL. Free, no auth, 1B+ citation links indexed.

### Phase 3: Publisher Direct Access

If Phase 2 returned no usable URL, try constructing the PDF URL directly from the DOI and publisher
identity. Use the `doi_prefix` and `publisher` from the canonical record to route.

**Fully open-access publishers** (always free — try these URL patterns first):

* **PLOS** (`10.1371`): `https://journals.plos.org/{journal}/article/file?id={doi}&type=printable`
* **MDPI** (`10.3390`): append `/pdf` to article URL (e.g.,
  `https://www.mdpi.com/2073-8994/11/10/1189/pdf`)
* **Frontiers** (`10.3389`): `https://www.frontiersin.org/articles/{doi}/pdf`
* **BMC / SpringerOpen**: `https://link.springer.com/content/pdf/{doi}.pdf`

**Major subscription publishers** (free for OA articles only):

* **Elsevier** (`10.1016`): `https://www.sciencedirect.com/science/article/pii/{PII}/pdf` for OA
  articles. TDM API: `GET https://api.elsevier.com/content/article/doi/{doi}?httpAccept=text/xml`
  (requires `ELSEVIER_API_KEY`).
* **Springer Nature** (`10.1038`, `10.1007`): `https://link.springer.com/content/pdf/{doi}.pdf` for
  OA articles. Also check for SharedIt read-only links at `https://rdcu.be/{hash}` — these provide
  view access even for paywalled articles.
* **Wiley** (`10.1002`): `https://onlinelibrary.wiley.com/doi/pdfdirect/{doi}` for OA articles.
* **IEEE** (`10.1109`): `https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={article_number}`.
  IEEE Access journal is fully OA.
* **ACM** (`10.1145`): `https://dl.acm.org/doi/pdf/{doi}`. ACM Author-izer service lets authors post
  free-access links.
* **Taylor & Francis** (`10.1080`): `https://www.tandfonline.com/doi/pdf/{doi}`
* **SAGE** (`10.1177`): `https://journals.sagepub.com/doi/pdf/{doi}`
* **ACS** (`10.1021`): `https://pubs.acs.org/doi/pdf/{doi}`. ACS AuthorChoice articles are CC-BY.

Note: DOI prefix alone is not always reliable for publisher identification — Elsevier alone has 26+
prefixes. The CrossRef `member` field from Phase 1 is the authoritative publisher identifier. Use
prefix as a fast hint, fall back to CrossRef member for routing.

### Phase 4: Domain-Specific Sources

If Phases 2-3 did not yield full text, try domain-specific repositories.

1. **PubMed Central / Europe PMC** (biomedical papers):
   * If PMCID is known:
     `GET https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/ BioC_json/{PMCID}/unicode`
     for structured full text.
   * Europe PMC: `GET https://www.ebi.ac.uk/europepmc/webservices/rest/{PMCID}/fullTextXML` for JATS
     XML. Also try direct PDF: `https://europepmc.org/articles/{pmcid}?pdf=render`.
   * Also check PMC OA subset via efetch:
     `Entrez.efetch(db="pmc", id=PMCID, rettype="full", retmode="xml")`.
   * **PubMed LinkOut**: Query
     `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id={pmid}&cmd=llinks`
     to get third-party free full-text links registered with NCBI. Publishers and repositories
     register these links directly — a source most agents miss.
   * **NIH mandate awareness**: Papers from NIH-funded research accepted after 2025-07-01 must be in
     PMC with no embargo. If the paper acknowledges NIH funding and is recent, PMC is very likely to
     have it.
   * **PMC migration note**: PMC is transitioning from FTP to Cloud Service between Feb–Aug 2026.
     For bulk access, prefer the PMC Cloud Service (`s3://pmc-oa-opendata/`) over FTP.
2. **arXiv** (CS, math, physics, stats, quant-bio, quant-fin, EE):
   * If `arxiv_id` is known: download directly from `https://arxiv.org/pdf/{arxiv_id}.pdf` or
     `https://export.arxiv.org/pdf/{arxiv_id}`.
   * If `arxiv_id` is unknown: search by title via
     `http://export.arxiv.org/api/query?search_query=ti:{title}&max_results=3`. Verify match by
     title similarity + author overlap.
3. **bioRxiv / medRxiv** (biology, medicine preprints):
   * Query by DOI: `GET https://api.biorxiv.org/details/biorxiv/{doi}/na/json`.
   * Use the `/pubs/` endpoint to find preprint-to-published mappings:
     `GET https://api.biorxiv.org/pubs/biorxiv/{published_doi}`.
   * PDF URL pattern: `https://www.biorxiv.org/content/{doi}v{version}.full.pdf`.
4. **SSRN** (social sciences, law, economics): Search by title on SSRN. PDF URL pattern:
   `https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID{id}.pdf?abstractid={id}`.
5. **RePEc / EconPapers** (economics): Search for working paper versions that may be freely
   available.
6. **OSF Preprints** (multidisciplinary): Query OSF API for preprint matches by title. PDF download
   at `https://osf.io/preprints/{provider}/{id}/download`.
7. **Conference proceedings** — many top venues are 100% open access with predictable URLs:
   * **ACL Anthology**: `https://aclanthology.org/{id}.pdf` (all computational linguistics)
   * **NeurIPS**: `https://proceedings.neurips.cc/paper_files/paper/{year}/file/{hash}-Paper.pdf`
   * **ICML / PMLR**:
     `https://proceedings.mlr.press/v{volume}/{author}{suffix}/{author}{suffix}.pdf`
   * **CVF** (CVPR, ICCV, ECCV): `https://openaccess.thecvf.com/` (CVPR 2013 onward)
   * **AAAI**: `https://ojs.aaai.org/` (OJS-based, supports OAI-PMH)
   * **IJCAI**: `https://www.ijcai.org/proceedings/{year}/{number}.pdf`
   * **USENIX**: all proceedings freely available as PDFs
   * **JMLR**: `https://jmlr.org/papers/` (all open access)
   * **OpenReview.net** (ICLR, NeurIPS workshops): API at `https://api.openreview.net/`
8. **NASA ADS** (astronomy, astrophysics):
   `GET https://api.adsabs.harvard.edu/v1/search/query?q={query}`. API key required. Full-text links
   via `/resolver/{bibcode}/esource`. Covers 15M+ records.
9. **INSPIRE-HEP** (high-energy physics): `GET https://inspirehep.net/api/literature?q={query}`. No
   auth required. PDF links in `metadata.documents[].url`. Covers 1.5M+ records.
10. **Government repositories**:
    * **ERIC** (education): `GET https://api.ies.ed.gov/eric/?search={query}&format=json`. PDFs at
      `https://files.eric.ed.gov/fulltext/{ED_number}.pdf`. ~1.5M records, ~25% full text.
    * **OSTI.gov** (DOE-funded research): `GET https://www.osti.gov/api/v1/records?title={query}`.
      Covers journal articles and technical reports. OAI-PMH also available.

### Phase 5: Repository Aggregators

Search aggregators that index institutional repositories, author deposits, and funder-mandated
copies.

1. **CORE** (requires free API key): `GET https://api.core.ac.uk/v3/search/works?q={title}`. CORE
   aggregates 40M+ full-text papers from 10,000+ institutional repositories. Check results for
   `downloadUrl` or direct PDF links.
2. **OpenAIRE Graph**: Query the Graph API for publications matching the DOI or title. Especially
   strong for EU-funded research (Horizon 2020/Europe mandates OA within 6-12 months).
3. **HAL** (strong for French/European research):
   `GET https://api.archives-ouvertes.fr/search/?q={title}&fq=submitType_s:file&fl=uri_s,files_s`.
   Filter for records that actually have deposited files using `submitType_s:file`. PDF in
   `fileMain_s` field or at `https://hal.science/{halId}/document`.
4. **Zenodo** (conference papers, reports, datasets with papers):
   `GET https://zenodo.org/api/records?q={title}`. Check file attachments in record metadata. Direct
   file download at `https://zenodo.org/records/{id}/files/{filename}?download=1`.
5. **BASE** (Bielefeld Academic Search Engine): 400M+ documents from 12,000+ providers. API at
   `https://api.base-search.net/` uses Solr query syntax. **Requires IP whitelisting** — request
   access via their contact form. Key fields: `dctitle:` (title), `dcauthor:` (author), `dclink:`
   (document URL), `dcoa:1` (OA filter).
6. **DOAJ OAI-PMH** (gold OA journals): Harvest article records from `https://doaj.org/oai.article`.
   The Dublin Core `relation` field contains direct full-text URLs. If a paper is in a DOAJ-indexed
   journal, this is a reliable path to a legal PDF.

### Phase 6: Preprint Linkage (Creative Fallback)

If the published version is paywalled, actively hunt for preprint or accepted manuscript versions.

1. Check CrossRef `relation` fields for `has-preprint` / `is-preprint-of` links discovered in Phase
   1\.
2. Query bioRxiv `/pubs/` endpoint with the published DOI to find a linked preprint.
3. Search arXiv by exact title — many published papers have arXiv preprints even when the metadata
   does not link them.
4. Search OpenAlex `locations[]` — it often lists preprint server copies that other services miss.
5. Search Semantic Scholar — its corpus links preprints to published versions.
6. Use Dissemin API (`https://dissem.in/api/`) — query by DOI or title+authors+date. Returns OA
   classification and `pdf_url` when available. Also indicates self-archiving policy.

### Phase 7: Web Discovery (Broad Search)

If structured APIs have not yielded the paper, search the open web.

1. **Google Scholar** via the `scholarly` Python library: `scholarly.search_pubs(title)`. Check
   `eprint_url` for free PDF links. Scholar often finds PDFs on author homepages, lab websites, and
   university course pages that no API indexes.
   * Be aware: Google may rate-limit or CAPTCHA. Use sparingly and only after API sources are
     exhausted.
2. **Web search with file-type targeting**: Search for `"{exact paper title}" filetype:pdf` using a
   web search API. This surfaces PDFs on university servers, personal pages, and course materials.
   Also try `"{author name}" "{paper title}" filetype:pdf site:edu` for faculty-hosted copies.
3. **Internet Archive Scholar** (`https://scholar.archive.org/`): Full-text search over 25M+ open
   papers. Built on the Fatcat open catalog (`api.fatcat.wiki/v0/`). Also check the Wayback Machine
   for cached versions of known publisher URLs:
   `GET https://archive.org/wayback/available?url={publisher_url}`. For raw PDFs from the archive,
   use the `id_` suffix: `https://web.archive.org/web/{timestamp}id_/{original_url}`.
4. **Author homepage / lab page discovery**: From metadata, identify the first/corresponding
   author's affiliation. Search for their university profile page or lab publications page —
   researchers often self-host PDFs of their papers. Also query the **ORCID API**
   (`https://pub.orcid.org/v3.0/{orcid}/works`, requires OAuth2 `/read-public` token, 24 req/sec) to
   find author work listings with URLs to self-archived copies.

### Phase 8: HTML Full-Text Extraction

Some publisher sites display full text in HTML but restrict PDF download. HTML pages also often
contain machine-readable pointers to the PDF that are invisible to casual browsing.

1. If a publisher landing page URL is known (from DOI resolution), fetch the HTML.
2. **Quick paywall check via Schema.org JSON-LD** — before any heavy parsing, look for a
   `<script type="application/ld+json">` block in the HTML. If it contains
   `"isAccessibleForFree": false`, the article is paywalled on this site — skip directly to the next
   phase instead of wasting time parsing the page. Many publishers embed this structured data for
   Google indexing.
3. **Check `citation_pdf_url` meta tag** — parse the HTML `<head>` for
   `<meta name="citation_pdf_url" content="...">`. This is the standard mechanism used by Google
   Scholar, Unpaywall, and Zotero to discover PDFs. If present, download directly from that URL.
   Also check related tags: `citation_title`, `citation_doi`, `citation_authors` to verify you are
   on the correct article page.
4. If no `citation_pdf_url` is found but the full article text is present in the page body, extract
   the article text using content-extraction techniques (main content detection, stripping
   navigation/ads). Note: some "soft paywalls" load full text in the DOM but hide it behind CSS
   overlays or JavaScript modals — check the raw HTML, not just the rendered view.
5. Save as plain text — this is often sufficient for AI processing and avoids PDF extraction issues
   entirely.

### Phase 9: Non-Standard Sources

If the major APIs and aggregators failed, try less conventional but still structured sources:

* Search for the paper title in PhD theses and dissertations — a thesis chapter may reproduce the
  paper's content. Check OATD (`https://oatd.org/`, 7M+ theses from 1,100+ institutions) and NDLTD.
* Check if the venue uses OpenReview (`https://openreview.net/`) — all submissions are openly
  hosted.
* Search for conference workshop versions, extended abstracts, or supplementary materials hosted
  separately from the main paper.
* Look for slide decks, posters, or technical reports by the same authors covering the same results.
* Search GitHub — authors sometimes include paper PDFs alongside their code implementations.
* Check if the paper appears in a government or NGO report under open-access terms.
* Try alternate URL patterns on the publisher site — some expose PDFs at predictable paths that
  differ from the landing page.

### Phase 10: Creative Last-Resort Discovery

If every method above has failed, do not give up. Stop following the playbook. Use the canonical
record from Phase 1 — title, authors, year, venue, topic — and think creatively about where this
specific paper's text might exist. Consider the field, the authors, the institution, the funding
source, the publication venue, the time period, and any other clue. There are no prescribed steps
here. Improvise. Try anything that might work.

### Phase 11: Download, Validate, and Save

Throughout Phases 2-10, collect all discovered URLs into a **ranked candidate list** using the
scoring system below. Do not stop at the first URL found — gather candidates from multiple sources,
then work through the list from highest to lowest score. This resilience matters because the
top-ranked URL may be temporarily down, geo-blocked, or rate-limited.

1. Download the best candidate found (highest version quality, best format).
2. **Validate the download**:
   * If PDF: check HTTP `Content-Type` header is `application/pdf`. Verify the file starts with
     `%PDF-` magic bytes and contains an `%%EOF` marker (truncated PDFs lack it). Check file size >
     10 KB (a typical paper is 100KB-5MB). Extract text from the first page using `pymupdf` or
     `pdfplumber` and fuzzy-match the extracted title against the canonical title (similarity >
     0.80). For stronger verification, run `pdf2doi` against the downloaded file to extract the
     embedded DOI from text/metadata and compare it against the canonical DOI.
   * If XML/text: verify the content contains the expected title and is not an error page or login
     redirect.
   * If any validation fails, discard the candidate and try the next best from the scored list.
3. Save to `{{ output_dir }}` with filename format:
   `{first_author_last_name}_{year}_{short_title_slug}.{ext}` (e.g.,
   `vaswani_2017_attention_is_all_you_need.pdf`).
4. Return a result record containing:
   * `status`: `"success"` | `"partial"` | `"not_found"`
   * `file_path`: path to the saved file (if downloaded)
   * `format`: `"pdf"` | `"xml"` | `"text"` | `"html"`
   * `version`: `"published"` | `"accepted"` | `"submitted"` | `"preprint"` | `"working_paper"` |
     `"unknown"`
   * `source`: URL or API name where the file was obtained
   * `confidence`: float 0.0-1.0 (based on title match, author overlap, year match)
   * `canonical_record`: the full metadata record built in Phase 1
   * `all_attempted_sources`: list of sources tried and their status

* * *

## API Keys and Credentials

All API keys are stored as environment variables in `.env` (loaded automatically via `direnv`). Read
keys from environment variables at runtime using `os.environ`. **NEVER** hardcode keys in source
files.

Before starting, check which keys are available. Skip services whose required keys are missing — do
not fail, just move to the next source in the cascade.

| Environment Variable | Service | Required? |
| --- | --- | --- |
| `SCHOLAR_EMAIL` | CrossRef, Unpaywall | **Yes** — `mailto:` for CrossRef polite pool and email param for Unpaywall |
| `OPENALEX_API_KEY` | OpenAlex | **Yes** — required since Feb 2025, free at openalex.org |
| `SEMANTIC_SCHOLAR_API_KEY` | Semantic Scholar | Recommended — free at semanticscholar.org |
| `CORE_API_KEY` | CORE | Required for CORE — free at core.ac.uk |
| `NCBI_API_KEY` | PMC / PubMed | Optional — raises rate limit 3→10 req/sec |
| `ELSEVIER_API_KEY` | Elsevier / ScienceDirect | Optional — free at dev.elsevier.com |
| `SPRINGER_API_KEY` | Springer Nature | Optional — free at dev.springernature.com |

Services that need no key at all: arXiv, bioRxiv, medRxiv, Europe PMC, Zenodo, HAL, Dissemin, OSF,
DOAJ, Internet Archive, OpenCitations, INSPIRE-HEP, ORCID (public data).

If `SCHOLAR_EMAIL` is not set, abort with a clear error — it is the minimum required credential for
this skill.

## API Reference Summary

| Service | Auth | Rate Limit |
| --- | --- | --- |
| CrossRef | `SCHOLAR_EMAIL` | 50 req/sec (polite) |
| Unpaywall | `SCHOLAR_EMAIL` | 100K req/day |
| OpenAlex | `OPENALEX_API_KEY` | 100K credits/day |
| Semantic Scholar | `SEMANTIC_SCHOLAR_API_KEY` | 1 req/sec |
| CORE | `CORE_API_KEY` | 5 req/10 sec |
| OpenCitations | None | Be polite |
| arXiv | None | Use export subdomain |
| bioRxiv/medRxiv | None | Be polite |
| PMC / NCBI | `NCBI_API_KEY` | 3-10 req/sec |
| Europe PMC | None | Generous |
| NASA ADS | API key required | Per plan |
| INSPIRE-HEP | None | Be polite |
| ORCID | OAuth2 `/read-public` | 24 req/sec |
| Zenodo | None | 60-100 req/hour |
| HAL | None | Be polite |
| Dissemin | None | Be polite |
| OSF | None | 100 req/hour |
| DOAJ | None | Be polite |
| Google Scholar | None (no official API) | Rate-limited by IP |

All services expect a descriptive `User-Agent` header with `SCHOLAR_EMAIL`. Implement exponential
backoff with jitter (base 1s, max 30s, factor 2x) on HTTP 429/5xx responses. Use a circuit breaker:
if a source fails >5 times in 5 minutes, skip it for 30 minutes. Cache all API responses keyed by
DOI (lowercase, URL-decoded) — never re-fetch the same identifier.

## Python Libraries

| Library | Purpose |
| --- | --- |
| `habanero` | CrossRef API client (DOI lookup, title-to-DOI) |
| `unpywall` | Unpaywall API (OA PDF discovery by DOI) |
| `pyalex` | OpenAlex API (works, authors, OA locations) |
| `semanticscholar` | Semantic Scholar API (paper search, OA PDF) |
| `arxiv` | arXiv search + PDF/source download |
| `biopython` | `Bio.Entrez` for PubMed/PMC efetch/esearch |
| `pyeuropepmc` | Europe PMC search + full-text XML retrieval |
| `scholarly` | Google Scholar search (use as last resort) |
| `paperscraper` | Multi-preprint server search (arXiv/bioRxiv) |
| `sickle` | OAI-PMH harvesting from institutional repositories |
| `pymupdf` | PDF text extraction and validation |
| `pdf2doi` | Reverse-extract DOI from a downloaded PDF for verification |
| `findpapers` | Multi-database parallel search (arXiv, IEEE, OpenAlex, PubMed, Scopus) |
| `httpx` | Async HTTP client for parallel API calls |

* * *

## Candidate Scoring

When multiple versions are found, score candidates to pick the best:

* **+5** exact DOI match
* **+4** title similarity > 0.95
* **+3** title similarity 0.85-0.95
* **+2** author overlap > 50%
* **+2** exact year match
* **+1** year within +/- 1
* **+3** published version
* **+2** accepted manuscript
* **+1** preprint / submitted
* **+2** structured XML/text format
* **+1** born-digital PDF
* **-2** scanned PDF (no selectable text)

Pick the candidate with the highest total score. On ties, prefer the source with higher trust
ranking: publisher > PMC > major repository > preprint server > personal page > other.

* * *

## Done When

* A result record is returned with `status`, `source`, `version`, `confidence`, and
  `all_attempted_sources` fields populated.
* If `status` is `"success"`: a validated file exists at `file_path` with confirmed title match
  (confidence > 0.80).
* If `status` is `"not_found"`: at least **10 distinct sources** were attempted (documented in
  `all_attempted_sources`), including Unpaywall, OpenAlex, Semantic Scholar, CrossRef, at least one
  preprint server, and at least one repository aggregator.
* The canonical metadata record is complete with all discoverable IDs.

## Forbidden

* **NEVER** fabricate a download URL. Every URL must come from an API response or a verified web
  page.
* **NEVER** return a file without validating that its content matches the requested paper (title
  fuzzy-match > 0.80).
* **NEVER** save login pages, error pages, or CAPTCHA pages as if they were paper content.
* **NEVER** skip Phase 1 (identification). Downloading without a canonical record leads to
  wrong-paper errors.
* Do not hammer a single API. Respect rate limits and implement backoff.
* Do not re-download a paper already present in `{{ output_dir }}` with matching DOI — check for
  existing files first.
