---
sidebar_position: 0
---

# Introduction

## About this docs

- **Overview & goals**: What the library does and who it is for
- **Getting Started**: Basic usage of the public API
- **Scenarios**: Typical usage flows
- **API spec**: Public API contract (exceptions, return values)

For implementation details, design decisions, and testing policy, see the [Development docs](/docs/dev/intro).

## What is Fino Filing

Fino Filing is a Python library for collecting, searching, and downloading disclosure documents using the EDINET API.

**Target users** are Stock Holders, or Investigator who want to analyze financial aata or collect them efficiently in your environments.

It is provided as a library to be used via `import fino_filing` from Python code.

:::warning
This Package is now developed as hobby project and all functionality is not fixed and stable.

**Current implementation**: Add, search, and retrieve via Collection / Catalog / LocalStorage / Filing (including EDINET and Edgar extensions) to a local store. API integration (EDINET client, collection) is planned.
:::

---

## Goals

- Provide a simple client for the EDINET/Edgar API (planned)
- Sync document list API results to an internal data store and enable flexible search
- Allow document collection by company, period, document type, etc.
- Design so that storage location and structure are under the user’s control
