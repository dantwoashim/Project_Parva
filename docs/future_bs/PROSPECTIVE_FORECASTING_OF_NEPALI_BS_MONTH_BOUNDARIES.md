---
title: "Prospective Forecasting of Nepali Bikram Sambat Month Boundaries Using Astronomical Evidence and Historical Civil Decisions"
author: "Prabin Ghimire"
affiliation: "Project Parva, Nepal"
date: "2026-09-09"
version: "Working paper 2.0"
study_type: "Computational methods and prospective evaluation protocol"
status: "Preprint draft; BS 2084 outcome pending in the study record"
---

# Prospective Forecasting of Nepali Bikram Sambat Month Boundaries Using Astronomical Evidence and Historical Civil Decisions

Prabin Ghimire  
Project Parva, Nepal  
9 September 2026

## Abstract

A forecast of Nepal's Bikram Sambat calendar must assign astronomical events to dates that will eventually appear in a published civil calendar. Project Parva models that assignment explicitly. Sidereal solar ingresses provide time features; historical month starts provide same-day or next-day labels. Two source-filtered training streams feed month-specific nearest-neighbour and cutoff rules. Weighted votes select thirteen civil boundaries, from which twelve month lengths follow. Structural checks constrain the annual result.

The recorded rolling evaluation reproduces 72 month lengths across BS 2078-2083, using a training cutoff before each target year. These six annual vectors also informed model development. The source register records incomplete primary-document review, and the current astronomy adapter discards the returned ephemeris flags. A targeted reproduction during manuscript revision requested JPL calculations and received Moshier flags. Consequently, the reported result measures agreement with the development corpus under the recorded computational pipeline; attribution to a verified DE440 execution remains open.

The primary prospective outcome is the BS 2084 annual month-length vector. The frozen artifact records the forecast as (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30), with a training cutoff at BS 2083 and a declared freeze time of 5 August 2026. The study defines source review, artifact verification, and five fixed scoring measures for later official evidence. An analysis of adjacent-boundary errors establishes why length accuracy, absolute-date accuracy, and year-total validity require separate evaluation. The contribution is a source-stratified forecasting procedure and an auditable prospective test of published calendar behaviour.

**Keywords:** Bikram Sambat; civil calendar; solar ingress; historical evidence; prospective forecasting; reproducibility

## 1. Introduction

A calendar year in software often ends as a row of twelve integers. For Nepal's Bikram Sambat calendar, each integer carries a practical decision: where one month ends and the next begins. The row determines whether a date exists, when a monthly period closes, and which Gregorian day receives a Nepali date. It also conceals the evidence that produced those decisions.

Project Parva encountered this directly. Its conversion table once placed Shrawan 1, 2082 on 16 July 2025. The published calendar placed it on 17 July. The table gave Ashadh 31 days and Shrawan 32 days; the corrected values were 32 and 31. Their combined length stayed at 63 days, so Bhadra began on the expected date. The annual total stayed valid.

That incident was a table defect. It provided a concrete example of error propagation across adjacent months. The research question concerns the point where a future year still requires a forecast: how should software estimate the civil date assigned to each solar ingress, and what evidence should support that estimate?

Nepal's calendar authority provides a reason to model publication practice explicitly. In a notice dated 5 Falgun 2082, the Nepal Panchanga Nirnayak Bikas Samiti describes the computational basis used for annual Panchangas. It records traditional Saurukta calculation for the Panchanga component, other planetary calculations using Jyotirganitam and Ketaki methods, and a decision to prepare BS 2083 on the BS 2082 basis after a proposed change required further discussion. The notice also calls for technical work on agreement with planetary positions [1]. This is evidence of a managed publication process with an evolving computational basis.

The study asks:

> Given historical BS month starts and astronomical features available through a stated cutoff, what annual month-length vector does a fixed algorithm predict for the next published calendar?

I use *civil decision* to mean the date printed as a month start. The observations are calendar outputs. The institutional reasoning behind an individual output remains a separate subject of study.

The paper develops a source-stratified forecasting method, examines the structure of its errors, and specifies how a frozen prediction will be scored against later evidence. Its primary prospective target is BS 2084. The committed snapshot also contains BS 2085-2200, which records the output of the same frozen procedure across an extended horizon. Those later vectors have the status of model extrapolations.

## 2. Calendar computation and the prediction target

### 2.1 Astronomical events and published dates

The Nepali BS civil calendar has twelve solar months. A Sankranti identifies the Sun's entry into a sidereal zodiac sign. Traditional Indian calendrical algorithms describe how solar motion, sunrise conventions, and calendrical rules determine dates [2]. Nepal Sambat has its own lunisolar structure and computational literature [3]. The target here is the solar month sequence of Nepal's civil Bikram Sambat calendar.

An ephemeris supplies solar positions over time. With an ayanamsha specifying the sidereal reference, those positions locate the sign crossing. The civil assignment rule then places that event on a date, which can be checked against the published month start.

