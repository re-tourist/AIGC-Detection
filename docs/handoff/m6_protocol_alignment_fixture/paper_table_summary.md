# M6 BR-Gen-style Evaluation Protocol Alignment Summary

- Current readout is image-level localized sensitivity reporting.
- Current evidence comes from the restricted pilot diagnostic pipeline.
- This is not a full localization benchmark.
- Evaluation scope: `restricted_pilot`
- Legacy threshold: `0.5`
- Paper-style threshold: `0.5`

## Overall Summary
| Slice | Accuracy | AUROC | F1@paper | Recall@50 | Real R@50 | IoU | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| overall | 0.800000 | 1.000000 | 0.750000 | 0.600000 | 1.000000 | N/A (deferred) | ok |

## Clean vs Degraded
| Slice | Accuracy | AUROC | F1@paper | Recall@50 | Real R@50 | IoU | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| clean | 0.833333 | 1.000000 | 0.800000 | 0.666667 | 1.000000 | N/A (deferred) | ok |
| degraded | 0.791667 | 1.000000 | 0.736842 | 0.583333 | 1.000000 | N/A (deferred) | ok |

## Split A: GAN / Diffusion
| Slice | Accuracy | AUROC | F1@paper | Recall@50 | Real R@50 | IoU | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| GAN | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | N/A (deferred) | ok |
| Diffusion | 0.800000 | 1.000000 | 0.666667 | 0.500000 | 1.000000 | N/A (deferred) | ok |

## Split B: Background / Stuff
| Slice | Accuracy | AUROC | F1@paper | Recall@50 | Real R@50 | IoU | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| background | 0.800000 | 1.000000 | 0.666667 | 0.500000 | 1.000000 | N/A (deferred) | ok |
| stuff | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | N/A (deferred) | ok |

## Area Bins
| Slice | Accuracy | AUROC | F1@paper | Recall@50 | Real R@50 | IoU | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| small | 0.750000 | 1.000000 | 0.000000 | 0.000000 | 1.000000 | N/A (deferred) | ok |
| medium | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | N/A (deferred) | ok |
| large | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | N/A (deferred) | ok |

## Degradation Detail
| Slice | Accuracy | AUROC | F1@paper | Recall@50 | Real R@50 | IoU | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| clean | 0.833333 | 1.000000 | 0.800000 | 0.666667 | 1.000000 | N/A (deferred) | ok |
| jpeg | 0.833333 | 1.000000 | 0.800000 | 0.666667 | 1.000000 | N/A (deferred) | ok |
| resize | 0.833333 | 1.000000 | 0.800000 | 0.666667 | 1.000000 | N/A (deferred) | ok |
| blur | 0.833333 | 1.000000 | 0.800000 | 0.666667 | 1.000000 | N/A (deferred) | ok |
| crop | 0.666667 | 1.000000 | 0.500000 | 0.333333 | 1.000000 | N/A (deferred) | ok |

## Alignment and Deferred Notes
- IoU: `N/A (deferred)` because IoU remains deferred because the repo does not expose a stable mask-prediction path or a frozen localization evaluation contract for paper-comparable reporting.
- Threshold contract: paper_style_threshold=0.5 is a repo-frozen M6 alignment contract used to construct BR-Gen-style Recall@50 reporting. It is not claimed as a reconstruction of unpublished paper implementation details.
- repo_frozen_alignment_bins: `{'small_lt': 0.05, 'medium_gte': 0.05, 'medium_lt': 0.2, 'large_gte': 0.2}`
- Excluded Split A counts: `{'unknown_generator_count': 0, 'unsupported_generator_count': 0, 'excluded_from_split_a_count': 0, 'excluded_generator_ids': []}`
- Partially aligned: generator_family is derived from canonicalized generator_id rather than stored as raw manifest metadata.
- Partially aligned: area_bin uses repo_frozen_alignment_bins and aligns the paper naming grammar only.
- Partially aligned: Conditioned slices use the repo's clean-shared-negative contract instead of claiming the paper's original benchmark pairing.
- Partially aligned: The restricted pilot remains diagnostic evidence and is not promoted to a formal benchmark claim.
- Deferred: IoU (IoU remains deferred because the repo does not expose a stable mask-prediction path or a frozen localization evaluation contract for paper-comparable reporting.)
