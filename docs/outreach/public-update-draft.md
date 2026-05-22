# Public Update Draft

Project Parva's Nepali date conformance work now has a first public milestone.

A standalone calendar source consistency benchmark inspired by this work was
merged into `yarsa/nepal-compliance`. The check compares duplicated frontend and
backend BS month tables and reports overlapping source drift without changing
runtime behavior or adding any dependency.

Parva now also has public conformance fixtures for Nepali date regression
classes: source drift, month-length disagreements, conversion boundaries,
invalid dates, unsupported ranges, and review-needed future BS data.

The focus is broader than date conversion. It is about making Nepali date/time
software easier to test, review, and discuss from public evidence without
claiming endorsement, production impact, or official authority.
