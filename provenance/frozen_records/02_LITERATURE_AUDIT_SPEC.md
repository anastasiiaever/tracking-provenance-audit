# V9 Literature / Disclosure Audit Specification

**Frozen before reading the selected reporting locations in full.**
This is a non-performance measurement. No benchmark value is read, recorded or
compared.

## Population

Exactly the papers, supplements and official repositories of the frozen
deployment universe (8 deployments, 7 systems) at the commits pinned in
`01_SOURCE_MANIFEST.json`.

## Unit of coding

One (pipeline x dataset) result presentation.

## Mutually exclusive statuses

1. `DISCLOSED_IN_RESULT_TABLE_OR_CAPTION`
2. `DISCLOSED_IN_MAIN_METHOD_TEXT`
3. `DISCLOSED_IN_SUPPLEMENT`
4. `DISCLOSED_IN_OFFICIAL_REPOSITORY_ONLY`
5. `NOT_DISCLOSED_IN_FROZEN_SOURCES`
6. `NO_DOCUMENTED_RULE`

## Fixed search order (identical for every pipeline, never varied)

1. result table and its caption
2. main method text
3. supplement / appendix
4. official repository README and released scripts

The first location satisfying the disclosure definition determines the status.

## What counts as disclosure

The source must communicate that post-processing, interpolation or smoothing is
part of the reported pipeline or result.

- The mere existence of a source file does NOT count as paper disclosure.
- Reporting intent must NOT be inferred from code.
- A generic methods sentence that does not connect the step to the reported
  result does not satisfy the definition.

## Frozen source versions

For each system record: paper DOI and version, supplement version, repository
commit (already pinned in `01_SOURCE_MANIFEST.json`).

## Evidence field

Record location (section/table/line) plus a SHORT verbatim quotation. Public
artifacts must respect copyright-safe short-quotation limits; quote the minimum
needed to establish the status.

## Prohibited

Reading, recording or comparing any benchmark performance value while coding
disclosure status.