Several combinations of physical calculations and civil rules can produce the same published date. Conversely, a change within either layer can move a sensitive boundary. This creates an identification problem: fitting published starts determines how a model reproduces the observed calendar, while attributing the fit to a particular institutional rule requires evidence about that rule.

The v7 feature is the ingress minute within the Nepal civil day, with a separate classifier for each month. Its location convention is Nepal Standard Time. The selected civil model uses month identity and clock time; sunrise calculations and latitude-dependent features belong to other research components.

### 2.2 Boundaries, lengths, and an anchor

For BS year $Y$, define thirteen civil-day ordinals,

$$
B_Y=(b_{Y,1},\ldots,b_{Y,13}),
$$

where the first twelve entries start its months and the final entry starts Baishakh of $Y+1$. Then

$$
L_{Y,m}=b_{Y,m+1}-b_{Y,m}, \qquad m=1,\ldots,12.
\tag{1}
$$

The implemented acceptance constraints are

$$
L_{Y,m}\in\{29,30,31,32\},
\qquad
\sum_{m=1}^{12}L_{Y,m}\in\{365,366\}.
\tag{2}
$$

These conditions define the release's permitted calendar structure. They are explicit modeling assumptions for the covered civil-calendar regime.

A complete length vector determines relative starts. Absolute conversion additionally needs the Gregorian date of Baishakh 1:

$$
b_{Y,m}=b_{Y,1}+\sum_{i=1}^{m-1}L_{Y,i}.
\tag{3}
$$

This distinction matters throughout the evaluation. The implementation predicts month starts internally. The frozen public commitment preserves month lengths and the annual total. Its locked prospective score therefore evaluates the length vector.

### 2.3 How a boundary error moves through a calendar

Let the forecast error at boundary $m$ be

$$
e_m=\widehat b_{Y,m}-b_{Y,m}.
$$

Subtracting the observed and predicted versions of Equation (1) gives

$$
\widehat L_{Y,m}-L_{Y,m}=e_{m+1}-e_m.
\tag{4}
$$

An isolated internal boundary shifted by one day changes both adjacent lengths. Moving Shrawan's start one day early reduces Ashadh by one day and increases Shrawan by one day. The following boundary restores the date alignment.

Summing Equation (4) yields

$$
\sum_{m=1}^{12}(\widehat L_{Y,m}-L_{Y,m})=e_{13}-e_1.
\tag{5}
$$

Thus an annual-total check sees the difference between the endpoint errors. Every internal boundary error cancels from that sum.

A uniform shift illustrates another consequence. If all thirteen predicted boundaries share the same offset $c$, each month-length error equals zero. A perfect length score is compatible with a displaced Gregorian anchor.

Equations (4) and (5) are elementary consequences of adjacent differencing. Here they determine what the study must measure. Length accuracy describes the annual pattern, boundary accuracy describes date placement, and an anchor observation locates the pattern on the Gregorian calendar. Each answers a distinct operational question.

## 3. Historical evidence and its limits

### 3.1 The corpus used by the model

The reference training range extends from BS 2000 through the chosen cutoff. At the public BS 2083 cutoff, this covers 84 annual rows, or 1,008 nominal month observations. Source labels distinguish repository reference tables, approved-publication material, and rows classified as official.

The corpus loader begins with the canonical BS table and overlays an eligible CSV. It selects a private corpus when that file exists, then a legacy corpus location, then the public six-year file. For the ordinary v7 training path, Gregorian month starts come from the canonical BS conversion function. Reproduction therefore depends on the resolved corpus, canonical table, and date anchors together.

The authority stream applies a source filter to this corpus. Its eligible rows carry both the source type *official_verified* and verification status *verified*. Because the reference stream also accepts those rows, the streams overlap. Their separation expresses a weighting policy for source classes.

That overlap is consequential. Agreement between the streams can reflect a shared observation or shared transcription. The interpretation of their joint support must account for that dependence.

### 3.2 What the public provenance record establishes

The public evaluation CSV contains BS 2078-2083. All six rows carry official labels. The accompanying acquisition register gives the documentary status:

| Evidence item | Recorded state |
|---|---|
| BS 2078-2083 structured values | Six annual rows in the public development corpus |
| BS 2082 table calendar | Direct Department of Information and Broadcasting source attached to the row |
| BS 2080 and BS 2083 annual artifacts | Sources identified and hashed in the acquisition register |
| BS 2078, BS 2079, BS 2081 direct annual provenance | Recovery and promotion pending in that register |
| Completed two-reviewer full-year extractions | Zero recorded in the acquisition register |

Five CSV rows retain the generic source reference *structured_official_repo_artifact*. The register adds source discoveries for two of those years. This distinction explains how artifact acquisition can progress while the evaluation rows still await full source linkage.

Accordingly, this paper calls the benchmark an *official-labeled development corpus*. The phrase describes its current evidentiary state. Direct annual publication, raw-file capture, page-level extraction, and reviewer records are the conditions for upgrading the provenance claim.

