# Pro English AI YouTube Demo Flow

Target duration: 8-12 minutes.

## 1. Opening - 30 seconds

"Pro English AI is an AI-supported English intelligence platform that estimates a
user's CEFR level from A1 to C2, explains writing errors, runs a multi-skill
assessment, and creates a personalized weekly learning plan."

Show the landing page, product name, and CEFR scale.

## 2. Problem and Solution - 60 seconds

- Problem: Most level tests return only a score.
- Solution: Pro English AI combines level prediction, explainable metrics, correction,
  assessment, and an actionable plan.
- Clarify that the result is not an official certificate.

## 3. AI Writing Analysis - 2 minutes

Use a prepared 80-120 word English paragraph with several intentional errors.

Show:

- Estimated CEFR level and likely range.
- Reliability and input-quality scores.
- Word count, sentence length, vocabulary diversity, and complexity.
- Model validation: 77.95% exact agreement and 98.56% within one level.

## 4. Writing Coach - 2 minutes

Show:

- Exact line and column of each issue.
- Wrong and suggested forms.
- Turkish explanation.
- Corrected full text.
- Before/after sentence comparison.
- Corrected-text download.

## 5. Placement Assessment - 2 minutes

- Explain 36-question full placement and 18-question target checks.
- Show grammar, vocabulary, and reading coverage.
- Complete a few questions.
- Show answer explanations and skill profile using a prepared result.

## 6. Learning Plan and Progress - 90 seconds

- Open the weekly plan.
- Show current level, target level, focus domain, and task duration.
- Mark one task complete.
- Open the progress center and explain session-safe public deployment.

## 7. Technical Architecture - 90 seconds

Show a simple slide:

- Streamlit interface.
- Scikit-learn word and character TF-IDF features with Ridge regression.
- CEFR-SP and project data.
- LanguageTool 6.5 plus deterministic fallback rules.
- SQLite only for trusted local mode.
- Unit tests and Docker deployment.

Avoid saying that the model "understands English like a human." Describe it
as a validated machine-learning estimate.

## 8. Closing - 30 seconds

Summarize the four pillars:

1. CEFR analysis.
2. Writing correction.
3. Multi-skill assessment.
4. Personalized learning plan.

Keep the public application URL and GitHub repository link visible.

## Recording Checklist

- Use 1080p recording and 125-150% browser zoom.
- Disable notifications.
- Prepare input text and assessment result before recording.
- Wake the Render service before starting.
- Record one clean backup take of the full product flow.
- Blur local paths, usernames, and private repository information.
