# gen_full_paper — report_results

> Phase: `gen_paper_repo` · `gen_full_paper`
> Run: `run_q27XJGeAT3TE` — When Two Classifiers Disagree, Does the Direction Tell You Which One Is Right?
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_full_paper` (sdk_openhands_agent)

### [1] SYSTEM-USER prompt · 2026-09-10 08:32:33 UTC

````
<task>
Create a publication-ready top-conference LaTeX paper with BibTeX from <paper_text> and <available_figures>, compile to PDF.
</task>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<paper_text>
title: When Two Classifiers Disagree, Does the Direction Tell You Which One Is Right?
abstract: >-
  When two classifiers produce different labels on the same example, practitioners typically fall back on confidence scores
  or majority voting to decide which model to trust. We ask whether the direction of disagreement carries a systematic signal:
  does knowing that a simple model predicts the majority class while a complex model predicts the minority class tell us which
  prediction is correct? This question follows from the bias-variance tradeoff, which predicts that simple models err toward
  the mode while complex models err toward noise. We test this hypothesis across 719 configurations on three sentiment datasets,
  varying sample size, class imbalance, and model pair. We find no evidence for directional asymmetry: both the original rule
  and its inversion achieve accuracy indistinguishable from the majority-class prior. The confidence-based baseline outperforms
  both directional rules by over five percentage points. We show that an earlier report of below-chance accuracy for the original
  rule was driven by a confound between model complexity and feature representation and disappears when both models share
  the same features. The negative result rules out a natural intuition about the bias-variance tradeoff as a diagnostic tool
  for inter-model disagreement on sentiment data.
paper_text: |-
  # When Two Classifiers Disagree, Does the Direction Tell You Which One Is Right?

  ## Abstract

  When two classifiers produce different labels on the same example, practitioners typically fall back on confidence scores or majority voting to decide which model to trust. We ask whether the *direction* of disagreement carries a systematic signal: does knowing that a simple model predicts the majority class while a complex model predicts the minority class tell us which prediction is correct? This question follows from the bias-variance tradeoff, which predicts that simple models err toward the mode while complex models err toward noise. We test this hypothesis across 719 configurations on three sentiment datasets, varying sample size, class imbalance, and model pair. We find no evidence for directional asymmetry: both the original rule and its inversion achieve accuracy indistinguishable from the majority-class prior. The confidence-based baseline outperforms both directional rules by over five percentage points. We show that an earlier report of below-chance accuracy for the original rule was driven by a confound between model complexity and feature representation and disappears when both models share the same features. The negative result rules out a natural intuition about the bias-variance tradeoff as a diagnostic tool for inter-model disagreement on sentiment data.

  ## Introduction

  Sentiment classification on small datasets is unstable. Models overfit, benchmarks contain label noise, and it is unclear which model to trust when they disagree. When a logistic regression and a random forest produce different labels on the same sentence, the standard response is to pick the prediction with higher confidence or to fall back to majority voting. Both approaches measure the *magnitude* of disagreement but ignore its *direction*.

  The direction of disagreement should matter, at least in principle. A simple model with strong inductive bias toward the majority class should be reliable when it predicts the majority and unreliable when it predicts the minority. A complex model that captures genuine minority-class signals but overfits to noise in the majority class should be reliable on minority predictions and unreliable on majority predictions. If this intuition is correct, the pattern of disagreement between two dissimilar classifiers should systematically predict which one is right.

  We formalized this intuition as the *disagreement asymmetry oracle* in a previous study and tested it on two sentiment datasets. We reported 42.4% accuracy for the directional rule, below the 50% chance level, and concluded that the bias-variance asymmetry does not manifest as a usable signal. Reviewers of that work identified a critical confound: our simple model used word-level TF-IDF features while our complex model used character n-grams. Their disagreements may have reflected representation differences rather than complexity differences, making it impossible to attribute results to the bias-variance tradeoff. Reviewers also noted that 42.4% accuracy implies the *inverted* rule achieves 57.6%, and asked whether the asymmetry operates in the opposite direction of the hypothesis.

  This paper addresses both concerns. We re-run the experiment with matched feature representations, where both models use the same TF-IDF word n-gram features, and test both the original and inverted rules. We expand the study to three datasets (SST-2, IMDB, and Twitter Financial News), two model pairs (logistic regression vs. random forest, and Naive Bayes vs. support vector machine), and add probability calibration to ensure fair confidence comparisons. We test 719 configurations across four sample sizes, three class imbalance ratios, and ten random seeds.

  We find that neither the original nor the inverted directional rule works. Both achieve 49.0% accuracy on disagreement samples, identical to the majority-class prior and indistinguishable from random guessing. The effect holds across both model pairs, all three datasets, all sample sizes, and all imbalance ratios. No configuration reaches statistical significance after multiple-comparisons correction. The original 42.4% result was an artifact of the feature confound: when both models share features, the directional signal vanishes entirely.

  Our contribution is threefold. First, we rule out the disagreement asymmetry hypothesis after controlling for the feature representation confound that invalidated the earlier study. Second, we show that the inverted rule — the most natural alternative to the original hypothesis — also fails, closing off the most promising direction for future work. Third, we release an experimental suite with matched features, calibrated probabilities, and rigorous statistical testing that can be reused to test this hypothesis on other domains.

  [FIGURE:fig1]

  **Summary of Contributions**

  - We test the disagreement asymmetry oracle with matched feature representations, eliminating the word-level vs. character-level confound from our previous study \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-2f324c-disagreement-asymmetry-oracle/tree/main/round-2/experiment-1}}.
  - We find that both the original and inverted directional rules achieve 49.0% accuracy on disagreement samples, indistinguishable from the majority-class prior across 719 configurations.
  - We show that the original 42.4% result was driven by the feature confound and disappears when both models share features.
  - We demonstrate that confidence-based selection (54.3%) remains the practical default for resolving inter-model disagreements on sentiment data.

  ## Related Work

  **Trust scores.** Jiang et al. [1] propose the trust score, which measures agreement between a classifier and a modified nearest-neighbor classifier. High trust scores identify correctly classified examples with high precision, outperforming the classifier's own confidence score. The trust score measures *agreement magnitude*, not disagreement direction. Our work tests whether the direction of disagreement between two *dissimilar* classifiers carries predictive signal.

  **Ensemble diversity.** The ensemble learning literature studies how diversity among members improves performance [2, 3]. Kuncheva and Whitaker [2] introduce the Q-statistic and correlation coefficient as measures of pairwise disagreement. Gong et al. [3] review diversity measures and their relationship to ensemble accuracy. None of this work examines whether the *direction* of individual disagreements predicts correctness.

  **Dynamic ensemble selection.** Dynamic classifier selection methods choose the best model for each test instance based on local accuracy estimates [4, 5]. These methods use a separate oracle set to estimate each model's competence region. Our approach asks whether the disagreement pattern itself, without any oracle set, encodes information about correctness.

  **Label noise detection.** Methods like FINE [6] use loss patterns and representation dynamics to detect noisy labels. Han et al. [7] survey label-noise representation learning methods. These approaches rely on a single model's training dynamics, not on inter-model disagreement. Our work asks whether disagreement between two models trained on the same data provides a cheaper signal for label quality.

  **Active learning disagreement.** Active learning uses disagreement between models to select informative samples for labeling [8]. Vote entropy, consensus entropy, and max disagreement measure how much models disagree, not which one is right. Our work tests the complementary question: when models disagree, can we predict the correct label from the pattern of disagreement?

  **Learning from disagreement.** Uma et al. [9] survey methods for learning from human annotator disagreement. The focus is on soft labels and crowdsourcing, not on inter-model disagreement as a diagnostic tool. They note that "the question of how to leverage inter-model disagreement remains underexplored" [9].

  **Classifier calibration.** Comparing confidence scores across models requires calibrated probabilities. Logistic regression outputs are naturally calibrated, while random forest and support vector machine outputs are typically not [10, 11]. We calibrate both models using Platt scaling before comparing confidence, addressing a limitation of our previous study.

  **Pervasive label errors.** Freestone et al. [12] show that label errors in benchmarks destabilize results across models. They do not propose using inter-model disagreement direction to detect which labels are wrong, but their work motivates the search for cheap diagnostics for label quality.

  To our knowledge, no prior work studies the direction of inter-model disagreement as a systematic predictor of correctness.

  ## Methods

  ### Models

  We train two classifiers with different inductive biases on the same training data, using **matched feature representations** to eliminate the confound identified in our previous study:

  1. **Simple model pair**: Logistic regression ($L_2$ regularization, $C=1.0$, max 1000 iterations) and Multinomial Naive Bayes ($\alpha=0.1$). Both models have strong inductive biases — linear decision boundaries and feature independence, respectively.

  2. **Complex model pair**: Random forest (100 trees, no depth limit) and linear support vector machine ($C=1.0$, max 1000 iterations). Both models can fit non-linear decision boundaries (random forest) or find optimal separating hyperplanes with margin maximization (SVM).

  Both models in each pair use the **same TF-IDF feature representation**: word-level unigrams and bigrams, maximum 5,000 features, minimum document frequency 2, sublinear TF scaling. This eliminates the feature confound identified by reviewers of our previous study.

  ### Datasets

  We use three binary sentiment datasets:

  - **SST-2** [13]: 67,349 movie review sentences with binary sentiment labels (44% negative, 56% positive).
  - **IMDB** [14]: 25,000 movie reviews with balanced sentiment labels (50/50).
  - **Twitter Financial News** \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-2f324c-disagreement-asymmetry-oracle/tree/main/round-1/dataset-1}}: 3,365 finance-related tweets with binary sentiment labels (43% bearish, 57% bullish).

  ### Experimental Protocol

  For each dataset, we create subsamples at four sizes (100, 200, 500, 1000) and three class imbalance ratios (1.0, 1.5, 2.0), where the ratio is majority-to-minority. Each configuration is repeated with 10 random seeds, giving 720 total configurations (4 sizes $\times$ 3 ratios $\times$ 10 seeds $\times$ 3 datasets $\times$ 2 model pairs). Of these, 719 completed successfully and 652 produced at least one disagreement on the test set.

  Each subsample is split 80/20 into train and test. Both models are trained on the training split. Probabilities are calibrated using Platt scaling on a held-out validation set before evaluation. On the test set, we identify all samples where the two models disagree and evaluate the following methods:

  **Inverted directional rule**: If the simple model predicts the minority class, trust the simple model. Otherwise, trust the complex model.

  **Original directional rule**: If the simple model predicts the majority class, trust the simple model. Otherwise, trust the complex model.

  **Confidence baseline**: Trust the model with higher calibrated predicted probability for its prediction.

  **Always-trust-accurate**: Always trust the model that is more accurate on the disagreement subset (oracle baseline).

  **Majority prior**: Always predict the majority class on the disagreement set.

  ### Statistical Testing

  For each configuration, we test whether the inverted rule's accuracy exceeds the majority-class prior on the disagreement set using a binomial test. We apply the Benjamini-Hochberg procedure across all 652 configurations with disagreements to control the false discovery rate at $\alpha = 0.05$. We report both raw and adjusted p-values.

  ## Results

  ### Overall Performance

  Across all 652 configurations with disagreements, both the inverted and original directional rules achieve a mean accuracy of 49.0%, identical to the majority-class prior (49.0%). The confidence baseline achieves 54.3%, and the oracle baseline (always trust the more accurate model) achieves 67.3%.

  [FIGURE:fig2]

  The directional rules perform at chance. This is not a marginal effect: the confidence baseline outperforms both directional rules by 5.3 percentage points on average. The gap between the directional rules and the oracle baseline (18.3 percentage points) shows that information about which model is correct *does* exist on the disagreement set, but the directional rule cannot access it.

  ### Per-Dataset Breakdown

  Table 1 shows the mean accuracy of each method broken down by dataset.

  [FIGURE:fig3]

  The pattern holds across all three datasets. On IMDB, the confidence baseline achieves the highest accuracy (56.7%), suggesting that confidence carries more signal on longer review texts. On SST-2 and Twitter Financial News, the confidence baseline is lower (52.5% and 53.4%), but still above both directional rules.

  ### Per-Model-Pair Breakdown

  The results are consistent across both model pairs. For logistic regression vs. random forest, the inverted rule achieves 50.7% and the original rule achieves 46.7%. For Naive Bayes vs. SVM, the inverted rule achieves 47.3% and the original rule achieves 51.3%. Neither pair shows a systematic directional signal.

  ### Effect of Sample Size and Imbalance

  The inverted rule's accuracy varies from 41.6% at sample size 100 to 51.0% at sample size 1000, but the variation is consistent with sampling noise rather than a systematic trend. The correlation between sample size and inverted accuracy is positive ($r = 0.215$, $p < 10^{-8}$), but this reflects the fact that larger samples produce more disagreements, making the accuracy estimate more stable rather than indicating a real effect.

  The accuracy varies across imbalance ratios: 47.3% at ratio 1.0, 52.2% at ratio 1.5, and 47.4% at ratio 2.0. The correlation between imbalance ratio and inverted accuracy is negative ($r = -0.133$, $p = 0.0003$), but the effect is small and inconsistent with any theoretical prediction.

  ### Statistical Significance

  Of 652 configurations with disagreements, 67 (10.3%) show raw significance at $p < 0.05$. After Benjamini-Hochberg correction, zero configurations remain significant. The mean raw p-value is 0.616, and the mean adjusted p-value is 1.0.

  ### Feature Confound Analysis

  Our previous study reported 42.4% accuracy for the original directional rule \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-2f324c-disagreement-asymmetry-oracle/tree/main/round-1/experiment-1}}. That study compared a model using word-level TF-IDF features (logistic regression) against a model using character n-gram features (random forest). The 42.4% result — 7.6 percentage points below chance — suggested the inverted rule might achieve 57.6%.

  The current study eliminates this confound by using matched TF-IDF features for both models. With matched features, the original rule achieves 49.0% and the inverted rule achieves 49.0%. The 42.4% result was driven by the feature representation difference, not by the bias-variance tradeoff.

  [FIGURE:fig4]

  This is a critical finding: the original study's negative result was an artifact of comparing two different feature spaces. The simple model's "bias" was not toward the majority class — it was toward word-level patterns. The complex model's "variance" was not noise sensitivity — it was character-level sensitivity. Their disagreements reflected representation mismatch, not complexity differences.

  ## Discussion

  ### Why the Hypothesis Failed

  The disagreement asymmetry oracle was motivated by the bias-variance tradeoff: simple models should be biased toward the majority class, and complex models should capture minority-class signals. The intuition is theoretically sound but does not translate to a usable signal in practice for three reasons.

  **First**, the bias-variance tradeoff operates at the population level, not the instance level. A simple model's tendency to predict the majority class is an aggregate property, not a per-instance guarantee. On any given disagreement, the simple model may be right for reasons unrelated to its bias.

  **Second**, even with matched features, the two models in each pair have different inductive biases that do not align with the majority-minority axis. Logistic regression and random forest disagree for reasons related to their decision boundaries (linear vs. tree-based), not to their treatment of class balance. Naive Bayes and SVM disagree because of their different assumptions about feature independence and margin maximization.

  **Third**, the sentiment classification task may not exhibit the kind of noise structure that the hypothesis requires. If label noise is roughly symmetric across classes, the simple model's majority-class bias does not give it an advantage on majority-class disagreements.

  ### What the Negative Result Means

  The negative result does not imply that disagreement is uninformative. The confidence baseline achieves 54.3% accuracy, above chance, showing that the *magnitude* of disagreement (as captured by calibrated confidence scores) does carry signal. The oracle baseline achieves 67.3%, showing that information about which model is correct exists but is not accessible through a simple directional rule.

  This suggests that the bias-variance asymmetry, if it exists at all, is not accessible through the binary directional rules we tested. A more sophisticated oracle that accounts for local data density, feature-space geometry, or model calibration might recover the signal.

  ### Limitations

  Our study has several limitations. We test two model pairs on three sentiment datasets. The hypothesis might hold for other model families (e.g., neural networks vs. linear models) or other domains where the bias-variance tradeoff manifests differently. The small sample sizes (100–1000) may not be sufficient to reveal the effect, though the effect should be strongest in small-sample regimes where the bias-variance tradeoff matters most. We do not test the effect of model calibration on the directional rule itself, only on the confidence baseline.

  ### Multi-Model Extension

  The directional rule might generalize to settings with more than two models. With three or more models, the pattern of disagreement becomes richer: a 2-vs-1 split encodes more information than a binary disagreement. The model that disagrees with the majority might be the one that is wrong, or it might be the one that is right. This question remains open.

  ## Conclusion

  We tested whether the direction of disagreement between a simple and a complex classifier predicts which model is correct on sentiment classification tasks. The hypothesis, motivated by the bias-variance tradeoff, predicts that simple models are more reliable on majority-class predictions and complex models on minority-class predictions. We find no evidence for this pattern across 719 configurations on SST-2, IMDB, and Twitter Financial News. Both the original and inverted directional rules achieve 49.0% accuracy, indistinguishable from the majority-class prior. The original 42.4% result from our previous study was driven by a confound between model complexity and feature representation and disappears when both models share features.

  The negative result rules out a natural intuition about the bias-variance tradeoff as a diagnostic tool for inter-model disagreement. Confidence-based selection remains the practical default, achieving 54.3% accuracy on disagreement samples.

  **Future work**:
  - Test the hypothesis on image classification and tabular datasets.
  - Investigate whether neural network model pairs exhibit directional asymmetry.
  - Study whether multi-model disagreement patterns (e.g., 2-vs-1 splits) carry more signal than binary disagreements.
  - Develop oracles that combine directional information with local data density or feature-space geometry.

  ## References

  [1] Jiang, H., Kim, B., & Gupta, M. (2018). To trust or not to trust a classifier. *Neural Information Processing Systems*, 5546–5557.

  [2] Kuncheva, L. I., & Whitaker, C. J. (2003). Measures of diversity in classifier ensembles and a correlation-based analysis. *Machine Learning*, 51(2), 181–207.

  [3] Gong, Z., Zhong, P., & Hu, W. (2018). Diversity in machine learning. *IEEE Access*, 7, 64323–64350.

  [4] Rodriguez, J. J., Kuncheva, L. I., & Alonso, C. J. (2017). Dynamic classifier selection: Recent advances and perspectives. *Information Fusion*, 36, 124–135.

  [5] Zhou, Z.-H., & Wu, J. (2018). K-nearest oracles borderline dynamic classifier ensemble selection. *International Joint Conference on Neural Networks*, 1–8.

  [6] Kim, T., Ko, J., Cho, S., Choi, J., & Yun, S.-Y. (2021). FINE samples for learning with noisy labels. *Neural Information Processing Systems*, 24137–24149.

  [7] Han, B., Yao, Q., Liu, T., Niu, G., Tsang, I. W., Kwok, J. T., & Sugiyama, M. (2020). A survey of label-noise representation learning: Past, present and future. *arXiv preprint arXiv:2011.04406*.

  [8] Danka, P. (2018). modAL: a modular active learning library for Python. *Journal of Machine Learning Research*, 19(129), 1–6.

  [9] Uma, A., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M. (2021). Learning from disagreement: A survey. *Journal of Artificial Intelligence Research*, 72, 1385–1470.

  [10] Wang, C. (2023). Calibration in deep learning: A survey of the state-of-the-art. *arXiv preprint arXiv:2308.01222*.

  [11] Naeini, M. P., Cooper, G. F., & Hauskrecht, M. (2015). Obtaining well calibrated probabilities using bayesian model averaging. *Proceedings of the 32nd International Conference on Machine Learning*, 2901–2909.

  [12] Freestone, J., Durrant, J., & Ellul, J. (2019). Pervasive label errors in test sets for natural language inference tasks. *arXiv preprint arXiv:1909.13133*.

  [13] Socher, R., Perelygin, A., Wu, J., Chuang, J., Mangatar, C., Pang, B., & Ng, A. Y. (2013). Recursive deep models for semantic compositionality over a sentiment treebank. *Proceedings of the 2013 Conference on Empirical Methods in Natural Language Processing*, 1631–1642.

  [14] Maas, A. L., Daly, R. E., Pham, P. T., Huang, D., Ng, A. Y., & Potts, C. (2011). Learning word vectors for sentiment analysis. *Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics*, 142–150.
summary: >-
  We test whether the direction of disagreement between a simple and a complex classifier predicts which model is correct
  on sentiment classification tasks. Across 719 configurations on three datasets with matched features and calibrated probabilities,
  both the original and inverted directional rules achieve 49.0% accuracy, indistinguishable from the majority-class prior.
  We show that an earlier below-chance result was driven by a feature representation confound and disappears when both models
  share features. Confidence-based selection remains the practical default at 54.3%.
</paper_text>

<available_figures>
--- Item 1 ---
id: fig1
figure_type: concept
title: Disagreement Asymmetry Hypothesis
caption: >-
  The disagreement asymmetry oracle hypothesis: when a simple model and a complex model disagree, the direction of disagreement
  should predict which model is correct. The original rule (top) trusts the simple model on majority-class predictions; the
  inverted rule (bottom) trusts the simple model on minority-class predictions. Both rules achieve 49.0% accuracy, indistinguishable
  from the majority-class prior.
image_gen_detailed_description: >-
  Horizontal flow diagram with three panels. Left panel: two model icons labeled 'Simple Model' (blue, simple icon) and 'Complex
  Model' (red, complex icon) with arrows pointing to a central 'Disagreement' box. Middle panel: two branches labeled 'Original
  Rule' (top, arrow pointing to 'Trust Simple on Majority') and 'Inverted Rule' (bottom, arrow pointing to 'Trust Simple on
  Minority'). Right panel: a large 'X' mark in gray over both branches, with text '49.0% accuracy — no directional signal'.
  Clean white background, sans-serif font, minimal design. No 3D effects.
aspect_ratio: '21:9'
summary: >-
  Conceptual overview of the disagreement asymmetry hypothesis and its disconfirmation
figure_path: figures/fig1_v0.jpg

--- Item 2 ---
id: fig2
figure_type: data
title: Overall Accuracy Comparison
caption: >-
  Mean accuracy across 652 configurations with disagreements. Both directional rules achieve 49.0%, identical to the majority-class
  prior. The confidence baseline achieves 54.3%. The oracle baseline (always trust the more accurate model) achieves 67.3%,
  showing that information about correctness exists but is not accessible through directional rules.
image_gen_detailed_description: >-
  Horizontal bar chart. Y-axis: method names (top to bottom: 'Oracle (always-trust-accurate)', 'Confidence baseline', 'Inverted
  directional rule', 'Original directional rule', 'Majority prior'). X-axis: accuracy percentage, range 0 to 75. Bar values:
  Oracle=67.3, Confidence=54.3, Inverted=49.0, Original=49.0, Majority prior=49.0. Colors: Oracle=green, Confidence=blue,
  Inverted=orange, Original=orange, Majority prior=gray. Error bars showing standard deviation of 22.8 for the directional
  rules. A vertical dashed line at 49.0% labeled 'Majority prior'. Sans-serif font, white background.
aspect_ratio: '16:9'
summary: Compares accuracy of all methods across all configurations
figure_path: figures/fig2_v0.pdf

--- Item 3 ---
id: fig3
figure_type: data
title: Per-Dataset Accuracy Breakdown
caption: >-
  Mean accuracy broken down by dataset. The pattern holds across all three datasets: both directional rules perform at chance
  while the confidence baseline exceeds chance. IMDB shows the largest confidence gap (56.7% vs 49.0%).
image_gen_detailed_description: >-
  Grouped bar chart with three groups on x-axis: 'SST-2', 'IMDB', 'Twitter Financial News'. Each group has three bars: 'Inverted
  rule', 'Original rule', 'Confidence baseline'. Y-axis: accuracy percentage, range 40 to 65. Values: SST-2 (Inverted=47.6,
  Original=51.9, Confidence=52.5), IMDB (Inverted=51.3, Original=47.7, Confidence=56.7), Twitter Financial (Inverted=47.9,
  Original=47.8, Confidence=53.4). Colors: Inverted=orange, Original=red-orange, Confidence=blue. A horizontal dashed line
  at 49.0% labeled 'Majority prior'. Sans-serif font, white background.
aspect_ratio: '16:9'
summary: Breaks down accuracy by dataset showing consistent pattern
figure_path: figures/fig3_v0.pdf

--- Item 4 ---
id: fig4
figure_type: data
title: Feature Confound Analysis
caption: >-
  Comparison of the original directional rule accuracy between the previous study (unmatched features: word-level TF-IDF vs.
  character n-grams) and the current study (matched features: both use TF-IDF word n-grams). The 42.4% result from the previous
  study was driven by the feature confound and disappears when both models share features.
image_gen_detailed_description: >-
  Side-by-side bar chart with two groups on x-axis: 'Previous Study (unmatched features)' and 'Current Study (matched features)'.
  Y-axis: accuracy percentage, range 35 to 60. Previous study has one bar: 'Original rule' = 42.4 (red). Current study has
  two bars: 'Original rule' = 49.0 (orange) and 'Inverted rule' = 49.0 (blue). A horizontal dashed line at 50.0% labeled 'Chance
  level'. A horizontal dashed line at 49.0% labeled 'Majority prior'. An annotation arrow from 42.4 to 49.0 labeled 'Feature
  confound effect: +6.6 pp'. Sans-serif font, white background.
aspect_ratio: '4:3'
summary: Shows how the feature confound drove the original below-chance result
figure_path: figures/fig4_v0.pdf
</available_figures>

<figure_requirements>
CRITICAL: Include ALL figures from <available_figures>. No exceptions.

- Every figure MUST use \includegraphics{figures/<the filename from its own `figure_path` above>} — INCLUDING the extension it actually has. Data figures are delivered as `.pdf` (vector, so their axis labels stay sharp) and concept figures as `.jpg`. Writing `.jpg` for a `.pdf` figure names a file that is not in figures/ and the build fails on it
- Do NOT skip, convert to tables, or describe without inserting
- Each needs: \begin{figure}[placement], \includegraphics, \caption, \label, \end{figure} — one placement for every figure, see FLOAT PLACEMENT below. Constrain every \includegraphics with `width=\linewidth,height=0.85\textheight,keepaspectratio`. The height is a LAST RESORT, not the usual limit: it exists so a very tall figure cannot overrun the page, and at 0.4 it bound almost everything instead — a 1:1 confusion matrix printed at 50.9% and its 11 pt axis labels reached the page at 5.6 pt, below what any venue accepts. At 0.85 every ratio the paper prompt prescribes (21:9, 16:9, 4:3, 1:1) is limited by WIDTH, prints at 93% and keeps its text above 10 pt. Use exactly these option keys — `max height=` is NOT valid LaTeX
- Use the `caption` field from each figure for \caption{...} — do NOT invent new captions
- Place figures where their [FIGURE:fig_id] markers appear in paper_text
- VERIFICATION: paper.tex MUST have exact same number of \includegraphics as <available_figures>
- Do NOT generate new figure images (no matplotlib, no PIL, no image generation). Use ONLY the pre-generated figures from <available_figures>. They were already created by a previous pipeline step.

FLOAT PLACEMENT: every figure gets \begin{figure}[!htbp]. Measured, not chosen:
the document the aii-paper-to-latex skill sets up is ONE column, so `figure*` is
exactly as wide as `figure` (469.76pt either way) and gains nothing; and any
placement asking for a page TOP — `[!t]`, `[!tbp]` — floated the hero diagram above
the paper's own title on page 1, while `[!htbp]` did not. `[!htbp]` also gives LaTeX
four options, so a float can never be deferred to the end of the document, which one
option alone risks. Where the hero ENDS UP is decided by its [FIGURE:] marker in
paper_text, which is already placed near the end of the Introduction — preserve it.
</figure_requirements>

<artifact_links>
The paper_text contains \footnote{Code: \url{...}} references linking to artifact source code
on GitHub. Include \usepackage{hyperref} and \usepackage{url}.
Preserve these exactly as-is — do not remove, rewrite, or convert them to plain text.
The URLs will not resolve yet (the repo is deployed after compilation) — do NOT try to verify or fix them.
</artifact_links>

<headings>
NEVER use inline math (``$...$``) inside ``\section{...}`` / ``\subsection{...}`` / ``\subsubsection{...}`` arguments — hyperref's bookmark builder errors out (``Token not allowed in a PDF string``) and the PDF outline breaks. If a section heading needs a math-looking term, use the text equivalent (``d star`` not ``$d^*$``, ``alpha-equivalent`` not ``$\alpha$-equivalent``) or wrap it in ``\texorpdfstring{$math$}{plain}``. Inline math inside body paragraphs is fine.
</headings>

<writing_register>
Write in the register of the field's best papers (the style exemplars block below, when the writing step saved any), not in the register of a language
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

<style_exemplars>
The draft in <paper_text> was written to the register of these passages, which the writing step
saved as style_exemplars.md. Any prose you add or change here (captions, transitions, cuts
for the page limit) stays in that register.

# Style Exemplars for Disagreement Asymmetry Paper

**Field**: Machine learning methodology / empirical ML study (NeurIPS/ICML/ACL track)
**Style notes**: These papers use short-to-medium sentences (15-25 words median), first person plural ("we"), dense citation in Related Work but sparse in Methods/Results, minimal hedging in results sections (state numbers plainly), and direct negative-result language ("does not hold", "we find no evidence").

---

## "To Trust Or Not To Trust A Classifier" (Jiang et al., 2018, NIPS)
URL: https://arxiv.org/abs/1805.11783

**Abstract**:
Knowing when a classifier's prediction can be trusted is useful in many applications and critical for safely using AI. While the bulk of the effort in machine learning research has been towards improving classifier performance, understanding when a classifier's predictions should and should not be trusted has received far less attention. The standard approach is to use the classifier's discriminant or confidence score; however, we show there exists an alternative that is more effective in many situations. We propose a new score, called the trust score, which measures the agreement between the classifier and a modified nearest-neighbor classifier on the testing example. We show empirically that high (low) trust scores produce surprisingly high precision at identifying correctly (incorrectly) classified examples, consistently outperforming the classifier's confidence score as well as many other baselines. Further, under some mild distributional assumptions, we show that if the trust score for an example is high (low), the classifier will likely agree (disagree) with the Bayes-optimal classifier. Our guarantees consist of non-asymptotic rates of statistical consistency under various nonparametric settings and build on recent developments in topological data analysis.

**Introduction (first paragraph)**:
Knowing when a classifier's prediction can be trusted is useful in many applications and critical for safely using AI.

**Results paragraph**:
We evaluate the trust score on 10 image classification datasets and 4 text classification datasets. The trust score consistently outperforms the confidence score across all datasets, with an average improvement of 12.3% in precision at identifying misclassified examples. On the CIFAR-10 dataset, the trust score achieves 78.4% precision compared to 66.1% for the confidence score.

**Discussion/Limitations**:
Our analysis assumes that the training and test distributions are identical. When distribution shift occurs, the trust score may degrade. We leave the study of distribution-shift-robust trust scores to future work.

---

## "A Survey of Label-noise Representation Learning" (Han et al., 2020)
URL: https://arxiv.org/abs/2011.04406

**Abstract**:
Classical machine learning implicitly assumes that labels of the training data are sampled from a clean distribution, which can be too restrictive for real-world scenarios. However, statistical-learning-based methods may not train deep learning models robustly with these noisy labels. Therefore, it is urgent to design Label-Noise Representation Learning (LNRL) methods for robustly training deep models with noisy labels.

**Results paragraph**:
Table 3 summarizes the performance of 15 LNRL methods on 6 benchmark datasets with 20% symmetric noise. The best performing method, FINE, achieves 89.2% accuracy on CIFAR-10, improving over the baseline by 4.7 percentage points.

**Discussion**:
Most existing methods rely on heuristics rather than theoretical guarantees. We identify three open problems: instance-dependent noise modeling, adversarial label noise, and generalization beyond classification tasks.

---

## "FINE Samples for Learning with Noisy Labels" (Kim et al., 2021, NeurIPS)
URL: https://arxiv.org/abs/2102.11628

**Abstract**:
Modern deep neural networks (DNNs) become frail when the datasets contain noisy (incorrect) class labels. Robust techniques in the presence of noisy labels can be categorized into two folds: developing noise-robust functions or using noise-cleansing methods by detecting the noisy data.

**Results paragraph**:
We evaluate FINE on 6 benchmark datasets with varying noise rates. FINE achieves state-of-the-art performance on 5 out of 6 datasets. On CIFAR-10 with 40% symmetric noise, FINE reaches 82.1% accuracy, outperforming the previous best by 2.3%.

**Limitations**:
FINE requires computing the eigendecomposition of the data gram matrix, which has O(n^3) complexity. This limits its application to datasets with fewer than 10,000 samples.

---

## "Learning from Disagreement: A Survey" (Uma et al., 2021, JAIR)
URL: https://doi.org/10.1613/jair.1.12752

**Abstract**:
Disagreement among annotators is ubiquitous in real-world data collection scenarios. This survey provides a comprehensive overview of methods for learning from disagreeing annotators in natural language processing and computer vision.

**Results paragraph**:
We compare 12 disagreement-aware learning methods across 8 datasets. Methods that model annotator expertise achieve 3.2% higher F1 scores than methods that treat all annotators equally.

**Discussion**:
Most existing work focuses on human-to-human disagreement. The question of how to leverage inter-model disagreement remains underexplored.

---

## "Diversity in Machine Learning" (Kuncheva, 2019, IEEE Access)
URL: https://doi.org/10.1109/access.2019.2917620

**Abstract**:
Diversity among ensemble members is a key factor in achieving good ensemble performance. This paper reviews measures of diversity and their relationship to ensemble accuracy.

**Results paragraph**:
We evaluate 8 diversity measures on 10 datasets. The Q-statistic and correlation coefficient show the strongest correlation with ensemble accuracy (r = 0.72 and r = 0.68 respectively).

**Limitations**:
The relationship between diversity and accuracy is dataset-dependent. No single diversity measure works optimally across all domains.
</style_exemplars>
FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-paper-to-latex, aii-semscholar-bib.
TODO 2. Review <paper_text> and <available_figures>. Copy all figure images into ./figures/ in your workspace. Count figures — MUST include every one. Plan placements per section. Build `./references.bib` via aii_semscholar_bib__fetch — collect DOIs/ArXiv IDs from <paper_text> and batch-fetch all BibTeX in one call. Do NOT fabricate entries.
TODO 3. Create `./paper.tex` per aii-paper-to-latex skill's setup, write ALL sections, insert ALL figures from <available_figures>, include `./references.bib` via \bibliography. Compile to PDF per skill's process. Fix errors.
TODO 4. CRITICAL VERIFICATION: Run `grep -c 'includegraphics' paper.tex`, confirm count equals figures in <available_figures>. If not, add missing figures. Verify `./paper.pdf` was created.
TODO 5. VISUAL REVIEW: Write Python script to convert EVERY page of paper.pdf to PNG at 150 DPI (use pdf2image or pymupdf). Then read ALL page screenshots — each page image costs ~1,600 tokens so a 15-page paper is only ~24K tokens. You MUST read every page. The ONLY exception is if all page images would not fit in your remaining context — in that case, read as many as fit and state which pages you are skipping and why. Check every page for layout issues, overlapping figures, cut-off text, bad spacing, formatting problems. Fix issues and recompile.
TODO 6. FINAL READ: Check page count (`pdfinfo paper.pdf` or pymupdf). Read entire paper.pdf — check for missing sections, unclear explanations, inconsistencies, typos. Fix and recompile. The ONLY exception is if all pages would not fit in your remaining context — in that case, read as many pages as fit and state which pages you are skipping and why.
</todos>

---

Output the result as JSON to: `/ai-inventor/aii_data/runs/run_q27XJGeAT3TE/4_gen_paper_repo/_4_assemble_paper/paper/workspace/.sdk_openhands_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "FullPaperExpectedFiles": {
      "description": "All expected output files from full paper generation.",
      "properties": {
        "paper_tex_path": {
          "description": "Path to LaTeX source file. Example: 'paper.tex'",
          "title": "Paper Tex Path",
          "type": "string"
        },
        "paper_pdf_path": {
          "description": "Path to compiled PDF. Example: 'paper.pdf'",
          "title": "Paper Pdf Path",
          "type": "string"
        },
        "references_bib_path": {
          "description": "Path to BibTeX bibliography file. Example: 'references.bib'",
          "title": "References Bib Path",
          "type": "string"
        },
        "figure_paths": {
          "description": "Paths to all figure image files. Example: ['figures/fig1_v0.jpg', 'figures/fig2_v0.jpg']",
          "items": {
            "type": "string"
          },
          "title": "Figure Paths",
          "type": "array"
        }
      },
      "required": [
        "paper_tex_path",
        "paper_pdf_path",
        "references_bib_path",
        "figure_paths"
      ],
      "title": "FullPaperExpectedFiles",
      "type": "object"
    }
  },
  "description": "Full paper \u2014 structured output from paper generation.",
  "properties": {
    "title": {
      "description": "Paper title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance. Aim for about 4-8 words (~40 characters).",
      "maxLength": 90,
      "minLength": 12,
      "title": "Title",
      "type": "string"
    },
    "summary": {
      "description": "Brief summary of the generated paper: sections written, figures included, compilation status",
      "maxLength": 5000,
      "minLength": 500,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/FullPaperExpectedFiles",
      "description": "All output files you created. Must include paper.tex, paper.pdf, references.bib, and paths to all figure files."
    }
  },
  "required": [
    "title",
    "summary",
    "out_expected_files"
  ],
  "title": "FullPaper",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `/ai-inventor/aii_data/runs/run_q27XJGeAT3TE/4_gen_paper_repo/_4_assemble_paper/paper/workspace/.sdk_openhands_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [2] HUMAN-USER prompt · 2026-09-10 08:32:33 UTC

```
Compare two simple baselines for sentiment classification on a small public dataset.
```

### [3] SKILL-INPUT — aii-paper-to-latex · 2026-09-10 08:32:53 UTC

The agent loaded the **aii-paper-to-latex** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-paper-to-latex
description: "Assembles and compiles a LaTeX paper into paper.pdf: documentclass and package preamble, figure floats that includegraphics pre-generated vector .pdf and .jpg files, float-placement and width rules, and the required pdflatex, bibtex, pdflatex, pdflatex run sequence. Use whenever pre-written text and pre-generated figures must become a compiled PDF, and whenever a build misbehaves — citations printing as question marks, figures drifting to the end or above the title, shrunken axis labels, undefined references. Triggers: latex, tex, pdflatex, bibtex, natbib, includegraphics, figure float, htbp, compile or build the paper, paper.tex, paper.pdf. NOT for: writing the paper's text or deciding its structure (use aii-paper-writing), creating the figure images (aii-data-fig-gen, aii-concept-fig-gen), or fetching bibliography entries (use aii-semscholar-bib); NOT for reshaping a PDF that already exists — merging, splitting, form filling, table extraction (use anthropic-pdf)."
---

## LaTeX Paper Assembly

Assembles a research paper from paper text, pre-generated figures (vector `.pdf` for data figures, `.jpg` for concept figures) and a bibliography into a compiled PDF.

### Document Setup

```latex
\documentclass[11pt,letterpaper]{article}
\usepackage{graphicx, geometry, amsmath, hyperref, url, natbib, booktabs, xcolor, listings}
\geometry{margin=1in}
\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black}
```

### Figure Inclusion

CRITICAL: Include ALL figures. Every figure MUST appear in the paper.

```latex
\begin{figure}[!htbp]
  \centering
  \includegraphics[width=\linewidth,height=0.85\textheight,keepaspectratio]{figures/filename.pdf}
  \caption{Descriptive caption.}
  \label{fig:label}
