---
name: check-name-clearance
description: Check whether a proposed company, product, app, or App Store seller name is already used or likely to conflict. Use when the user provides a name and asks to check duplicates, availability, registrability, domain availability, App Store seller suitability, social/project/package-name collisions, trademark risk, state LLC name availability, D-U-N-S/Apple identity risk, or wants a concise clearance report before forming a US LLC or choosing a brand. Can also generate names, but duplicate checking is the primary behavior.
---

# Check Name Clearance

## Core stance

Default to checking a user-supplied name for duplicate use. Name originality is a practical clearance problem, not just a creativity problem. Browse before making availability claims because domains, trademarks, app listings, repositories, packages, and business registries change.

Present results as screening, not legal advice. Say "low visible duplicate risk" or "worth attorney clearance," not "legally clear," unless the relevant official registry and jurisdiction were actually checked.

## Default workflow for one proposed name

1. Normalize the input:
   - Brand form: `Name`
   - Legal form: `Name LLC`
   - Domain root: `name`
   - Variants: lowercase, plural, spaced, hyphenated, phonetic neighbors, common misspellings.
2. Ask only blocking questions:
   - Formation state, if the user needs actual LLC name availability.
   - Product/app category and target markets, if trademark risk matters.
3. Run a duplicate sweep:
   - Exact web use.
   - Company/legal entity use.
   - Trademark use.
   - App Store/developer use.
   - Domain use.
   - Social/project/package use.
4. Separate findings by surface:
   - "Legal blocker," "brand/trademark concern," "domain occupied," "common-law/product collision," "minor unrelated use," or "no obvious duplicate found."
5. Return a concise verdict:
   - `Proceed`, `Proceed with caution`, `Rename`, or `Need attorney/state check`.

If the user asks for name generation instead, generate candidates and then run the same duplicate sweep on the shortlist.

## Fast duplicate tools

Use these for broad public-name collision checks before deeper official searches:

- Namechecker: `https://namechecker.vercel.app/`
- Namechk: `https://namechk.com/`
- KnowEm: `https://knowem.com/`
- Google/Bing exact phrase search.
- OpenCorporates: `https://opencorporates.com/`
- SEC EDGAR: `https://www.sec.gov/search-filings`
- LinkedIn company search, Crunchbase, Product Hunt, GitHub organizations.
- Package indexes when relevant: npm, PyPI, crates.io, RubyGems, Docker Hub.

Treat bulk checker tools as convenience screens. If they show "available," still verify important surfaces directly.

## Domain checks

For a proposed name, always check the domain root and common TLDs:

- Primary: `.com`
- Startup/app backup: `.co`, `.io`, `.app`, `.dev`
- General backup: `.net`, `.org`
- AI category only if relevant: `.ai`

Use:

- ICANN Lookup: `https://lookup.icann.org/`
- Verisign RDAP for `.com`: `https://rdap.verisign.com/com/v1/domain/<domain>`
- Registrar search: Namecheap, GoDaddy, Porkbun, Cloudflare Registrar, or the registrar the user prefers.
- DNS quick check: NS/A/CNAME records when command-line DNS tools are available.

Report domain results as:

- `available-looking`: no RDAP/DNS result, but registrar purchase still required.
- `registered-unused`: registered with parking/default nameservers or no active site.
- `active-conflict`: active site, product, company, or app.
- `premium/for-sale`: purchasable but not clean availability.
- `unknown`: tool timeout, blocked lookup, or inconsistent data.

Do not overvalue a weaker name just because `.com` is available. Do not recommend a name with a serious trademark/company collision just because the domain is open.

## Official legal and trademark checks

Use official tools for surfaces that can block registration or create legal risk.

### LLC legal entity

Use the target state's Secretary of State or Division of Corporations business name search. Common states:

- Delaware: `https://icis.corp.delaware.gov/Ecorp/EntitySearch/NameSearch.aspx`
- Wyoming: `https://wyobiz.wyo.gov/Business/FilingSearch.aspx`
- California: `https://bizfileonline.sos.ca.gov/search/business`
- Nevada: `https://esos.nv.gov/EntitySearch/OnlineEntitySearch`
- Florida: `https://search.sunbiz.org/Inquiry/CorporationSearch/ByName`
- Texas: use SOSDirect for formal filing checks; use Comptroller taxable entity search only as a supporting screen.

