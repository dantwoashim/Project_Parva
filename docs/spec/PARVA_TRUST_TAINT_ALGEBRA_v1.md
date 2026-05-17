# PARVA_TRUST_TAINT_ALGEBRA v1

Authority is monotone. Derived fields may retain or lose authority, but they
must not upgrade authority without a signed review witness and source docket.

Required order, strongest to weakest:

1. structured_official
2. archived_official
3. reviewed_institutional
4. computed_certified
5. computed_uncertified
6. static_reference
7. third_party_reference
8. user_supplied
9. unknown_unverified

Public outputs must carry the weakest authority of their fields and must keep
review-required flags when any field requires review.