Earlier research material also identifies archive-preserved Panchangas. An archival copy can provide useful historical evidence when its edition, approval statement, relevant pages, and extraction record are available. Discovery, transcription, and acceptance are separate events. A count of discovered documents measures acquisition activity; accepted observations require completed review.

### 3.3 Source dependence and delayed publication

A government PDF, an approved printed Panchanga, a public BS-AD dateline, and a software table each provide a different kind of observation. A dateline can corroborate one correspondence. A complete annual calendar can establish twelve lengths and, where displayed, their absolute starts. Repeated copies of one table preserve a single source lineage.

Publication time is also part of the data. For a historical replay, BS year order supplies the current training cutoff. A fully reconstructed forecast origin would additionally require evidence of when each publication, correction, and transcription became available. The present historical study uses the current curated corpus to recreate earlier prediction windows.

Newly recovered historical records can strengthen the provenance of those windows. Their recovery date alone leaves their evaluation role retrospective, especially when the same values already appeared in the reference table.

## 4. Forecasting method

The selected implementation is *parva_authority_aware_solar_civil_v7*. It uses deterministic classifiers and weighted votes. The term *tower* in repository identifiers denotes one source-filtered stream of rule outputs.

### 4.1 Ingress features

For sidereal solar longitude $\lambda_s(t)$ and sign index $k$, the target is $30k$ degrees. The solver uses the wrapped residual

$$
f_k(t)=((\lambda_s(t)-30k+180)\bmod360)-180.
\tag{6}
$$

It starts a search near the expected Gregorian ingress month, brackets a crossing with daily steps over a 40-day horizon, and applies a Brent-style root finder. Brent's method combines interpolation with bracketing [4]. The implementation sets a 30-second termination tolerance and a ceiling of 60 iterations.

The selected sidereal mode is Lahiri. The event time is expressed in UTC and Nepal Standard Time. For each target year, the pipeline obtains the twelve relevant sign crossings and the following Baishakh crossing.

The solver tolerance concerns its numerical search interval. Calendar-date accuracy also depends on the longitude calculation, time-scale conversion, reference frame, civil rule, and source labels. The execution evidence for the astronomy adapter is examined in Section 6.

### 4.2 Historical labels

For a historical published start $b_{y,m}$, choose the corresponding ingress and let $d_{y,m}$ be the Nepal civil date containing that event. The assignment label is

$$
z_{y,m}=b_{y,m}-d_{y,m}.
\tag{7}
$$

The training routine retains labels in $\{0,1\}$: same-day and next-day assignment. Observations outside this candidate set are omitted by the implementation. A subsequent evaluation should report those exclusions by year, month, and source because they describe where the model's assumed decision space fits the data.

The predictor's feature is

$$
x_{y,m}=60h_{y,m}+q_{y,m},
\tag{8}
$$

with $h$ and $q$ denoting hour and minute. Seconds are discarded for the stored feature. Each month has its own sample set.

The binary label absorbs every difference between the chosen astronomical model and the published start. It can encode civil convention, ephemeris approximation, transcription, or their combined effect. Its interpretation is an empirical date offset.

### 4.3 Civil assignment rules

The nearest-neighbour rule searches the preceding 36 years for the same month. It takes three observations with minimum absolute clock-minute distance and assigns the majority label. Recency resolves equal distances. Sparse histories expand to all eligible prior rows; an empty history delegates to a cutoff rule. This is an application of nearest-neighbour classification [5].

The recent-cutoff rule considers a 24-year slice. It searches integer minutes from 0 through 1,439 for a threshold that minimizes same-day and next-day classification errors. Samples at or before the threshold receive the same-day label. An eight-observation minimum controls use of the recent slice; sparse samples use the full eligible history. Error ties use proximity to noon.

The full-history cutoff applies the same search to the complete eligible training window.

These parameters define the released method:

| Parameter | v7 value |
|---|---|
| Neighbours | 3 |
| Recent neighbour window | 36 years |
| Recent cutoff window | 24 years |
| Sparse cutoff threshold | 8 observations per month |
| Authority-stream activation | 4 eligible annual rows |
| Total weight per active stream | 1.0 |
| Civil assignment candidates | Same day, next day |
| Month-length candidates | 29, 30, 31, 32 days |

The learned cutoffs belong to this feature representation and training sample. Historical agreement gives them predictive meaning. A documented institutional rule would provide a separate basis for procedural interpretation.

### 4.4 Rule selection and the production branch

For most training windows, the implementation scores each rule by exact month-length agreement over eligible training rows. The cutoff estimates use that same window. These scores are internal weighting statistics.

The public reference configuration has an explicit fixed branch: BS 2000-2083 under the broad reference policy receives scores 0.99 for nearest-neighbour, 0.94 for recent cutoff, and 0.90 for full-history cutoff. The selection rule retains nearest-neighbour alone when its score reaches 0.98 and its lead reaches 0.03. Thus the fixed production branch selects that single reference rule.

Other windows compute the scores through the rule-scoring routine. The selected rules then retain their weights within the stream. This distinction belongs in the method definition because the public forecast's reference-rule selection depends on fixed constants.

