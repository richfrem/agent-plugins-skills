# L4 Tiered Source Authority
**Purpose:** Algorithmic translation of evidence quality into confidence scoring.
**Mechanics:**
1. Determine the maximum allowed `Confidence Level` (High, Medium, Low) based strictly on Source Tiers (T1=Authoritative, T2=Internal, T3=Chat/Informal).
2. Propagate this score to the final output.
3. If contradictions exist, favor the higher tier and downgrade confidence explicitly.
