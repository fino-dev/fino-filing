# fino-filing Overview

## Summary

fino-filing is a Python library for collecting, searching, and downloading disclosure documents using the EDINET API.

Target users: OSS users, data analysts, and Python engineers.

It is provided as a library to be used via `import fino_filing` from Python code; no CLI is provided.

**Current implementation**: Add, search, and retrieve via Collection / Catalog / LocalStorage / Filing (including EDINET and EDGAR extensions) to a local store. API integration (EDINET client, collection) is planned.

---

## Goals

- Provide a simple client for the EDINET/EDGAR API (planned)
- Sync document list API results to an internal data store and enable flexible search
- Allow document collection by company, period, document type, etc.
- Design so that storage location and structure are under the user’s control

---

## Usage (high level)

(Use cases and scenarios will be documented here.)
