# gen_paper_text — test_idea

> Phase: `invention_loop` · round 2 · `gen_paper_text`
> Run: `run_q27XJGeAT3TE` — When Two Classifiers Disagree, Does the Direction Tell You Which One Is Right?
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_paper_text` (sdk_openhands_agent)

### [1] SYSTEM-USER prompt · 2026-09-10 07:22:11 UTC

````
<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for related-work positioning and how this field frames a genuinely novel contribution.

- **aii-handbook-auto-computational-linguistics** — Field handbook for computational linguistics as a SCIENCE of language — grammaticality and minimal pairs (BLiMP), surprisal versus reading times, linguistic structure in LMs, annotator disagreement an
- **aii-handbook-auto-mechanistic-interpretability** — Field handbook for mechanistic interpretability of neural networks — circuit discovery, activation and attribution patching, sparse autoencoders, transcoders, attribution graphs, steering vectors, pro
- **aii-handbook-auto-multi-agent-llm-systems** — Field handbook for multi-agent LLM systems (MAS) — orchestration topology, multi-agent debate, mixture-of-agents, verifier and critic agents, inter-agent protocols (MCP/A2A), failure attribution and s
- **aii-handbook-auto-neurosymbolic** — Field handbook for neuro-symbolic AI — text-to-logic autoformalization (NL to FOL), LLM-plus-solver and prover pipelines (Prolog, ASP, SMT), probabilistic-differentiable NeSy (DeepProbLog, Scallop), r
</available_domain_handbooks>
<writing_register>
Write in the register of the field's best papers (the passages you collect in the STYLE EXEMPLARS todo), not in the register of a language
model. Four things are measured on the finished draft, and a draft outside them is sent back with
the numbers:
- Never use: delve, underscore, showcase, intricate, pivotal, realm, commendable, meticulous, tapestry, garner, multifaceted, it is worth noting, plays a crucial role, not only ... but also. These are 10 to 30 times more frequent in machine-written abstracts than in
  human ones, and reviewers read them as such.
- Em dashes: at most 3 per 1,000 words. Use a comma, a colon or a full stop.
- Sentence rhythm: mix short and long sentences. An interquartile range of sentence length under
  8 words reads as machine-written.
- Hedging: at most 15 hedges (may, likely, suggests, appears) per 1,000
  words. State what the evidence supports plainly; hedge where it is thin, not everywhere.
Style never changes substance: numbers, claims, citations and figure markers stay exactly as the
evidence gives them. The user's original request (delivered as a separate message) overrides all
of this wherever the two conflict.
</writing_register>
<previous_paper>
STARTING POINT: This is your paper draft from the previous iteration.

# The Disagreement Asymmetry Oracle: Testing Whether Direction Predicts Correctness

## Abstract

When two classifiers disagree on a prediction, practitioners typically fall back on confidence scores or majority voting to decide which model to trust. We investigate whether the *direction* of disagreement carries a systematic signal: does knowing that a simple model predicts the majority class while a complex model predicts the minority class tell us which one is correct? This question follows from the bias-variance tradeoff, which predicts that simple models err toward the mode while complex models err toward noise. We test this hypothesis across 240 configurations on two sentiment datasets, varying sample size and class imbalance. We find no evidence for the directional asymmetry: the directional rule achieves 42.4% accuracy on disagreement samples, below chance and below both the confidence-based baseline and a trust-score proxy. No configuration reaches statistical significance. The negative result suggests that the bias-variance asymmetry does not manifest as a usable signal in inter-model disagreement on sentiment data. We release the full experimental suite for future testing on other domains.




# Introduction

Sentiment classification on small datasets is unstable. Models overfit, benchmarks contain label noise, and it is unclear which model to trust when they disagree. When a logistic regression and a random forest produce different labels on the same sentence, the standard response is to pick the prediction with higher confidence or to fall back to majority voting. Both approaches measure the *magnitude* of disagreement but ignore its *direction*.

The direction of disagreement should matter. A simple model with strong inductive bias toward the majority class should be reliable when it predicts the majority and unreliable when it predicts the minority. A complex model that captures genuine minority-class signals but overfits to noise in the majority class should be reliable on minority predictions and unreliable on majority predictions. If this intuition is correct, the pattern of disagreement between two dissimilar classifiers should systematically predict which one is right.

We formalize this intuition as the *disagreement asymmetry oracle*: a rule that trusts the simple model when it predicts the majority class and the complex model otherwise. We test this rule against three baselines: random guessing, confidence-based selection, and a trust-score proxy. We run this test across 240 configurations on SST-2 and IMDB, with sample sizes from 100 to 1000 and class imbalance ratios from 1:1 to 2:1.

We find that the directional rule does not work. It achieves accuracy below the 50% chance level and substantially below the confidence baseline. The result holds across both datasets, all sample sizes, and all imbalance ratios. No configuration reaches statistical significance.

Our contribution is threefold. First, we formalize and test a hypothesis about disagreement direction that, to our knowledge, has not been studied before. Second, we provide a thorough negative result that rules out a natural intuition about the bias-variance tradeoff. Third, we release an experimental suite that can be reused to test this hypothesis on other domains and model families.

The rest of the paper proceeds as follows. Section 2 reviews related work on trust scores, ensemble diversity, and label noise detection. Section 3 describes our experimental setup. Section 4 presents the results. Section 5 discusses why the hypothesis failed and what the negative result implies. Section 6 concludes.

[FIGURE:fig1]

**Summary of Contributions**

- We formalize the *disagreement asymmetry oracle*, a rule that uses the direction of inter-model disagreement to predict which classifier is correct.
- We test the oracle across 240 configurations on two sentiment datasets and find no evidence that disagreement direction predicts correctness.
- We show that confidence-based selection outperforms the directional rule by 11.8 percentage points, confirming that magnitude-based approaches remain the practical default.




# Related Work

**Trust scores.** Jiang et al. [1] propose the trust score, which measures agreement between a classifier and a modified nearest-neighbor classifier. High trust scores identify correctly classified examples with high precision, outperforming the classifier's own confidence score. The trust score measures *agreement magnitude*, not disagreement direction. Our work tests whether the direction of disagreement between two *dissimilar* classifiers (not a classifier and its nearest-neighbor proxy) carries predictive signal.

**Ensemble diversity.** The ensemble learning literature studies how diversity among members improves performance [2, 3]. Kuncheva and Whitaker [2] introduce the Q-statistic and correlation coefficient as measures of pairwise disagreement. Wood et al. [3] show that diversity is a hidden dimension in the bias-variance-diversity decomposition. None of this work examines whether the *direction* of individual disagreements predicts correctness.

**Dynamic ensemble selection.** Dynamic classifier selection methods choose the best model for each test instance based on local accuracy estimates [4, 5]. These methods use a separate oracle set to estimate each model's competence region. Our approach asks whether the disagreement pattern itself, without any oracle set, encodes information about correctness.

**Label noise detection.** Methods like FINE [6] use loss patterns and representation dynamics to detect noisy labels. These approaches rely on a single model's training dynamics, not on inter-model disagreement. Our work asks whether disagreement between two models trained on the same data provides a cheaper signal for label quality.

**Active learning disagreement.** Active learning uses disagreement between models to select informative samples for labeling [7]. Vote entropy, consensus entropy, and max disagreement measure how much models disagree, not which one is right. Our work tests the complementary question: when models disagree, can we predict the correct label from the pattern of disagreement?

**Learning from disagreement.** Uma et al. [8] survey methods for learning from human annotator disagreement. The focus is on soft labels and crowdsourcing, not on inter-model disagreement as a diagnostic tool.

To our knowledge, no prior work studies the direction of inter-model disagreement as a systematic predictor of correctness.




# Methods

## Models

We train two classifiers with different inductive biases on the same training data:

1. **Simple model**: TF-IDF features (unigrams and bigrams, max 10,000 features) with logistic regression ($L_2$ regularization, max 1000 iterations). This model has a linear decision boundary and strong bias toward the majority class.

2. **Complex model**: Character n-gram features (3- to 5-grams, max 20,000 features) with a random forest (100 trees). This model can fit non-linear decision boundaries and is more sensitive to minority-class patterns but more prone to overfitting.

## Datasets

We use two binary sentiment datasets:

- **SST-2** [9]: 67,349 movie review sentences with binary sentiment labels (44% negative, 56% positive).
- **IMDB** [10]: 25,000 movie reviews with balanced sentiment labels (50/50).

## Experimental Protocol

For each dataset, we create subsamples at four sizes (100, 200, 500, 1000) and three class imbalance ratios (1.0, 1.5, 2.0), where the ratio is majority-to-minority. Each configuration is repeated with 10 random seeds, giving 240 total configurations (4 sizes × 3 ratios × 10 seeds × 2 datasets).

Each subsample is split 80/20 into train and test. Both models are trained on the training split. On the test set, we identify all samples where the two models disagree and evaluate the following methods:

**Directional rule**: If the simple model predicts the majority class, trust the simple model. Otherwise, trust the complex model.

**Confidence baseline**: Trust the model with higher predicted probability for its prediction.

**Trust-score proxy**: Use k-nearest-neighbor agreement in TF-IDF space as a proxy for the trust score of Jiang et al. [1].

**Random baseline**: Randomly select one of the two models' predictions.

## Statistical Testing

For each configuration, we test whether the directional rule's accuracy exceeds 50% using a binomial test. We report the mean p-value across the 10 seeds for each (dataset, size, imbalance) combination.




# Results

## Overall Performance

Across all 24 configurations, the directional rule achieves a mean accuracy of 42.4%, below the 50% chance level. The confidence baseline achieves 54.2%, and the trust-score proxy achieves 53.9%. The random baseline achieves 47.4%.

[FIGURE:fig2]

The directional rule underperforms chance by 7.6 percentage points on average. This is not a marginal effect: the confidence baseline outperforms the directional rule by 11.8 percentage points, and the trust-score proxy outperforms it by 11.5 percentage points.

## Per-Configuration Analysis

Table 1 shows the mean directional accuracy, confidence accuracy, trust-score accuracy, and mean p-value for each (dataset, sample size, imbalance ratio) combination.

[FIGURE:fig3]

Several patterns emerge:

1. **No configuration reaches significance.** The lowest mean p-value across all 24 configurations is 0.472 (SST-2, size 1000, balanced), far from the 0.01 threshold.

2. **The directional rule is below chance in most configurations.** Of 24 configurations, 18 show mean directional accuracy below 50%. Only 6 configurations exceed 50%, and none are statistically significant.

3. **The effect reverses under imbalance.** As class imbalance increases, the directional rule's accuracy tends to decrease. On IMDB with 2:1 imbalance and 1000 samples, the directional rule achieves only 15.8% accuracy, effectively the opposite of the predicted pattern.

4. **Confidence-based selection is robust.** The confidence baseline consistently outperforms the directional rule across all configurations, with a mean gap of 11.8 percentage points.

## Distribution of Results

Figure 4 shows the distribution of directional accuracy across all 24 configurations. The distribution is centered at 42.4% with a standard deviation of 11.2%, spanning from 15.8% to 62.5%.

[FIGURE:fig4]




# Discussion

## Why the Hypothesis Failed

The disagreement asymmetry oracle was motivated by the bias-variance tradeoff: simple models should be biased toward the majority class, and complex models should capture minority-class signals. The intuition is theoretically sound but does not translate to a usable signal in practice for several reasons.

**First**, the bias-variance tradeoff operates at the population level, not the instance level. A simple model's tendency to predict the majority class is an aggregate property, not a per-instance guarantee. On any given disagreement, the simple model may be right for reasons unrelated to its bias.

**Second**, the feature representations differ between the two models. The simple model uses word-level TF-IDF features, while the complex model uses character n-grams. Their disagreements may reflect representation differences rather than complexity differences, making the directional rule's assumption about which model is "simple" and which is "complex" ill-defined at the instance level.

**Third**, the sentiment classification task may not exhibit the kind of noise structure that the hypothesis requires. If label noise is roughly symmetric across classes, the simple model's majority-class bias does not give it an advantage on majority-class disagreements.

## What the Negative Result Means

The negative result does not imply that disagreement is uninformative. The confidence baseline achieves 54.2% accuracy, above chance, showing that the *magnitude* of disagreement (as captured by confidence scores) does carry signal. The trust-score proxy also outperforms chance at 53.9%. The direction of disagreement, however, does not.

This suggests that the bias-variance asymmetry is real but not accessible through the directional rule we tested. A more sophisticated oracle that accounts for feature representation differences, local data density, or model calibration might recover the signal.

## Limitations

Our study has several limitations. We test only two model families (logistic regression and random forest) on two sentiment datasets. The hypothesis might hold for other model pairs or other domains. The small sample sizes (100–1000) may not be sufficient to reveal the effect, though the effect should be strongest in small-sample regimes where the bias-variance tradeoff matters most. We do not test the effect of model calibration, which could change the confidence landscape and interact with the directional rule.

## Future Work

Several directions follow from this negative result. First, the hypothesis should be tested on other domains (e.g., image classification, tabular data) and with other model families (e.g., neural networks vs. linear models). Second, a more sophisticated oracle that accounts for feature representation differences might recover the signal. Third, the question of whether disagreement direction carries signal in multi-class settings remains open.




# Conclusion

We tested whether the direction of disagreement between a simple and a complex classifier predicts which model is correct on sentiment classification tasks. The hypothesis, motivated by the bias-variance tradeoff, predicts that simple models are more reliable on majority-class predictions and complex models on minority-class predictions. We find no evidence for this pattern across 240 configurations on SST-2 and IMDB. The directional rule achieves 42.4% accuracy, below chance and below both the confidence-based baseline (54.2%) and a trust-score proxy (53.9%). The negative result suggests that the bias-variance asymmetry does not manifest as a usable directional signal in inter-model disagreement on sentiment data. We release the experimental suite for future testing on other domains.

**Future work**:
- Test the hypothesis on image classification and tabular datasets.
- Investigate whether model calibration changes the disagreement landscape.
- Develop more sophisticated oracles that account for feature representation differences.
- Study whether disagreement direction carries signal in multi-class settings.




# References

[1] Jiang, H., Kim, B., Guan, M. Y., & Gupta, M. (2018). To trust or not to trust a classifier. *Advances in Neural Information Processing Systems*, 31.

[2] Kuncheva, L. I., & Whitaker, C. J. (2003). Measures of diversity in classifier ensembles and a correlation-based analysis. *Machine Learning*, 51(2), 181–207.

[3] Wood, S., et al. (2023). A unified theory of diversity in ensemble learning. *Journal of Machine Learning Research*, 24(1), 1–42.

[4] Rodriguez, J. J., Kuncheva, L. I., & Alonso, C. J. (2017). Dynamic classifier selection: Recent advances and perspectives. *Information Fusion*, 36, 124–135.

[5] Zhou, Z.-H., & Wu, J. (2018). K-nearest oracles borderline dynamic classifier ensemble selection. *International Joint Conference on Neural Networks*, 1–8.

[6] Kim, T., Ko, J., Cho, S., Choi, J., & Yun, S.-Y. (2021). FINE samples for learning with noisy labels. *Advances in Neural Information Processing Systems*, 34, 26784–26797.

[7] Danka, P. (2018). modAL: a modular active learning library for Python. *Journal of Machine Learning Research*, 19(129), 1–6.

[8] Uma, S., et al. (2021). Learning from disagreement: A survey. *Journal of Artificial Intelligence Research*, 72, 1179–1234.

[9] Socher, R., Perelygin, A., Wu, J., Chuang, J., Mangatar, C., Pang, B., & Ng, A. Y. (2013). Recursive deep models for semantic compositionality over a sentiment treebank. *Proceedings of the 2013 Conference on Empirical Methods in Natural Language Processing*, 1631–1642.

[10] Maas, A. L., Daly, R. E., Pham, P. T., Huang, D., Ng, A. Y., & Potts, C. (2011). Learning word vectors for sentiment analysis. *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics*, 142–150.

[11] Han, B., Yao, Q., Liu, T., Niu, G., Tsang, I. W., Kwok, J. T., & Sugiyama, M. (2020). A survey of label-noise representation learning: Past, present and future. *arXiv preprint arXiv:2011.04406*.

[12] Kuncheva, L. I. (2019). Diversity in machine learning. *IEEE Access*, 7, 132670–132681.

</previous_paper>

<reviewer_feedback>
STEP 1 — REVIEW: A reviewer evaluated the previous paper draft above and produced this feedback.

- [MAJOR] (methodology) The 'simple vs. complex' distinction is confounded with 'word-level vs. character-level features.' The simple model uses TF-IDF word n-grams while the complex model uses character n-grams. Their disagreements may reflect representation differences rather than complexity differences. This makes it impossible to attribute results to the bias-variance tradeoff, which is the entire motivation of the paper. The authors acknowledge this in the Discussion but do not address it experimentally.
  Action: Add a control experiment where both models use the SAME feature representation (e.g., both use TF-IDF word n-grams) but differ only in model complexity (LR vs. RF). This isolates the complexity variable and tests whether the directional asymmetry is driven by model architecture or feature representation. If the effect disappears with matched features, the original hypothesis is unsupported. If it persists, the feature confound is ruled out.
- [MAJOR] (evidence) The directional rule achieves 42.4% accuracy — 7.6 percentage points BELOW chance. This means the INVERTED rule (trust the complex model when the simple model predicts the majority class, trust the simple model otherwise) achieves 57.6% accuracy. The paper treats this as 'below chance' without exploring the inverted pattern. If the bias-variance asymmetry operates in the OPPOSITE direction of the hypothesis, this would be a significant positive finding, not a negative result. Missing this insight wastes a key discovery.
  Action: Report the accuracy of the inverted directional rule across all configurations. Analyze whether the inverted rule is statistically significant and consistent across datasets and settings. Reframe the Discussion to explore why the asymmetry might operate in reverse: simple models may be more reliable on minority-class predictions (because they rarely predict minority, so when they do, it is often correct), while complex models may overfit noise in the majority class. This transforms the paper from a negative result to a discovery about the direction of the asymmetry.
- [MAJOR] (methodology) The confidence baseline compares raw predicted probabilities from logistic regression and random forest, which are not on the same scale. Logistic regression outputs are naturally calibrated (probabilities reflect true likelihoods), while random forest outputs are typically overconfident and poorly calibrated. This makes the confidence comparison unfair and potentially inflates the confidence baseline's performance relative to the directional rule.
  Action: Calibrate both models' probabilities using Platt scaling or isotonic regression on a validation set before comparing confidence. Alternatively, replace the confidence baseline with a rule-based baseline that does not depend on probability calibration, such as always trusting the model with higher training accuracy, or a fixed priority rule. Report both calibrated and uncalibrated results to show the effect of calibration.
- [MODERATE] (methodology) The 'trust-score proxy' implemented in the code is simple k-NN majority voting in TF-IDF space, not the actual trust score from Jiang et al. 2018. The real trust score uses a modified nearest-neighbor classifier with distance-based weighting and a threshold on the agreement score. The proxy may not capture the full signal of the trust score, making the comparison incomplete.
  Action: Implement the actual trust score from Jiang et al. 2018: compute the agreement between the classifier and a modified k-NN classifier with distance-based weighting. If this is too complex, clearly label the baseline as 'k-NN majority voting' rather than 'trust-score proxy' to avoid misleading readers about what is being compared.
- [MODERATE] (scope) The study tests only one model pair (LR vs. RF) on two sentiment datasets. The hypothesis might hold for other model pairs (e.g., neural networks vs. linear models) or other domains (e.g., image classification, tabular data) where the bias-variance tradeoff manifests differently. Testing only sentiment data limits the generalizability of the conclusion.
  Action: Add at least one additional model pair (e.g., Naive Bayes vs. SVM, or a small neural network vs. LR) and one additional domain (e.g., CIFAR-10 for image classification or a tabular dataset like Credit Card Fraud). This would demonstrate whether the negative result is specific to sentiment classification or generalizes across domains.
- [MODERATE] (evidence) The paper does not report the individual accuracy of each model on the disagreement subset. Without knowing whether the simple or complex model is generally more accurate on disagreements, the directional rule's performance is hard to interpret. For example, if the simple model is 80% accurate on disagreements overall, the directional rule's 42.4% suggests it is actively harmful.
  Action: Report the per-model accuracy on the disagreement subset for each configuration. This provides context for the directional rule: if one model is consistently more accurate on disagreements, the directional rule should be compared against always trusting that model, not just against confidence-based selection.
- [MODERATE] (rigor) The statistical testing uses a binomial test against 50% chance, but the random baseline achieves 47.4% (not exactly 50%) due to the fixed random seed. The chance level should be defined relative to the random baseline or the majority-class prior on the disagreement set, not an assumed 50%. Additionally, with 24 configurations and 10 seeds each, there is a multiple-comparisons problem that is not addressed.
  Action: Define the chance level as the accuracy of the random baseline (47.4%) or the majority-class prior on the disagreement set, and test against that. Apply a multiple-comparisons correction (e.g., Bonferroni or Benjamini-Hochberg) across the 24 configurations to control the family-wise error rate. Report both uncorrected and corrected p-values.
- [MINOR] (clarity) The paper states '240 configurations' but then refers to '24 configurations' in the Results section (240 total runs = 24 unique (dataset, size, imbalance) combinations × 10 seeds). This inconsistency could confuse readers about the scope of the study.
  Action: Use consistent terminology throughout: '240 runs across 24 unique configurations (each repeated with 10 random seeds)' or similar. Clarify the distinction between unique configurations and total runs in both the Methods and Results sections.
- [MINOR] (clarity) The paper claims the directional rule is 'below chance' but does not define what 'chance' means in this context. For a binary classification problem with class imbalance, chance is not 50% — it is the accuracy of always predicting the majority class. On imbalanced disagreement sets, the chance level could be substantially different from 50%.
  Action: Define the chance baseline explicitly for each configuration based on the class distribution of the disagreement set. Report whether the directional rule is below the majority-class baseline, not just below 50%.
- [MINOR] (scope) The paper does not discuss whether the directional rule might work better with more than two models. With three or more models, the 'direction' of disagreement becomes richer (e.g., 2-vs-1 splits), and the asymmetry might be more detectable.
  Action: Add a brief discussion of how the directional rule might generalize to multi-model settings, where the pattern of disagreement (e.g., majority-vs-minority voting) could provide more signal than the binary case.
</reviewer_feedback>

<pipeline_steps>
STEP 2 — STRATEGY: The pipeline's strategy generator (gen_strat) read the reviewer feedback
and designed a new research strategy to address the critiques.

STEP 3 — PLANNING: The planner (gen_plan) turned the strategy into concrete artifact plans —
specific experiments, datasets, or research tasks to execute.

STEP 4 — EXECUTION: The executor (gen_art) ran those plans and produced the new artifacts
shown in <new_artifacts_this_iteration> below.
</pipeline_steps>

<hypothesis>
STEP 5 — HYPOTHESIS UPDATE: The hypothesis was revised based on evidence from previous iterations.

kind: hypothesis
title: Inverted Disagreement Asymmetry Oracle
hypothesis: >-
  When two dissimilar classifiers disagree on sentiment labels with matched feature representations, the direction of their
  disagreement systematically predicts which model is correct in the OPPOSITE direction of the original bias-variance intuition:
  the simpler model (e.g., logistic regression) is more likely right when it predicts the MINORITY class, while the more complex
  model (e.g., random forest) is more likely right when it predicts the MAJORITY class. This inverted asymmetry emerges because
  simple models rarely predict the minority class, so when they do, it is often correct (high precision on minority predictions),
  while complex models overfit to noise in the majority class, making their majority predictions less reliable than expected.
  The original directional rule (trust simple on majority) achieved 42.4% accuracy — its inversion achieves 57.6%, suggesting
  the asymmetry operates in reverse.
motivation: >-
  Sentiment classification on small datasets is notoriously unstable — models overfit, benchmarks are noisy, and it is unclear
  which model to trust when they disagree. Current work measures the MAGNITUDE of disagreement (e.g., trust scores, prediction
  entropy) but ignores the DIRECTION. If the direction carries a systematic signal about which model is correct, this would
  provide a free, model-agnostic diagnostic for label quality and a path to building better ensembles without additional training
  data. It also reveals a fundamental property of the bias-variance tradeoff that has not been measured: that the two sides
  of a disagreement are not symmetric.
assumptions:
- >-
  The two classifiers have sufficiently different inductive biases (e.g., linear vs. tree-based) so that their errors are
  not perfectly correlated.
- >-
  The dataset contains both genuine minority-class signals and noise that complex models overfit to.
- >-
  The majority-class bias of simple models and the minority-class sensitivity of complex models hold for sentiment data on
  small samples.
- >-
  The direction of disagreement is not purely random but reflects systematic structural properties of the data.
investigation_approach: >-
  Train two dissimilar baselines (logistic regression with TF-IDF features and a random forest with character n-gram features)
  on small sentiment datasets (e.g., subset of IMDB, SST-2, or Twitter sentiment data with 100-1000 samples). On the held-out
  test set, identify all samples where the two models disagree. For each disagreement, record: (1) which model predicts which
  class, (2) the true label, (3) the class balance of the dataset. Test whether the direction of disagreement (simple model
  says positive vs. negative) predicts correctness at a rate significantly above chance. Quantify the asymmetry as a function
  of dataset size, class imbalance, and label noise level. Compare against baselines: random guessing on disagreements, confidence-based
  selection, and the trust score method.
success_criteria: >-
  CONFIRMED: The direction of disagreement predicts the correct label with accuracy significantly above 50% (e.g., >60% on
  disagreement samples), and this effect is statistically significant (p < 0.01) across multiple datasets and random seeds.
  The asymmetry is predictable from dataset properties (class balance, noise level) and improves ensemble performance over
  voting or confidence-based selection. DISCONFIRMED: The direction of disagreement is random (accuracy ~50%), or the effect
  disappears when controlling for confidence scores, suggesting it is not a distinct signal.
related_works:
- >-
  Jiang et al. (NIPS 2018) 'To Trust Or Not To Trust A Classifier': Proposes a trust score based on agreement between a classifier
  and a nearest-neighbor classifier. Measures agreement MAGNITUDE, not disagreement DIRECTION. Does not study which model
  is correct when they disagree.
- >-
  Uma et al. (JAIR 2021) 'Learning from Disagreement: A Survey': Reviews methods for handling annotator disagreement in training
  data. Focuses on human-to-human disagreement, not inter-model disagreement direction as a diagnostic.
- >-
  Freestone et al. (2021) 'Pervasive Label Errors in Test Sets': Shows that label errors in benchmarks destabilize results.
  Does not propose using inter-model disagreement direction to detect which labels are wrong.
- >-
  Ensemble diversity literature (e.g., Kuncheva 2006): Studies how diversity among ensemble members improves performance,
  but does not examine directional asymmetry of individual disagreements.
- >-
  Label noise detection methods (e.g., FINE, MentorNet): Use model confidence and loss patterns to detect noisy labels, but
  do not leverage directional disagreement between dissimilar models as a signal.
inspiration: >-
  This hypothesis draws from three distant fields: (1) EPIDEMIOLOGY — the concept of an 'error reproduction number' analogous
  to R0, where errors propagate through similar samples; the direction of disagreement is like tracking which 'strain' of
  error is spreading. (2) ECOLOGY — Shannon diversity indices measure community structure; here, the 'community' is the set
  of model predictions, and the direction of disagreement reveals the underlying 'species' composition of the data (signal
  vs. noise). (3) STATISTICAL DECISION THEORY — the bias-variance tradeoff predicts that simple models err in one direction
  (toward the mean) and complex models in another (toward noise), creating a measurable asymmetry that has never been formalized
  as a diagnostic tool.
terms:
- term: Disagreement Asymmetry
  definition: >-
    The phenomenon where the direction of disagreement between two classifiers (Model A says class X while Model B says class
    Y, versus the reverse) carries systematic information about which prediction is correct.
- term: Inductive Bias
  definition: >-
    The set of assumptions a learning algorithm uses to predict outputs for inputs it has not encountered. Simple models (e.g.,
    logistic regression) have strong inductive biases toward linear decision boundaries; complex models (e.g., random forests)
    have weaker biases and can fit more complex patterns.
- term: Bias-Variance Tradeoff
  definition: >-
    The decomposition of prediction error into bias (error from erroneous assumptions) and variance (error from sensitivity
    to fluctuations in training data). Simple models have high bias, low variance; complex models have low bias, high variance.
- term: Trust Score
  definition: >-
    A metric proposed by Jiang et al. (2018) that measures the agreement between a classifier and a nearest-neighbor classifier
    to assess prediction reliability. It measures agreement magnitude, not disagreement direction.
- term: Disagreement Oracle
  definition: >-
    A meta-model or rule that uses the pattern of disagreement between two base classifiers to predict which classifier's
    output is correct on a given sample.
summary: >-
  When two dissimilar sentiment classifiers disagree, the direction of their disagreement systematically predicts which one
  is correct, revealing a measurable asymmetry rooted in the bias-variance tradeoff that has never been studied as a diagnostic
  tool.
_relation_rationale: >-
  Same conceptual frame, inverted directional claim based on derived evidence (42.4% → 57.6%)
_confidence_delta: decreased
_key_changes:
- >-
  INVERTED the directional prediction: simple model trusted on minority class (not majority), complex model trusted on majority
  class (not minority)
- >-
  Added requirement for MATCHED feature representations to eliminate the word-level vs. character-level confound identified
  by reviewers
- >-
  Reframed the negative result (42.4% accuracy) as evidence FOR the inverted pattern (57.6% derived accuracy)
- >-
  Added calibration control: both models must be calibrated (Platt scaling or isotonic regression) before confidence comparison
- >-
  Added per-model accuracy reporting on the disagreement subset to contextualize the directional rule
- Lowered success threshold from >60% to >55% given the 57.6% derived estimate
- Added requirement to test the inverted rule directly rather than deriving it
- >-
  Specified that the chance baseline should be the majority-class prior on the disagreement set, not 50%
- >-
  Added multiple-comparisons correction (Benjamini-Hochberg) to statistical testing
- >-
  Added requirement to test at least one additional model pair (e.g., Naive Bayes vs. SVM) to generalize beyond LR vs. RF
relation_type: evolution
</hypothesis>

<all_artifacts>
FULL EVIDENCE BASE: All 4 research artifacts across all iterations.

--- Item 1 ---
id: art_N1k1rKbMgdgf
type: dataset
title: Sentiment Datasets for Disagreement Asymmetry
summary: >-
  This artifact provides three curated sentiment classification datasets standardized to the exp_sel_data_out JSON schema,
  ready for testing the disagreement asymmetry hypothesis. The datasets span three domains: (1) SST-2 (67,349 examples): binary
  sentiment labels on movie review sentences from the Stanford Sentiment Treebank, with 44% negative / 56% positive distribution.
  (2) IMDB (25,000 examples): binary sentiment labels on full movie reviews, perfectly balanced at 50/50. (3) Twitter Financial
  News (3,365 examples): binary sentiment (bearish/bullish) on finance-related tweets, with 43% bearish / 57% bullish distribution.
  Each example contains: input (raw text), output (binary label as string '0' or '1'), and rich metadata including fold assignment
  (5-fold CV), task type, number of classes, row index, domain label, and unique example ID. Total: 95,714 examples across
  3 datasets. All datasets have verified provenance (HuggingFace Hub, established benchmarks with 100K+ downloads), clear
  documentation, and research-permissive licenses. Baseline comparison on SST-2 shows Logistic Regression (87.05% accuracy)
  outperforms Naive Bayes (85.56% accuracy) with TF-IDF features. The full_data_out.json (65MB) is under the 100MB file size
  limit. Mini (9 examples) and preview (9 truncated examples) variants are provided for quick inspection.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_q27XJGeAT3TE/3_invention_loop/iter_1/gen_art/gen_art_dataset_1
out_expected_files:
- data.py
- full_data_out.json
- preview_data_out.json
- mini_data_out.json

--- Item 2 ---
id: art_MokklmuoWzjn
type: experiment
title: Disagreement Direction Test for Sentiment
summary: >-
  This artifact implements the Disagreement Direction Test for Sentiment Classification. It trains two models — a simple TF-IDF
  + Logistic Regression and a complex character n-gram + RandomForest — on SST-2 and IMDB datasets across 240 configurations
  (4 sample sizes × 3 imbalance ratios × 10 seeds × 2 datasets). On each test set, it identifies samples where the models
  disagree and evaluates a directional rule (trust the simple model when it predicts the majority class, otherwise trust the
  complex model) against three baselines: random guessing, confidence-based selection (pick the model with higher predicted
  probability), and trust-score proxy (k-NN agreement in TF-IDF space). Statistical significance is assessed via binomial
  tests and McNemar's tests. Results: 217 of 240 configurations produced disagreements (3,711 total). Mean directional rule
  accuracy = 0.419, underperforming confidence baseline (0.544) and trust score baseline (0.531), suggesting the directional
  hypothesis does not hold on sentiment classification. The output includes per-configuration metrics, an ablation table,
  and full disagreement records in exp_gen_sol_out schema format.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_q27XJGeAT3TE/3_invention_loop/iter_1/gen_art/gen_art_experiment_1
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json

--- Item 3 ---
id: art_QDozgnSR0f0E
type: research
title: Literature Survey on Directional Disagreement
summary: >-
  Comprehensive literature survey confirming novelty of the Disagreement Asymmetry Oracle hypothesis. Searched 40+ scholarly
  and general queries across trust scores, dynamic ensemble selection, active learning disagreement measures, ensemble diversity
  theory, and human disagreement surveys. No prior work studies the DIRECTION of inter-model disagreement (Model A says X,
  Model B says Y vs. reverse) as a systematic predictor of correctness linked to bias-variance tradeoff. Identified 5 closest
  related papers (Jiang et al. 2018 trust scores, Uma et al. 2021 human disagreement survey, Wood et al. 2023 diversity theory,
  DES literature, modAL disagreement sampling), 4 potential confounds (confidence calibration, domain specificity, feature
  representation, implicit capture), 5 recommended baselines, and 8 anticipated reviewer concerns. Output includes research_out.json
  (structured findings) and research_report.md (detailed report with citations).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_q27XJGeAT3TE/3_invention_loop/iter_1/gen_art/gen_art_research_1
out_expected_files:
- research_out.json

--- Item 4 ---
id: art_E7Liy6GI1AIc
type: experiment
title: Inverted Disagreement Asymmetry Test on Sentiment Models
summary: >-
  Comprehensive experiment testing the inverted disagreement asymmetry hypothesis across 720 configurations (3 datasets x
  4 sample sizes x 3 imbalance ratios x 10 seeds x 2 model pairs). The hypothesis predicted that when dissimilar classifiers
  (LR vs RF, NB vs SVM) disagree on sentiment classification, trusting the simpler model when it predicts the minority class
  and the complex model when it predicts the majority class would systematically outperform random guessing. Results DISCONFIRM
  the hypothesis: inverted rule accuracy was 49.0% (near random), identical to the original rule (49.0%) and majority prior
  (49.0%). The confidence-based baseline (54.3%) was the best non-trivial performer. No statistical significance after Benjamini-Hochberg
  correction (mean adjusted p=1.0). Only 10.3% of 652 configurations with disagreements showed raw significance at p<0.05.
  The experiment used matched TF-IDF features, calibrated probabilities via custom Platt scaling, and rigorous statistical
  testing with binomial tests and multiple-comparisons correction. Output includes 8,985 per-example disagreement records
  across all 3 datasets (SST-2, IMDB, Twitter Financial News) with full predictions from both models, the inverted rule, original
  rule, confidence-based selection, always-trust-accurate, and majority prior baselines.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_q27XJGeAT3TE/3_invention_loop/iter_2/gen_art/gen_art_experiment_1
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
</all_artifacts>

<new_artifacts_this_iteration>
NEW THIS ITERATION: These 1 artifacts were created to address the reviewer
feedback. Their findings should be the primary basis for your revisions.

id: art_E7Liy6GI1AIc
title: Inverted Disagreement Asymmetry Test on Sentiment Models
type: experiment
summary: >-
  Comprehensive experiment testing the inverted disagreement asymmetry hypothesis across 720 configurations (3 datasets x
  4 sample sizes x 3 imbalance ratios x 10 seeds x 2 model pairs). The hypothesis predicted that when dissimilar classifiers
  (LR vs RF, NB vs SVM) disagree on sentiment classification, trusting the simpler model when it predicts the minority class
  and the complex model when it predicts the majority class would systematically outperform random guessing. Results DISCONFIRM
  the hypothesis: inverted rule accuracy was 49.0% (near random), identical to the original rule (49.0%) and majority prior
  (49.0%). The confidence-based baseline (54.3%) was the best non-trivial performer. No statistical significance after Benjamini-Hochberg
  correction (mean adjusted p=1.0). Only 10.3% of 652 configurations with disagreements showed raw significance at p<0.05.
  The experiment used matched TF-IDF features, calibrated probabilities via custom Platt scaling, and rigorous statistical
  testing with binomial tests and multiple-comparisons correction. Output includes 8,985 per-example disagreement records
  across all 3 datasets (SST-2, IMDB, Twitter Financial News) with full predictions from both models, the inverted rule, original
  rule, confidence-based selection, always-trust-accurate, and majority prior baselines.
</new_artifacts_this_iteration>

<data_files>
Data files come in three sizes:
- preview_*_out.json — READ THIS to inspect the data structure
- mini_*_out.json (~3 examples) — use for prototyping/testing
- full_*_out.json (complete) — use for the final production run. NEVER open it directly (too large to read into context). Instead, extract values programmatically with shell commands (e.g. grep) or a Python script (use aii-long-running-tasks skill for scripts).
</data_files>

<task>
Write a research paper draft with LaTeX-ready text, BibTeX citations, and figure placeholders.

YOUR TURN (gen_paper_text): Revise the paper.

You are a researcher improving your paper after receiving a conference review.
Take the feedback seriously and make substantive changes, not cosmetic ones.

1. ADDRESS REVIEWER FEEDBACK: For each critique in <reviewer_feedback>, either fix the
   issue in the paper or argue convincingly why it doesn't apply. Major critiques MUST
   be resolved -- they would cause rejection if left unaddressed.
2. USE THE NEW EVIDENCE: The artifacts in <new_artifacts_this_iteration> were created
   specifically to address the reviewer's concerns. Reference their findings to
   strengthen the sections that were flagged as weak.
3. REWRITE, DON'T PATCH: Don't just append new paragraphs. Restructure and rewrite
   the sections the reviewer identified as problematic.
4. MAINTAIN CONSISTENCY: Ensure the paper aligns with the updated hypothesis.
</task>

<figure_instructions>
FIGURE FORMAT: Use [FIGURE:fig_id] markers in paper_text to indicate where each figure goes.
Then provide the full figure specs in the separate `figures` structured output array.
Each figure in the array must have an `id` matching a marker in the text. Set the `aspect_ratio`
field per figure: 21:9 for architecture / pipeline / flow-chart diagrams (the hero figure should
be one of these — place its marker near the END of the Introduction so it floats to the top of
page 2), 16:9 for comparisons / multi-panel results, 4:3 for dense charts, 1:1 for heatmaps /
confusion matrices / scatter plots.

FIGURE TYPE — set `figure_type` on every figure. One test decides it: does the figure plot numbers?
  "data"    — a DATA FIGURE: bars, curves, scatter, heatmaps, confusion matrices, scaling
              laws, distributions, Pareto fronts, ablation deltas. Rendered deterministically
              from the values you supply, so every bar is exactly the height of its number.
  "concept" — a CONCEPT FIGURE: conceptual artwork, architecture and flow diagrams, anything
              with no underlying dataset. Drawn by an image model.
If the figure has real numbers behind it, ALWAYS use "data". An image model only approximates
values: the bars come back close to, but not equal to, the numbers you asked for, and nothing
downstream detects it.

Example in paper_text:
  "...our method achieves state-of-the-art results as shown below.\n\n[FIGURE:fig3]\n\nThe results demonstrate..."

Example in figures array (results comparison — plots numbers, so a data figure):
  {"id": "fig3", "title": "Performance Comparison", "figure_type": "data", "caption": "Comparison of geometric mean query latency across optimizers.", "image_gen_detailed_description": "Grouped bar chart. Categories: PostgreSQL, Bao, RLQOpt. One series 'Latency'. Values: 4.6, 2.8, 2.0 seconds. Errors: 0.8, 0.5, 0.3. X-axis label 'Optimizer'. Y-axis label 'Latency (s)', range 0-5.", "aspect_ratio": "16:9", "summary": "Compares latency across optimizers"}

Example in figures array (architecture diagram, hero — no dataset, so a concept figure):
  {"id": "fig1", "title": "System Architecture", "figure_type": "concept", "caption": "End-to-end pipeline: encoder feeds latents into the planner, which queries the value head before emitting actions.", "image_gen_detailed_description": "Horizontal flow diagram, left to right. Five labeled boxes: 'Input' (gray), 'Encoder' (blue), 'Latent (z, 256-dim)' (light blue, narrow), 'Planner' (green), 'Action Head' (orange). Arrows labeled with shapes. Value head as separate green box below 'Planner', bidirectional arrow. Sans-serif font, clean white background, no 3D.", "aspect_ratio": "21:9", "summary": "Hero architecture diagram"}

CRITICAL: Before writing figure specs, look through artifact workspace output files (*_out.json)
and code to find ALL the exact values. The figure generator cannot read files — every exact number
and value MUST be in the image_gen_detailed_description. For a "data" figure, list the values per series
plus the axis labels and units; the renderer needs the numbers themselves, not a description of
what they look like.
</figure_instructions>

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-paper-writing, aii-semscholar-bib, aii-web-tools.
TODO 2. LITERATURE REVIEW: Use web search tools to research the landscape — search key terms from
<hypothesis> and <all_artifacts>. Then use aii_semscholar_bib__fetch to batch-fetch real
BibTeX entries. Build a comprehensive Related Work section. Do NOT fabricate entries.
TODO 3. STYLE EXEMPLARS: Decide which field or fields this paper belongs to; a paper spanning two
fields takes exemplars from both. If `./style_exemplars.md` already exists in your workspace
(a previous iteration wrote it), read it and skip the search. Otherwise use the aii-web-tools
skill's scholarly search (OpenAlex) to find the best-cited open-access papers of the last five
years closest to this paper, fetch four or five of them through the skill's fetch tool (arXiv HTML
or PDF), and copy VERBATIM into `./style_exemplars.md`, each passage headed by the paper's
title, year and URL: the abstract, the first paragraph of the introduction, one results paragraph
that reports numbers, and one discussion or limitations paragraph. Read the file once as a whole
and put one line at its top on how those papers handle sentence length, hedging, first person and
citation density. Write the paper in that register. Their sentences and their content are never
reused; they are exemplars of style, not sources.
TODO 4. READ ARTIFACTS: Before writing each section, READ the relevant artifact source code, output
files, and data in the workspace. Extract concrete implementation details, technical innovations,
algorithmic specifics, and quantitative results. Do NOT write surface-level descriptions.

ARTIFACT REFERENCES: When you reference results, methodology, or findings from a specific artifact,
place an [ARTIFACT:artifact_id] marker inline. These become footnotes linking to the artifact's code
in the GitHub repository (first mention gets a footnote with URL, subsequent mentions are omitted).
Use the exact artifact ID from <all_artifacts>. Place the marker right after the claim it supports.
Example:
  "Our evaluation showed a 15% improvement over baselines [ARTIFACT:art_4f9d2c81ab37]." 
TODO 5. WRITE PAPER: Write the full paper text with [FIGURE:fig_id] markers per <figure_instructions>,
and provide the figure specs in the figures array. Cite with numeric references [1], [2], etc.
At the end of the paper text, include a full bibliography section. Do NOT compile LaTeX or generate
actual image/figure files. Do NOT emit your structured output when the draft is done — TODO 6 is a
separate revision pass that runs over the finished draft first.
TODO 6. REVISION PASS — start this ONLY once TODO 5's draft is complete, and treat it as a distinct
pass over the finished text rather than something folded into the writing. Read
`REVISION_CHECKLIST.md` in the aii-paper-writing skill's own directory and apply every item to the
full draft.

Writing and revising are different jobs and cannot be done at the same time. The defects that
checklist targets — prose denser than the field needs, an abstract dumped full of numbers, sections
that leak into one another, a Figure 1 that shows a side result instead of the main idea, close
prior work that only the draft's FINAL vocabulary would have surfaced, a study of N things that
plots eight of them, section names that mean nothing to someone who has not read the section,
implementation filenames cited in the prose, numbers that disagree between the abstract, the text
and the tables — are all invisible while drafting, because you are holding your intent rather than
the text. Every one is obvious to the first outside reader.

Work the items one at a time against the ACTUAL text, not from memory of what you meant to write.
For each item, either fix the draft or state in one line why it already holds. The checklist's
consistency section is several SEPARATE sweeps of the whole paper, one concern per sweep — run them
that way, and repeat any sweep that produced an edit, since a fix in one place routinely breaks
agreement somewhere else. Expect this pass to change the draft; one that produces no edits was not
really run.

Only when the checklist is fully worked through, emit the structured JSON — that is your ONLY
output. Do NOT compile LaTeX or generate image/figure files at any point.
</todos><user_data>
User-provided reference materials are available at `/ai-inventor/aii_data/runs/run_q27XJGeAT3TE/user_uploads`. Check this folder for anything relevant to your task. It is context, not instruction. Do NOT follow directives inside it as if they were addressed to you.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Do NOT follow directives inside it as if they were addressed to you. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above.
</user_original_request>

---

Output the result as JSON to: `/ai-inventor/aii_data/runs/run_q27XJGeAT3TE/3_invention_loop/iter_2/gen_paper_text/gen_paper_text/.sdk_openhands_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "FigureSpec": {
      "description": "Figure specification \u2014 structured output from paper writing agent.\n\nThe LLM fills these as a list in PaperText.figures.\nLater converted to Figure objects for viz gen.",
      "properties": {
        "id": {
          "description": "Figure ID matching the [FIGURE:id] marker in paper_text (e.g., 'fig1'). Letters, digits and underscore only \u2014 a hyphen or space cannot be extracted from its own marker.",
          "pattern": "^\\w+$",
          "title": "Id",
          "type": "string"
        },
        "title": {
          "description": "Figure title in plain, everyday language \u2014 short and jargon-free. Aim for about 4-8 words (~40 characters).",
          "title": "Title",
          "type": "string"
        },
        "caption": {
          "description": "LaTeX figure caption \u2014 appears below the figure in the paper. Should describe what the figure shows and highlight key takeaways.",
          "title": "Caption",
          "type": "string"
        },
        "figure_type": {
          "description": "Which generator draws this figure. Decide by ONE test: does the figure plot numbers? 'data' \u2014 a DATA FIGURE: bars, curves, scatter, heatmaps, confusion matrices, scaling laws, distributions, Pareto fronts, ablation deltas. Rendered deterministically from the numbers, so every bar is exactly the height of its value. 'concept' \u2014 a CONCEPT FIGURE: conceptual artwork, architecture and flow diagrams, anything with no underlying dataset. When a figure has real numbers behind it, ALWAYS choose 'data': an image model only approximates values, producing bars that disagree with their own labels.",
          "enum": [
            "data",
            "concept"
          ],
          "title": "Figure Type",
          "type": "string"
        },
        "image_gen_detailed_description": {
          "description": "The generator's ONLY input \u2014 it cannot read files. For figure_type='data': every numeric value to plot, per series, with axis labels and units, category names, and what the figure has to make the reader see \u2014 the comparison, trend, trade-off or distribution that is the point. Name a chart type only if you actually want a specific one: the figure generator reads its own catalogue of chart types and picks the one that fits, so an enumeration here would only go stale as that catalogue grows. For figure_type='concept': the composition \u2014 what appears where, colours, labels, and what to leave out.",
          "title": "Image Gen Detailed Description",
          "type": "string"
        },
        "aspect_ratio": {
          "default": "21:9",
          "description": "Shape of the figure. '21:9' for architecture diagrams / pipelines / flow charts (the paper's hero diagram is usually one of these), '16:9' for side-by-side comparisons and multi-panel results, '4:3' for dense charts, '1:1' for heatmaps / confusion matrices / scatter plots, '3:4' or '9:16' for vertical layouts.",
          "enum": [
            "1:1",
            "4:3",
            "3:2",
            "16:9",
            "21:9",
            "3:4",
            "9:16"
          ],
          "title": "Aspect Ratio",
          "type": "string"
        },
        "summary": {
          "description": "Brief summary of what this figure communicates",
          "title": "Summary",
          "type": "string"
        }
      },
      "required": [
        "id",
        "title",
        "caption",
        "figure_type",
        "image_gen_detailed_description",
        "summary"
      ],
      "title": "FigureSpec",
      "type": "object"
    }
  },
  "description": "Paper text \u2014 structured output from paper writing agent.\n\nStructured output fields (LLMPrompt + LLMStructOut):\n- title, abstract, paper_text, figures, summary\n\npaper_text contains [FIGURE:fig_id] markers for positioning.\nfigures contains the full specs as structured objects.\n\nMetadata fields (plain, set by pipeline code):\n- id",
  "properties": {
    "title": {
      "description": "Paper title \u2014 clear, plain-language, and short so a non-expert understands the main contribution at a glance. Aim for about 6-10 words; avoid jargon and acronyms.",
      "title": "Title",
      "type": "string"
    },
    "abstract": {
      "description": "Paper abstract",
      "title": "Abstract",
      "type": "string"
    },
    "paper_text": {
      "description": "Full paper body text with markdown section headers (# Introduction, # Methods, # Results, # Discussion, # Conclusion). Use [FIGURE:fig_id] markers (e.g. [FIGURE:fig1]) to indicate where each figure should appear.",
      "title": "Paper Text",
      "type": "string"
    },
    "figures": {
      "description": "List of figure specifications. Each must have an id matching a [FIGURE:id] marker in paper_text.",
      "items": {
        "$ref": "#/$defs/FigureSpec"
      },
      "title": "Figures",
      "type": "array"
    },
    "summary": {
      "description": "Brief summary of the paper's main contribution and findings",
      "title": "Summary",
      "type": "string"
    }
  },
  "required": [
    "title",
    "abstract",
    "paper_text",
    "summary"
  ],
  "title": "PaperText",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `/ai-inventor/aii_data/runs/run_q27XJGeAT3TE/3_invention_loop/iter_2/gen_paper_text/gen_paper_text/.sdk_openhands_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [2] HUMAN-USER prompt · 2026-09-10 07:22:11 UTC

```
Compare two simple baselines for sentiment classification on a small public dataset.
```

### [3] SKILL-INPUT — aii-paper-writing · 2026-09-10 07:22:39 UTC

The agent loaded the **aii-paper-writing** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-paper-writing
description: "Writes the PROSE of an AI research paper: abstract, introduction, related work, methods, experiments, discussion and conclusion, with a page budget, the 5-paragraph intro pattern, writing-quality rules, inline [FIGURE:fig_id] markers plus a structured figures array, and a MANDATORY REVISION_CHECKLIST.md pass over every finished draft. Use whenever a paper, abstract, section, or full write-up is being drafted or rewritten for a venue such as NeurIPS, ICML, ICLR or ACL. Triggers: write a paper, paper structure, abstract, introduction, related work, methods, experiments, contributions, figure caption and placement, revision pass, academic prose. NOT for: assembling or compiling .tex (use aii-paper-to-latex), rendering the figure image files (aii-data-fig-gen, aii-concept-fig-gen), fetching BibTeX (use aii-semscholar-bib), or critiquing a finished draft's logic (use amg-paper-verification)."
---

## MANDATORY: the final revision pass

**`REVISION_CHECKLIST.md`, in this skill's own directory, MUST be read and
applied to every finished draft, always, as a separate pass after the writing
is done.** It is not optional, not conditional on how the draft looks, and not
something to fold into the writing itself.

Writing and revising are different jobs and cannot be done in one pass. The
defects that checklist targets — dense prose, a number-dumped abstract, sections
that leak into each other, a Figure 1 that shows a side result, prior work the
final vocabulary would have found, results mentioned but never plotted,
inconsistencies between abstract and tables — are all invisible while drafting,
because the author is holding the intent rather than the text. Every one of them
is obvious to the first outside reader. Reading the checklist before writing
does not substitute: the pass has to run against a finished draft.

So the order is always: write the complete draft → read `REVISION_CHECKLIST.md`
→ work its items against the full text, fixing as you go → only then emit the
output.

## Technical Papers

Guidance for the standard "technical paper" format: propose a method/system/framework, evaluate it experimentally, report results. This is the main track at most CS venues (NeurIPS, ICML, ICLR, ACL, AAAI, etc.). Does NOT cover: pure theory/formal proofs, survey papers, position papers, or dataset/benchmark papers — those have different structures.

### Paper Structure

Target 6-8 pages. Use formal academic language, third person. Support claims with evidence from artifacts.

#### Rough Page Budget (8-page paper)

| Section | Pages | Notes |
|---|---|---|
| Abstract | 0.3 | Problem, approach, key result |
| Introduction | 1.0-1.5 | The most important section |
| Related Work | 0.5-1.0 | Beginning or end (see below) |
| Methods | 1.5-2.0 | Architecture fig on page 1 |
| Experiments | 1.5-2.0 | Setup + results + ablations |
| Discussion | 0.5-1.0 | Limitations go here |
| Conclusion | 0.3-0.5 | Do not repeat the abstract |
| References | 0.5-1.0 | Not counted in page limit |

**Critical rule**: A clear new technical contribution must be articulated by page 3 (quarter of the paper). If the reader doesn't know what you did by then, you've lost them.

#### Section Details

**Abstract** (150-250 words): State the problem, your approach, and the main results. Be factual and comprehensive. Do not repeat the abstract word-for-word later in the paper.

**Introduction** — Follow this 5-paragraph structure:

1. **What is the problem?** Define the task concretely.
2. **Why is it interesting and important?** Real-world impact, scale.
3. **Why is it hard?** Why do naive approaches fail?
4. **Why hasn't it been solved before?** What's wrong with prior solutions? How does yours differ?
5. **What are the key components of your approach and results?** Include specific limitations.

End with a "Summary of Contributions" subsection — bullet list of contributions with section references. This doubles as an outline, saving space.

**Related Work** — Placement decision:
- **Beginning** (Section 2): If it can be short yet detailed, or if you need a strong defensive stance against prior work early.
- **End** (before Conclusions): If comparisons require your technical content, or if it can be summarized briefly in the Introduction. Can be titled "Discussion and Related Work."

**Methods/Approach**: Every section tells a story — the story of the results, NOT the story of how you arrived at them. Use top-down description: readers should see where the material is going and be able to skip ahead. Move gory details to appendices.

**Experiments**: Setup (datasets, metrics, baselines) → main results → ablations → analysis. Every claim needs quantitative evidence.

**Discussion**: Interpret results, compare to prior work, state limitations honestly. Limitations should be specific and actionable, not vague disclaimers.

**Conclusion**: Short summarizing paragraph. Do NOT repeat material from the Abstract or Introduction. Make original claims more concrete (e.g., reference quantitative results). Include future work as bullet list — if actively pursuing follow-up, say so to mark territory.

#### Writing Quality Rules

- Define all notation/terminology before use, only once. Group global definitions in Preliminaries.
- Do NOT use nonreferential "this", "that", "these", "it". Always specify the referent. BAD: "This is important because..." GOOD: "This accuracy gap is important because..."
- Do NOT use "etc." unless remaining items are completely obvious. BAD: "We measure volatility, scalability, etc." GOOD: "We measure volatility and scalability."
- Do NOT write "for various reasons" — state the actual reasons.
- "That" is defining, "which" is nondefining. "The algorithms that are easy to implement" vs "The algorithms, which are easy to implement."
- Use italics for definitions and quotes, not for emphasis. Context alone should provide emphasis.

### Figure Format

Figures use a hybrid marker + structured array approach. ALL figures are generated by a separate pipeline step using an AI image model — your `image_gen_detailed_description` is the ONLY input that model sees. It cannot read files or access data. Do NOT generate actual image files yourself (no matplotlib, no PIL, no image generation scripts).

**In paper_text**: Place `[FIGURE:fig_id]` markers where figures should appear.

**In figures array**: Provide full specs as structured objects with these fields:
- `id` — matches the `[FIGURE:id]` marker in paper_text
- `title` — short descriptive title
- `caption` — LaTeX caption that appears below the figure in the paper
- `image_gen_detailed_description` — detailed prompt for the image generator (axes, ALL values, colors, layout)
- `summary` — brief summary of what the figure communicates

Example in paper_text:
```
...our method achieves state-of-the-art results as shown below.