The authority stream activates when four earlier official-labeled years are eligible. At the BS 2084 cutoff it has six such years. Each active stream receives total weight 1.0 after its internal weights are normalized. With both streams active, total vote mass is 2.0.

Equal stream mass expresses the model's source policy. The four-year activation threshold and fixed reference scores are design choices inherited from model development. The prospective evaluation tests the resulting fixed procedure as a whole.

### 4.5 Voting on boundaries

Let $R$ be the active rule outputs and $w_r$ the normalized weight of rule $r$. Each output supplies thirteen candidate boundaries. For candidate date $d$ at position $j$,

$$
S_j(d)=\sum_{r\in R}w_r\,\mathbf{1}[b_{r,j}=d].
\tag{9}
$$

The selected date maximizes total support. Numerical ties use authority-stream support, then reference-stream support, then chronological date order. The boundary audit retains candidate dates, support by stream, and voter identities.

The selected boundaries yield lengths through Equation (1). The unified predictor checks Equation (2) and raises an error for a sequence outside those constraints. This makes structural validity an explicit condition of its output.

### 4.6 Sequence decoding and the published record

The public snapshot builder applies a further dynamic program to the month-length candidates. Candidate weights combine rule support with the selected length's heuristic confidence, followed by normalization. Alternatives survive the support threshold of 0.02; the current selected value remains eligible. The decoder maximizes the sum of log candidate weights over paths totaling 365 or 366 days.

This objective is a computational scoring function. Its inputs have model-support semantics. A joint probability interpretation would require a fitted dependence model.

The recorded BS 2084 run has a 365-day total and zero decoder adjustments. Its published point vector therefore preserves the boundary-derived lengths. The builder then stores a compact annual result for the public API.

The internal boundary audit and the compact snapshot have different contents. Absolute starts and complete voter traces live in the research output. The year commitment locks the month lengths and annual total; the full snapshot hash covers its additional public fields.

## 5. Development evaluation

### 5.1 Chronological windows

The recorded rolling evaluation uses one target year per run. Its source filter for scoring accepts official-labeled rows. Training ends in the year immediately preceding the target:

| Target BS year | Training cutoff | Authority stream | Exact month lengths |
|---:|---:|---|---:|
| 2078 | 2077 | Inactive | 12/12 |
| 2079 | 2078 | Inactive | 12/12 |
| 2080 | 2079 | Inactive | 12/12 |
| 2081 | 2080 | Inactive | 12/12 |
| 2082 | 2081 | Active | 12/12 |
| 2083 | 2082 | Active | 12/12 |
| Total | | | 72/72 |

These figures come from the archived unified rolling-validation artifact. The selected-model record and freeze manifest preserve the same aggregate result. This manuscript revision checked their consistency and ran the freeze verifier.

The result establishes agreement with six annual development vectors under the reported training windows. Each outer prediction excludes its target-year and future-year training rows. Model design, rule selection, and source curation had already drawn on this historical period, including the BS 2082 error.

Chronological row exclusion addresses one route of information leakage. Selection around previously examined outcomes remains relevant to the scientific interpretation. Kapoor and Narayanan discuss the broader reproducibility risks created by leakage in machine-learning studies [6]. Here the evidence is best read as a historical development result with a fixed prospective test attached.

### 5.2 The BS 2082 diagnostic

The retained v7 diagnosis records a Karka ingress at approximately 17:48 Nepal time on 16 July 2025. The timing is a stored pipeline result with the astronomy-attribution issue described in Section 6.

For the Shrawan boundary, training through BS 2081 produced these votes:

| Candidate start | Reference support | Authority support | Total support |
|---|---:|---:|---:|
| 16 July 2025 | 0.681235 | 0.276193 | 0.957428 |
| 17 July 2025 | 0.318765 | 0.723806 | 1.042571 |

The reconciler selected 17 July. Displayed vote totals reflect six-decimal rounding. The resulting adjacent lengths are Ashadh 32 and Shrawan 31.

The displayed votes also permit an analytical sensitivity calculation. Let $W_A$ and $W_R$ scale the authority and reference streams. The support advantage of 17 July is approximately

$$
\Delta(W_A,W_R)=0.447613W_A-0.362470W_R.
$$

Equal weights give $\Delta=0.085143$. The decision switches near $W_A/W_R=0.8098$; the exact tie follows the authority rule. These values follow directly from the rounded archived votes.

The correction is therefore attributable to an explicit source-weighting decision in this case. Its success across a new calendar remains an empirical question. A controlled ablation can test the weighting policy at preserved forecast origins.

### 5.3 What the historical score measures

The 72 monthly outcomes share annual boundaries, overlapping training windows, and source lineages. A calculation that treats them as 72 independent Bernoulli trials would assign an unjustified sampling model to the result.

The current evidence also contains several historical benchmark generations. Their calibration state and model names vary. This revision reports the unified v7 record directly and treats older scores as development history. A reproducible comparative experiment requires one specified corpus, one execution environment, consistent forecast origins, and preserved outputs for every method.

