# Evaluated-state provenance record: a reporting protocol

Companion to `PROPOSED_EVALUATED_STATE_REPORT_SCHEMA.json` (JSON Schema
2020-12) and `EXAMPLE_bytetrack_mot17_valhalf.json`, a filled record whose three
artifact hashes recompute from the real audited files.

## What it is for

A reported tracking score is computed on one specific file. Today nothing in a
submission identifies that file, the transformation that produced it, or the
evaluator settings that scored it. This record closes that gap in a form a third
party can check mechanically.

## Structure

Four required blocks, mirroring the state path, plus one optional block.

```
pre_transition_state   what the tracker produced          (R0)
transition             what was applied to it, in order
evaluated_state        the exact artifact that was scored (R2)
evaluation             what produced the reported number
reference_side_diagnostics   OPTIONAL — needs ground truth
```

### Why the reference-side block is optional

`R1` and the admission classes require ground truth for the evaluated split. A
submitter cannot compute them at submission time for a held-out benchmark, and
they are not deployable. **A record without that block is complete.** This is a
deliberate design decision: a protocol that required R1 would be unusable by the
people who need to fill it in. The block exists so that an auditor who *does*
have ground truth has somewhere to put the result.

### Why `transition.structural_type` is load-bearing

It is an enum over the four transition types, and it determines which
diagnostics are even definable:

| structural_type | keys | surviving content | admission / R1 definable |
|---|---|---|---|
| `row-additive` | grow | unchanged | yes |
| `key-additive-content-rewriting` | grow | changed | no |
| `rewrite-only` | unchanged | changed | no |
| `identity-remapping` | may shrink | identity changed | no |

A validator can therefore reject a record that claims admission counts under a
`rewrite-only` transition. That is a machine-checkable consistency rule, not a
style guideline.

## Five things the schema requires that a checklist does not

1. **`sha256` at all three states.** Makes "which file was scored" answerable
   rather than describable.
2. **`row_identity_fields`.** Without the tuple that makes a row unique, no state
   comparison is well defined. The schema forces it to be declared.
3. **`stages[].parameter_semantics`.** One line per parameter stating the exact
   condition it controls, including strictness. This exists because the audited
   releases contain a live example of the failure it prevents: `n_min` is a
   tracklet-length threshold (`n_frame > n_min`, strict), yet it is naturally
   misread as a minimum gap.
4. **`stages[].call_site`.** The audited releases disagree between signature
   defaults and call sites — ByteTrack's `dti` has `n_min=25` in its signature
   and `n_min=5` at its `__main__` call site. Reporting the signature would
   misreport the run.
5. **`evaluation.configuration.resolved_settings`.** The *resolved* value of every
   setting that changes scoring semantics, including values left at defaults.
   This is the field that catches the case where a default silently defines the
   science: at the pinned TrackEval commit, `DO_PREPROC` defaults to `True`, and
   that default is what makes the scoreable reference `mark != 0 AND class == 1`.

## Answers to the protocol questions

**IS THIS A REAL PROTOCOL OR JUST A CHECKLIST?**
A protocol. It has a typed schema with required fields and patterns, an enum that
induces machine-checkable cross-field rules, a validated worked example, and
integrity hashes that let a third party verify rather than trust. Table S33 is a
checklist: three prose rows naming fields, with no types, no
required-versus-optional distinction, no machine-readable form and no example.

**WHAT DOES IT ENABLE THAT TABLE S33 DOES NOT?**
Four things. (i) Mechanical validation — a record can be checked by a program,
including the consistency rule between `structural_type` and the diagnostics
block. (ii) Verification rather than description — the three `sha256` fields let
a reader confirm the exact scored artifact. (iii) Honest incompleteness — fields
like `selection_provenance` have an explicit `unresolved` value, so a gap is
recorded as a gap instead of being omitted. The schema comment states the rule
that matters: *"No recorded validation metric" is NOT "confirmed"; it is
"unresolved".* (iv) Split definition rather than split name — `split.definition`
requires the construction rule, because `MOT17-val_half` names a split without
defining it, and the obvious reconstruction gives 2,659 frames where the actual
split has 2,652.

**CAN A THIRD PARTY IDENTIFY THE EXACT SCORED STATE FROM IT?**
Yes. `evaluated_state.sha256` plus `row_count` plus `format` identify the artifact
uniquely; `split.ground_truth_sha256` pins what it was scored against.

**CAN A THIRD PARTY RECONSTRUCT THE TRANSITION?**
Yes for the audited class of operators, and the schema is explicit about the
limit. `stages[]` carries repository, commit, source file, symbol, call site,
parameter values and parameter semantics, in applied order — order is required
because stage composition is not commutative. What this does *not* give is
bit-exact reproduction where the operator depends on unpublished inputs; that
case is recorded through `checkpoint.upstream_checksum_published: false` rather
than hidden.

**IS EVALUATOR IDENTITY UNAMBIGUOUS?**
Yes, and more tightly than a commit alone. `evaluator_commit` plus
`evaluator_modified` plus `resolved_settings` pin the scoring semantics. The
`omitted_arguments_and_why` field exists for a real constraint found in the
audit: at the pinned commit, `--SEQMAP_FILE` and `--OUTPUT_FOLDER` *must* be
omitted for the DANCE benchmark, because the script registers every
`None`-default argument with `nargs='+'` and passing either raises `TypeError`.
A record that listed only the command line would omit the reason the command
line looks the way it does.

## On the "four records" framing

The paper currently frames the recommendation as four records. The schema has
four required blocks, so the number survives — but it survives because it is
right, not because it was preserved. The change is that evaluator metadata is
promoted from a trailing clause into a required block with required
`resolved_settings`, since the audit found a default in that block silently
defining the paper's own scoreable-reference rule. If the choice were between
keeping the number and keeping that requirement, the requirement wins.