\end{figure}
```

Rules:
- ALWAYS `[!htbp]` — all four options, so a float can never be deferred to the end of the
  document, which `[t]` or `[h]` alone risks. Do not ask for a page TOP: `[!t]` and
  `[!tbp]` both floated a figure ABOVE the paper's own title on page 1, where `[!htbp]`
  on the same document did not. Where a figure lands is decided by where it is declared
  in the text
- Use `figure`, never `figure*`. This document class is ONE column, so `figure*` is exactly
  as wide as `figure` (469.76pt either way) and gains nothing, while restricting the float
  to a page top
- ALWAYS constrain with `width` and `keepaspectratio`. Add `height` only as a
  LAST RESORT against a very tall figure overrunning the page, and keep it
  generous — `0.85\textheight`. A tight height cap binds on ordinary figures
  and LaTeX then shrinks the TEXT with them: at `0.4\textheight` a square
  figure printed at 50.9%, putting 11 pt axis labels on the page at 5.6 pt.
  The figure generator measures legibility at the figure's OWN size, so it
  cannot see this happen
- Every figure needs `\caption`, `\label`, and a `\ref` in the text
- Do NOT convert figures to tables or describe them without inserting the image
- Do NOT skip any figures

### Compilation Process

Run each command separately (do NOT chain with `&&` — pdflatex often exits non-zero on warnings, which would skip bibtex and leave citations as `??`):

```bash
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

All four commands are required. Skipping bibtex causes `??` in all citations.
Fix any errors between runs. Verify `./paper.pdf` was created.

### Output Files

- `./paper.tex` — LaTeX source
- `./references.bib` — bibliography file
- `./paper.pdf` — compiled PDF
- `./figures/` — all figure images (pre-generated, copied into workspace). Data
  figures are `.pdf` (vector — LaTeX renders their text at page resolution, which
  is what keeps axis labels sharp in print); concept figures are `.jpg`. Use each
  file's OWN extension in `\includegraphics`; there is no conversion step.
````

### [4] SKILL-INPUT — aii-semscholar-bib · 2026-09-10 08:32:53 UTC

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

### [5] SYSTEM-USER prompt · 2026-09-10 08:47:26 UTC

```
<validation-feedback>
Attempt 1 failed validation.

The output file `.sdk_openhands_agent_struct_out.json` does not exist yet. Produce it as JSON matching the schema.

Produce `.sdk_openhands_agent_struct_out.json` again so it contains corrected JSON that matches the schema. Do not invent new fields.
</validation-feedback>
```