Absolute-date evaluation remains separate. The month-length benchmark and the frozen truth schema use twelve integers. Equation (3) shows the additional anchor evidence needed for conversion accuracy. A supplementary boundary study should preserve thirteen predicted starts before acquiring its outcome and score their signed errors against reviewed Gregorian dates.

## 6. Astronomy execution and uncertainty

### 6.1 Intended ephemeris and observed execution

The freeze names JPL DE440 and records the expected kernel digest. DE440 is a numerical planetary and lunar ephemeris fitted to ground and spacecraft observations [7]. In v7, the adapter configures a local kernel path, requests JPL flags from Swiss Ephemeris, and assigns the label *jpl_de440* to its output.

Swiss Ephemeris returns flags identifying the calculation it actually performed. Its documentation explicitly describes fallback when the requested ephemeris is unavailable [8]. The v7 adapter reads the position and discards those returned flags.

A focused reproduction on 9 September 2026 used Swiss Ephemeris 2.10.03, the local file named *de440.bsp*, Lahiri sidereal mode, and the Sun at Julian day input corresponding to 16 July 2025, 12:00. The result was:

~~~text
requested flags:      65537
returned flags:       65604
JPL bit present:      false
Swiss file bit:       false
Moshier bit present:  true
~~~

This observation establishes fallback in that reproduced call. The provenance of the frozen event cache requires its own generation evidence, including actual returned flags. A cache label and a kernel filename express intended configuration; execution-level evidence establishes the backend that supplied the coordinates.

The paper therefore describes v7 as a solar-ingress-based civil predictor and preserves DE440 as the configured intent in the historical record. A verified DE440 execution claim awaits a corrected adapter and separately recorded regeneration.

### 6.2 Timing and resolution

The current time-scale helpers pass Julian UT through an identity conversion before the adapter calls the dynamical-time interface. That approximation belongs to the numerical method. The 30-second solver tolerance measures termination of the root search, while the full timing error budget includes the time-scale treatment.

The classifier further reduces ingress times to whole minutes. Cutoff assignment compares the event's full timestamp with a threshold at the start of a minute. This implementation detail can affect an event within the threshold minute and should remain visible in exact reproduction.

Historical samples are expressed under a common Nepal time convention. A study extending into earlier civil-time regimes should distinguish this normalized feature representation from a reconstruction of the clocks used by historical publishers.

### 6.3 Support, calibration, and review

For a length $l$ in month $m$, v7 reports the normalized weighted fraction of rule outputs that predict it:

$$
p_m(l)=
\frac{\sum_{r\in R}w_r\,\mathbf{1}[L_{r,m}=l]}
     {\sum_{r\in R}w_r}.
\tag{10}
$$

This is model support. Its numerical range allows useful summaries, including cumulative support sets. Empirical calibration asks a different question: among repeated forecasts issued with a stated probability, how often does the outcome occur? Proper scoring rules provide established tools for evaluating probabilistic forecasts [9].

The fields named *prediction_set_80* and *prediction_set_95* collect candidate lengths using cumulative model support. Their current scientific interpretation is a description of ensemble alternatives. Coverage rates remain an empirical target.

Dependence matters here. The streams overlap, the rules share inputs, and unanimous votes can preserve a common error. Multiplying monthly support values would introduce assumptions about independence and joint probability that the release has yet to estimate.

The boundary-distance diagnostic also needs precise interpretation. Cutoff rules measure distance to a learned threshold; nearest-neighbour measures distance to the nearest opposite-label precedent, with a default distance when that class is absent. The public month field takes the minimum across the active rules for its starting boundary. Month-length uncertainty involves the ending boundary as well.

In the snapshot-building path, the perturbation input is a fixed heuristic selected from boundary flags. Actual sensitivity experiments are a separate research task. The published YELLOW labels signal review under these limitations. Official published values remain the civil-calendar reference for operational adoption.

## 7. The frozen BS 2084 forecast

The v7 manifest declares a freeze time of 5 August 2026 at 10:04:41 UTC and a training cutoff of BS 2083. Its BS 2084 vector is

$$
(31,32,31,32,31,30,30,30,29,29,30,30),
$$

with a total of 365 days.

The complete month record is compact enough to inspect:

| Month | Predicted days | Candidate set stored as 95 | Support for selected length | Starting-boundary distance, minutes |
|---|---:|---|---:|---:|
| Baishakh | 31 | {31} | 1.0000 | 335 |
| Jestha | 32 | {31, 32} | 0.8543 | 333 |
| Ashadh | 31 | {31, 32} | 0.8543 | 40 |
| Shrawan | 32 | {32} | 1.0000 | 663 |
| Bhadra | 31 | {31} | 1.0000 | 149 |
| Ashwin | 30 | {30} | 1.0000 | 146 |
| Kartik | 30 | {30} | 1.0000 | 517 |
| Mangsir | 30 | {30} | 1.0000 | 585 |
| Poush | 29 | {29} | 1.0000 | 117 |
| Magh | 29 | {29, 30} | 0.6457 | 499 |
| Falgun | 30 | {29, 30} | 0.6457 | 39 |
| Chaitra | 30 | {30, 31} | 0.6457 | 334 |