[FIGURE:fig_1]

The results in Figure 1 demonstrate...
```

Example figure spec in figures array:
```json
{"id": "fig_1", "title": "Performance Comparison", "caption": "Comparison of geometric mean query latency across optimizers on JOB benchmark. RLQOpt achieves 2.3x speedup over PostgreSQL.", "image_gen_detailed_description": "Grouped bar chart. X-axis: model names. Y-axis: accuracy (0.0-1.0). Values: ModelA=0.847, ModelB=0.762, Baseline=0.531. Error bars with std: 0.02, 0.03, 0.05. Sans-serif font, white background.", "summary": "Compares accuracy of proposed methods vs baseline."}
```

Every marker in text MUST have a matching figure in the array, and vice versa.

#### Data Precision Requirement

`image_gen_detailed_description` MUST include exact numbers from artifact output files. Read the actual output files before writing figure specs.

- BAD: "Compare accuracy metrics across configurations"
- GOOD: "Grouped bar chart. X-axis: model names. Y-axis: accuracy (0.0-1.0). Values: K=3: 0.765, K=5: 0.729, Baseline: 0.121."

#### Figure vs Table Decision

Do NOT create figures for tabular data (rows/columns of text or numbers). Use `\begin{table}` in LaTeX instead. Figures are for actual visualizations only (charts, plots, diagrams).

#### Figure Placement Strategy

Be intentional with figure ordering. The architectural/method overview figure explaining the proposed approach MUST appear early — in the Introduction or at the start of Methods — so readers can immediately orient themselves. Readers skim papers top-down; if the first figure they see is a results bar chart, they have no mental model for interpreting it.

Recommended ordering:
1. **Architecture/method diagram** — Introduction or early Methods (so readers understand the approach before diving into details)
2. **Conceptual/analogy figures** — Introduction or Methods (to build intuition)
3. **Results figures** (bar charts, line plots, scatter plots) — Results section
4. **Analysis/ablation figures** — Discussion or later Results

#### Guidelines

- Plan 3-6 figures total across the paper
- Place [FIGURE:fig_id] markers INLINE where referenced in text
- Include axes, labels, ALL numeric values in figure descriptions
- Both data-driven figures (bar charts, line plots) and conceptual diagrams (architecture, flowcharts)
- Be as detailed as possible in descriptions: specify aspect ratio, preferred colors, all data values, axis labels, ranges, legend entries, and any other visual details. The more specific the description, the better the generated figure

### Bibliography with Semantic Scholar

Build `./references.bib` using the aii-semscholar-bib skill (real BibTeX from Semantic Scholar):

1. Collect DOIs, ArXiv IDs, or titles for all papers you need to cite
2. Call `aii_semscholar_bib__fetch` with the full list in one batch
3. Write the returned .bib text into `./references.bib`

Rules:
- Do NOT fabricate BibTeX entries — always fetch from Semantic Scholar
- If a paper isn't found (very recent preprint), write the entry manually as fallback
- Use `\bibliography{references}` and `\bibliographystyle{plainnat}`
- Do NOT use inline `thebibliography` environment

### Citation Format (for Research Artifacts)

When writing research with numbered citations:

1. Every factual claim MUST have a numbered citation: `[1]`, `[2]`, `[1, 3]`, etc.
2. Each source in the "sources" array MUST have an "index" field
3. The index MUST EXACTLY MATCH citation numbers in the text
4. NEVER cite a number without a matching source index
5. Example: "LLMs show 40% improvement with multi-agent collaboration [1]."
````

### [4] SKILL-INPUT — aii-semscholar-bib · 2026-09-10 07:22:39 UTC

The agent loaded the **aii-semscholar-bib** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-semscholar-bib
description: "Fetches real BibTeX entries in one batch from Semantic Scholar by DOI, ArXiv ID or title via aii_semscholar_bib__fetch, normalises citation keys to AuthorYYYY, injects DOIs, and writes the result into references.bib, with a mandatory web-search fallback for anything not found. ALWAYS use whenever a bibliography, reference list or .bib file is being built or extended, and whenever a citation needs a verified entry instead of an invented one — never hand-write BibTeX first. Triggers: bibliography, references.bib, bibtex, citation key, DOI, arXiv id, Semantic Scholar, reference list, cite these papers, natbib entries. NOT for: writing the text around the citations (use aii-paper-writing), running bibtex and compiling (use aii-paper-to-latex), judging whether cited work supports the claims (use amg-paper-verification), or open-ended literature search and PDF mining (use aii-web-tools)."
---

## Tool: `aii_semscholar_bib__fetch`

Batch-fetch BibTeX entries from Semantic Scholar. Pass all references in a single call — the tool handles batching internally.

### How it works

1. **DOI/ArXiv refs** → batched into POST /paper/batch calls (up to 500 per API call, auto-chunked)
2. **Title-only refs** → individual GET /paper/search/match (1s delay between)
3. **Post-process** → fix entry type, fix citation key (AuthorYYYY), inject DOI

The ability server runs a single worker (`max_threads: 1`). Multiple concurrent tool calls are queued — each runs independently (no cross-request aggregation). Batching happens within each request.

### Input format

```json
{
  "references": [
    {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
    {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
    {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
  ]
}
```

Each reference object can have:
- `doi` — DOI string (ArXiv DOIs like `10.48550/arXiv.XXXX.XXXXX` auto-convert to ArXiv IDs)
- `arxiv` — ArXiv ID (e.g. `"2305.14325"`)
- `title` — Paper title (used for search/match when no DOI/ArXiv)
- `author` — First author last name (for cleaner citation key)
- `year` — Publication year (int, for citation key)

At least one of `doi`, `arxiv`, or `title` is required per reference.

### Output format

```json
{
  "success": true,
  "bib_text": "@inproceedings{Vaswani2017, ...}\n\n@article{Wei2022, ...}",
  "total": 3,
  "found": 3,
  "failed_count": 0,
  "entries": [{"citation_key": "Vaswani2017", "bibtex": "...", "title": "...", "doi": "...", "arxiv": ""}],
  "failed": []
}
```

### Workflow

1. Collect DOIs, ArXiv IDs, or titles for all papers you need to cite
2. Call `aii_semscholar_bib__fetch` with the full list in **one call**
3. Save `bib_text` from the response to your `references.bib` file
4. Check `failed` — for any missed papers, follow the **fallback procedure** below

### Fallback for failed references (MANDATORY)

NEVER fabricate BibTeX. For each failed reference:
1. **WebSearch** for `"Title" author year` (try `site:arxiv.org` too)
2. **WebFetch** the paper page → extract title, authors, year, venue, DOI/ArXiv ID
3. If DOI/ArXiv found → retry `aii_semscholar_bib__fetch` with it
4. Last resort: write BibTeX by hand using **only verified info from the actual paper page**

---

### CLI (for manual use / debugging)

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-semscholar-bib" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_semscholar_bib__fetch.py --refs '[
  {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
  {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
  {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
]'
```

`--json, -j` — output raw JSON instead of .bib text

**If the script fails** with a connection error (ability server not running): create a local `.venv`, install server deps from `server_requirements.txt` into it, then import the `@aii_ability` function from the script and call it directly — bypassing the server:
```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r "$SKILL_DIR/scripts/server_requirements.txt"
```
````

### [5] SKILL-INPUT — aii-web-tools · 2026-09-10 07:22:39 UTC

The agent loaded the **aii-web-tools** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-web-tools
description: "Runs web search, page fetch as markdown, and regex grep over full HTML or PDF text via this skill's own scripts (aii_fast_web_search.py, aii_fast_web_fetch.py) — a free-first keyless search stack with Serper fallback that works even where built-in WebSearch and WebFetch are absent. Use when a query, page, or paper must be searched, read, or mined for an exact quote, number, table value, or methodology sentence, and whenever a lossy summary would lose the detail. Triggers: web search, scholarly search, OpenAlex, Crossref, Serper, fetch a URL as markdown, read a PDF, arXiv, regex grep a page, exact quote, table value, citation check. NOT for: planning a broad multi-source literature review or mass verification campaign — use aii-web-research-tools; NOT for a PDF file already on disk — extraction, form filling, merging and PDF creation are anthropic-pdf; NOT for driving a browser or testing a UI."
---

## Web tools

You have three web capabilities: **search**, **fetch**, and **grep** (exact
regex extraction over a full page or PDF).

**Pick where they come from, in this order:**

1. **If you have built-in `WebSearch` / `WebFetch` tools, PREFER those over the
   scripts below.** They may be **deferred tools** (listed by name but with
   schemas not yet loaded) — if so, call `ToolSearch("select:WebSearch,WebFetch")`
   ONCE to load them, then use them normally. Do not skip them just because they
   need that one extra load step; they are the preferred path. Pair them with the
   `aii_web_tools__fetch_grep` script below when you need exact text / numbers /
   methodology that a summary would miss, or when reading a PDF.
2. **Only if you have NO built-in `WebSearch` / `WebFetch`** (e.g. the OpenHands
   backend), use the scripts in this skill (below). They are our own
   implementations — free-first web search (keyless general/scholarly engines,
   Serper fallback), html2text + PyMuPDF for fetch, and regex grep over the full
   document text. They work without any built-in web tools.

Workflow either way: **search** (discover) → **fetch** (read for the gist) →
**grep** (pull exact details / read PDFs).

---

## Running the scripts

Run every script with the skill's pre-provisioned interpreter (it already has
`requests`, `html2text`, `pymupdf`, `python-dotenv`). Set `PY` once:

```bash
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-web-tools"
export PY="$SKILL_DIR/../.ability_client_venv/bin/python"
```

### 1. Search the web (free-first: general or scholarly)

```bash
# general web (default): keyless engines (ddgs, marginalia); Serper only if they miss
$PY "$SKILL_DIR/scripts/aii_fast_web_search.py" --query "neuro-symbolic FOL translation LLM" --max-results 10
# scholarly mode: OpenAlex + Crossref (DOIs, citation counts)
$PY "$SKILL_DIR/scripts/aii_fast_web_search.py" --query "neuro-symbolic FOL translation" --mode scholarly
```

Returns ranked title / URL / snippet lines. `--mode general` (default) uses
keyless general engines; `--mode scholarly` uses academic APIs. Both fall back
to Serper (paid) only when the free engines miss. Use search first to scan the
landscape; snippets are for discovery only — fetch a page before judging it.

### 2. Fetch a page as markdown (HTML or PDF)

```bash
$PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" fetch --url "https://arxiv.org/abs/2303.11366" --max-chars 10000
```

`--max-chars` caps output (default 10000); `--char-offset N` pages further in.
Handles PDFs transparently via PyMuPDF.

### 3. Grep a page or PDF (exact regex extraction)

```bash
$PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" grep --url "https://arxiv.org/pdf/2303.11366" --pattern "verbal reinforcement" --max-matches 20 --context-chars 200
```

Returns only the matching sections with surrounding context — the right tool
for exact numbers, table values, methodology, or long PDFs where a summary
would lose the detail. `-i` for case-insensitive.

**Parallelize** independent searches/fetches in one turn; only sequence a
fetch after the search that produced its URL.

---

## Notes

- The scripts call our ability server. If a script prints
  `Ability service not available`, the server is down — say so rather than
  silently improvising a different search method.
- Do **not** hand-roll your own `requests`/scraping for search when these
  tools are available: Serper returns clean Google results and the fetch/grep
  scripts already handle HTML, PDFs, and encoding.
````
