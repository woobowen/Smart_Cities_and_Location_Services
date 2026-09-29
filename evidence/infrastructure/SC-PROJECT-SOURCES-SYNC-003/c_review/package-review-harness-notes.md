# C archive harness execution notes

The first invocation of `independent_package_review.py` exited with
`KeyError: 'source_path'` before extraction or execution. C's new harness had
assumed every manifest row carried this optional field. Reading the actual
manifest showed that the two relocated README/requirements entries carry it;
the other 113 rows use their normal repository `path`. The harness now uses
`member.get('source_path', path)`. This was a C harness defect, not a package or
implementation defect, and did not modify the archive or repository sources.

While assembling the final C result, an auxiliary exact-equality assertion
between manifest `metadata` and `assignment.json` rejected their comparison:
the manifest also contains the pre-existing derived
`evidence_master_spec_and_lock: NOT_AVAILABLE` field. C read `package.py` and
compared the historical manifest. All original identity-source fields remain
equal, and the complete metadata object equals the historical executed package.
The final record states this actual relationship rather than dropping the extra
field or falsely claiming object equality. No engineering source was changed.