All twelve public month records carry YELLOW. Ashadh, Poush, and Falgun have starting-boundary distances inside the implementation's high-risk band. Five months retain two candidate lengths in the stored 95 support set.

Poush is particularly useful to examine: its length receives unanimous model support while its starting boundary remains sensitive. The two diagnostics describe different properties. Vote agreement records what the current rules say; boundary distance records proximity to a switch in their assignment behaviour.

The annual heuristic score, 0.8214, is the arithmetic mean of the monthly heuristic confidence values. It summarizes those diagnostics. The probability that all twelve lengths are correct remains unestimated.

BS 2084 supplies a complete annual outcome once the study accepts the official publication. The current acquisition register records prospective scoring as pending. A final public release of this paper should record the actual registration date and the outcome status at that release.

## 8. Commitment and prospective evaluation

### 8.1 What is fixed

The release commits to the model identifier, source commit, public snapshot, yearly vectors, and scoring protocol. Each yearly leaf hashes a canonical JSON record containing its BS year, model and snapshot identifiers, twelve lengths, annual total, and publication status. The ordered leaves form a SHA-256 Merkle tree, with the final node duplicated at an odd-sized level.

Source-artifact hashes in the freeze verifier normalize CRLF line endings to LF. Yearly leaf hashes use sorted JSON keys, compact separators, UTF-8, and preserved Unicode. Reproduction must follow those byte conventions.

A digest establishes a content identity. Evidence that the content existed before an outcome comes from a dated external record carrying that digest. The manifest's declared timestamp is maintained within the repository itself. A DOI deposit, public registration, or independently preserved release supplies the external timestamp required for a strong prospective claim.

The conceptual role of preregistration is to state predictions and evaluation choices before outcomes are used in their assessment [10]. The protocol already defines the primary year and metrics. External registration should preserve the original artifact and state the deposit's actual date.

The freeze verifier passed during this revision. That result establishes consistency among the artifacts covered by the verifier. Full computational reproduction also requires the transitive code dependencies, resolved input tables, event cache, package versions, and actual astronomy backend.

### 8.2 Acquisition of the outcome

The accepted-truth protocol requires a later official publication, its source URL, publication and retrieval timestamps, a raw-file SHA-256, a local artifact path, and at least two reviewer identifiers.

The intended review procedure is:

1. Acquire the original calendar file and hash its raw bytes.
2. Have two reviewers independently extract the twelve month lengths and retain their separate worksheets.
3. Resolve transcription differences against the cited source pages.
4. Record the source institution, edition, coverage, dates, and approval of the final extraction.
5. Verify the freeze and run the locked scorer.

The executable scorer checks source type, an HTTP or HTTPS URL, source-file existence and hash, timestamp ordering, distinct reviewer identifiers, and calendar structure. Reviewer independence and institutional authenticity require the human evidence record. Two different strings satisfy a software field check; separate extraction records establish the review process.

The source artifact path resolves relative to the truth JSON file. Publishing the source metadata and worksheets should follow the source's redistribution conditions.

### 8.3 Fixed metrics

Let $I_m=\mathbf{1}[\widehat L_m=L_m]$. The protocol locks five measures:

$$
M=\sum_{m=1}^{12} I_m,\qquad
A=M/12,\qquad
V=\prod_{m=1}^{12} I_m,
$$

$$
E=\sum_{m=1}^{12}|\widehat L_m-L_m|,
\qquad
H=\sum_{m=1}^{12}
\mathbf{1}[\widehat L_m\ne L_m]\,
\mathbf{1}[p_m(\widehat L_m)\ge0.8].
\tag{11}
$$

Here $M$ is the exact-month count, $A$ its fraction, $V$ the exact annual-vector indicator, $E$ the sum of absolute month-length errors, and $H$ the count of incorrect selections carrying high model support.

The error total $E$ counts discrepancies in month lengths. Counting displaced Gregorian dates or affected business records requires the boundary errors from Equation (4), an anchor, and the relevant operational schedule.

The high-support metric records whether the ensemble concentrated weight on an erroneous result. The published score should retain those cases individually, along with their selected support and source pages.

### 8.4 Preserving the experiment through corrections

The identified astronomy-attribution issue belongs to the record of v7. A corrected adapter, revised time-scale treatment, new source row, or changed weighting rule defines a subsequent computational version.

The original BS 2084 forecast remains available for its locked score. A revised model can issue a separately dated forecast and state which evidence it had at that time. Both outputs then have clear identities and forecast origins.

Later revisions to an official calendar also require a policy. The scoring record should preserve the first accepted source and append a correction record with its date and reason. The original score remains part of the study history.

Supplementary absolute-boundary metrics, alternative baselines, and new sensitivity analyses should receive their own dated protocol. Their role can then be assessed alongside the original five measures.

## 9. Scientific interpretation and the next study

The empirical question is whether source-labeled historical decisions contain enough stable structure to predict future published month lengths. V7 gives that question an executable form and a fixed annual prediction.