If the state is unknown, say that LLC availability cannot be confirmed and run broad duplicate screening only.

### US trademarks

- USPTO Trademark Search: `https://www.uspto.gov/trademarks/search`
- TSDR for status and owner records: `https://tsdr.uspto.gov/`
- Trademark ID Manual for goods/services classes: `https://idm-tmng.uspto.gov/`

Search exact marks, plural/singular forms, spacing variants, likely misspellings, phonetic neighbors, and marks in related classes. For apps and software, pay attention to classes 9 and 42; add class 35 when marketplaces, business services, advertising, or seller-platform functions are plausible.

### International trademarks

- WIPO Global Brand Database: `https://branddb.wipo.int/en/quicksearch`
- EUIPO eSearch/TMview/TMclass: `https://www.euipo.europa.eu/en/search`

Use these when the app will be distributed internationally, the name looks globally commercial, or a US search is clean but the word feels likely to be used elsewhere.

## Apple/App Store and D-U-N-S checks

- Apple Developer organization enrollment: `https://developer.apple.com/programs/enroll/`
- Apple D-U-N-S lookup: `https://developer.apple.com/enroll/duns-lookup/`
- Apple Search API for visible app/developer collisions: `https://itunes.apple.com/search?term=<name>&country=US&media=software`
- Search web for `"<Name>" "App Store"`, `"<Name>" "developer"`, and `"<Name> LLC" "App Store"`.

Apple does not provide a public seller-name availability checker. For App Store seller identity, the legal entity name, D-U-N-S record, company website/domain, and Apple Developer enrollment must align.

## Search query set

For each serious name, run a compact set of searches:

- `"<Name>"`
- `"<Name> LLC"`
- `"<Name>" company`
- `"<Name>" software`
- `"<Name>" app`
- `"<Name>" "App Store"`
- `"<Name>" developer`
- `"<Name>" trademark`
- `"<Name>" "USPTO" trademark`
- `site:opencorporates.com "<Name>"`
- `site:sec.gov "<Name>"`
- `site:github.com "<Name>"`
- `site:npmjs.com "<Name>"`
- `site:pypi.org "<Name>"`

For coined names, also search phonetic and spelling variants. For two-word names, search joined, spaced, and hyphenated forms.

## Naming guidance when asked to generate alternatives

For sober US LLC/App Store seller names:

- Prefer 5-9 letters, 2-3 syllables, easy ASCII spelling.
- Favor hard consonants and simple vowels: k, t, d, r, l, n, s, h.
- Avoid cute endings, fantasy suffixes, excessive x/y/z, invented apostrophes, and trendy tech terms such as AI, SaaS, Cloud, Labs, Systems, Technologies, unless the user asks for them.
- For legal names, test the brand with `LLC` appended.
- For App Store seller use, test whether the name looks credible in "Seller: Name LLC".

When using ancient Greek roots, prefer non-mythological concepts such as:

- Boundary and limit: `horos`, `peras`
- Stone and solid matter: `lithos`, `petra`, `stereos`
- Joining and support: `harmos`, `hedra`, `stathmos`
- Rule and order: `kanon`, `taxis`, `metron`
- Observation and path: `skopeo`, `opsis`, `hodos`, `axon`
- Craft and structure: `tekton`, `stoa`, `pleura`, `gonia`

Lightly Latinize or Anglicize roots when it improves pronounceability. Compress two roots into one natural-looking name only when the result still feels like a company name.

## Risk grading

- Low: no obvious exact commercial use, no visible USPTO conflict, no strong phonetic neighbor in related classes, domain direction plausible, no negative English reading.
- Medium: exact web use exists but unrelated, `.com` taken but inactive, similar marks exist in distant classes, or the name resembles a known company without being identical.
- High: exact or near-exact software/company/trademark collision, famous mark proximity, state LLC conflict in target state, hard Apple/D-U-N-S identity mismatch, or strong negative/regulated connotation.

## Output format for checking one name

Use this schema unless the user asks otherwise:

```text
Name:
Legal form:
What I checked:
Duplicates found:
Trademark / legal risk:
Domain status:
App Store / developer risk:
Social / project / package risk:
Risk:
Verdict:
Next checks:
```

For generated names, use:

```text
Brand:
Legal name:
Pronunciation:
Etymology:
Why it works:
Risk:
Domain direction:
Verdict:
```

Lead with the answer, not the research diary. Include sources or direct tool results for material claims.