The immediate data work begins with annual artifacts already identified in the source register. Completing their separate extractions would attach documentary evidence to the values used during development. The next corpus release should preserve that lineage and document every changed row.

The astronomy finding poses a concrete computational question: which civil assignments change when a verified ephemeris reader and explicit time-scale conversion generate the features? Answering it requires a separately versioned run with preserved backend flags and cache inputs. The original v7 output provides a fixed record of the earlier procedure.

BS 2084 will address a different question: whether the published vector agrees with the calendar accepted after its forecast origin. External timestamp evidence and reviewed publication establish that chronology. Success on the year would establish success on one annual case.

For a subsequent method study, the experiment should include a previous-year vector, a month-specific historical mode, fixed civil cutoff rules, a verified astronomical-rule implementation, and the source-stratified predictor. Every method should receive the same cutoff and eligible source material. This would estimate the value of the astronomical features and source weighting directly.

Ablations should address the source overlap, equal stream mass, four-year activation rule, fixed production scores, and sequence decoder. The target is attribution: which part of the method contributes to the forecast under controlled conditions?

Probability calibration needs its own observations and evaluation design. The repository's threshold of 528 verified month cases is an internal claim policy. A statistical sample requirement depends on annual dependence, source quality, horizon, event frequency, and the desired precision. Counting months alone leaves those choices unresolved.

There is also a limit to what historical labels can explain. A learned threshold can reproduce a published pattern while combining several physical and institutional effects. Interviews with calendar scholars, official method texts, and calculations under documented traditional conventions could make that model interpretable at the procedural level. They would also help identify changes in the calendar's governing practice.

The practical value of the present work lies in its explicit forecast, source record, and observable failure conditions. Software teams can preserve provisional assumptions and reconcile them when the calendar is published. Researchers can examine an erroneous month through its ingress feature, candidate start, rule votes, and reviewed outcome.

## 10. Conclusion

This study treats future Nepali BS month lengths as the result of predicted civil boundaries. The model links solar-ingress features to historical same-day and next-day assignments, then reconciles source-filtered rule outputs into an annual sequence.

Its recorded 72/72 result describes six development years. The revised manuscript identifies the source-review gaps and astronomy-attribution issue that govern interpretation of that result. The original BS 2084 vector remains fixed, with its artifact identities and evaluation protocol intact.

The next decisive observation is the accepted official BS 2084 calendar. It will supply twelve published month lengths against which the recorded forecast can be scored. That score, the source pages, and the boundary-level explanation of any errors should appear together.

## Data and software

The [Project Parva repository](https://github.com/dantwoashim/Project_Parva) contains the implementation and public forecast artifacts. The freeze names source commit `0591ca687b3c91918d1c7557d5033f49d41ba248`. This revision inspected checkout `cfa543f3015a13ce113780b902cd7f1f172d6f49`.

The frozen [model record](../../data/future_bs/public/selected_model_v7.json), [snapshot](../../data/future_bs/public/forecast_snapshot_v7_2084_2200.json), [manifest](../../data/future_bs/public/frozen/v7/freeze_manifest.json), [yearly commitments](../../data/future_bs/public/frozen/v7/year_commitments.json), and [evaluation protocol](../../data/future_bs/public/frozen/v7/prospective_evaluation_protocol.json) define the public study artifacts.

The [development corpus](../../data/future_bs/public/official_holdout_2078_2083.csv) and [acquisition register](../../data/future_bs/public/official_source_acquisition_register_v1.json) describe the current source evidence. The principal executable methods are the [unified predictor](../../backend/app/research/future_bs/unified_predictor.py), [civil classifier](../../backend/app/research/future_bs/solar_ingress_predictor.py), [sequence decoder](../../backend/app/research/future_bs/sequence_decoder.py), and [prospective scorer](../../scripts/future_bs/score_frozen_forecast.py).

The repository software carries an AGPL-3.0-or-later license. Third-party source documents and astronomical data retain their respective terms.

## Author and AI assistance

Prabin Ghimire maintains Project Parva. Generative AI tools assisted with literature discovery, source-code inspection, drafting, and revision through OpenAI Codex in August and September 2026. This disclosure describes the preparation of the manuscript. The planned independent calendar extractions remain a separate human review stage.

## References

[1] Nepal Panchanga Nirnayak Bikas Samiti. *Vigyapti* [Notice concerning Panchanga preparation for BS 2083]. Dated 5 Falgun 2082. Accessed 9 September 2026. [Official notice](https://npns.gov.np/content/13/press-release-20251216/).

[2] Dershowitz, N., and Reingold, E. M. (2011). Indian calendrical calculations. In *Ancient Indian Leaps into Mathematics*. Birkhauser. [doi:10.1007/978-0-8176-4695-0_1](https://doi.org/10.1007/978-0-8176-4695-0_1).

[3] Ranjitkar, S. *Nepal Sambat Algorithm: A Scientific Dissection*. Spiralogics, undated working paper. [Author manuscript](https://nsapi.spiralogics.net/nsalgorithm.pdf).

[4] Brent, R. P. (1971). An algorithm with guaranteed convergence for finding a zero of a function. *The Computer Journal*, 14(4), 422-425. [doi:10.1093/comjnl/14.4.422](https://doi.org/10.1093/comjnl/14.4.422).

[5] Cover, T. M., and Hart, P. E. (1967). Nearest neighbor pattern classification. *IEEE Transactions on Information Theory*, 13(1), 21-27. [doi:10.1109/TIT.1967.1053964](https://doi.org/10.1109/TIT.1967.1053964).

[6] Kapoor, S., and Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns*, 4(9), 100804. [doi:10.1016/j.patter.2023.100804](https://doi.org/10.1016/j.patter.2023.100804).

[7] Park, R. S., Folkner, W. M., Williams, J. G., and Boggs, D. H. (2021). The JPL planetary and lunar ephemerides DE440 and DE441. *The Astronomical Journal*, 161, 105. [doi:10.3847/1538-3881/abd414](https://doi.org/10.3847/1538-3881/abd414). [NASA-hosted paper](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440_and_de441.pdf).

[8] Astrodienst. *Swiss Ephemeris programming interface*. Sections on calculation time scales and returned calculation flags. Accessed 9 September 2026. [Official documentation](https://www.astro.com/swisseph/swephprg.htm).

[9] Gneiting, T., and Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359-378. [doi:10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437). [Author manuscript](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf).

[10] Nosek, B. A., Ebersole, C. R., DeHaven, A. C., and Mellor, D. T. (2018). The preregistration revolution. *Proceedings of the National Academy of Sciences*, 115(11), 2600-2606. [doi:10.1073/pnas.1708274114](https://doi.org/10.1073/pnas.1708274114).

## Appendix A. Fixed identities

~~~json
{
  "freeze_id": "parva_future_bs_v7_2026-08-05",
  "declared_recorded_at": "2026-08-05T10:04:41Z",
  "model_id": "parva_authority_aware_solar_civil_v7",
  "training_cutoff_bs_year": 2083,
  "bs_year": 2084,
  "month_lengths": [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
  "year_total_days": 365,
  "publication_status": "computed_prediction_not_official",
  "forecast_leaf_sha256": "sha256:6364a905bb3626fde54df8b3fbd38cd5a758325bb1249eac6cdfe53ccfb94e42",
  "snapshot_portable_sha256": "sha256:b02797b5074322e0856187daf3eb784142e8778adc031bcfc7b46ce0006112d9",
  "year_merkle_root": "sha256:5f27afa2349e0e2ce20e97d31a0b5715eeec64c2e8d43d2a70e914fd2e377206"
}
~~~

The declared timestamp reproduces the repository field. The paper's external registration should carry its own timestamp and a link to these identities.

## Appendix B. Reproduction

From the repository root, verify the committed artifacts:

~~~bash
python scripts/future_bs/freeze_public_v7.py --check
~~~

After an official calendar passes extraction and source review:

~~~bash
python scripts/future_bs/score_frozen_forecast.py \
  --truth <reviewed-official-truth.json> \
  --output <prospective-score.json>
~~~

Run the freeze verification immediately before scoring. The scorer's annual commitment check and the full freeze check cover different parts of the record.

The following diagnostic reproduces the astronomy flag observation in a separate Python process. Its Julian-day input deliberately matches the adapter call being examined.

~~~python
from pathlib import Path
import swisseph as swe

kernel = Path("data/ephemeris/jpl/de440.bsp").resolve()
swe.set_ephe_path(str(kernel.parent))
swe.set_jpl_file(kernel.name)
swe.set_sid_mode(swe.SIDM_LAHIRI)

requested = swe.FLG_JPLEPH | swe.FLG_SIDEREAL
position, actual = swe.calc(
    swe.julday(2025, 7, 16, 12),
    swe.SUN,
    requested,
)

print({
    "swisseph_version": swe.version,
    "requested_flags": requested,
    "returned_flags": actual,
    "jpl_used": bool(actual & swe.FLG_JPLEPH),
    "swiss_used": bool(actual & swe.FLG_SWIEPH),
    "moshier_used": bool(actual & swe.FLG_MOSEPH),
    "longitude": position[0],
})
~~~

## Appendix C. Supplementary boundary evaluation

A future protocol can extend the length-vector study by preserving thirteen predicted Gregorian starts and a reviewed annual anchor. For $n$ unique scored boundaries, useful summaries are

$$
\mathrm{MAE}_B=\frac{1}{n}\sum_{j=1}^{n}|\widehat b_j-b_j|,
\qquad
\mathrm{Bias}_B=\frac{1}{n}\sum_{j=1}^{n}(\widehat b_j-b_j),
$$

together with exact-boundary count and the complete sequence of signed errors.

Shared boundaries between adjacent years should appear once in an aggregate boundary score. Within-year reports can retain all thirteen positions for diagnosis. The published v7 protocol continues to use its five locked month-length measures; these supplementary measures define a separate extension.
