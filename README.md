# Pro English AI

Pro English AI is an AI-supported English writing intelligence product that estimates
CEFR level, explains the result, and turns each analysis into a practical
learning direction.

## Product Experience

- AI-supported CEFR analysis from A1 to C2
- Input quality and result reliability indicators
- Vocabulary, sentence, and complexity metrics
- Local spelling, grammar, punctuation, and style diagnostics
- Exact line/column error locations and before/after sentence comparison
- Downloadable corrected writing with an offline fallback engine
- Personalized focus areas and next-step guidance
- Downloadable JSON analysis reports
- Opt-in local profile with persistent analysis history
- Weekly analysis goals and target CEFR level
- Persistent progress center and assessment analytics
- Personalized weekly learning plan generated from analysis and assessment data
- Trackable practice tasks with weekly completion progress
- 36-question A1-C2 placement assessment
- 18-question targeted level checks
- Grammar, vocabulary, and reading skill profiles
- Difficulty-aware CEFR estimation and explained answer review

## Model Validation

The current lightweight model is trained on 8,724 samples and evaluated on
the official independent CEFR-SP test split containing 1,460 samples.

- Exact agreement with either expert annotation: 77.95%
- Prediction within one CEFR level: 98.56%
- Mean absolute error: 0.499 CEFR level

See [DATA_SOURCES.md](DATA_SOURCES.md) for corpus, citation, and licensing
details.

## Run Locally

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Public deployments use session-only profiles by default. To enable local
SQLite history on a trusted computer:

```powershell
$env:PRO_ENGLISH_AI_STORAGE_MODE="local"
streamlit run app.py
```

The full Writing Coach uses the local LanguageTool 6.5 runtime under
`.runtime/`. When that runtime is unavailable, Pro English AI continues with its
lightweight offline correction rules instead of blocking CEFR analysis.

## Deployment

- Single production path: GitHub to Render with `Dockerfile` and `render.yaml`
- Public address: your own subdomain connected directly to the Render service
- Emergency backup: the service's permanent `onrender.com` address

See [DEPLOYMENT.md](DEPLOYMENT.md) for the complete release checklist and
[VIDEO_SCRIPT.md](VIDEO_SCRIPT.md) for the YouTube demonstration flow.

To rebuild the model:

```powershell
python train.py
```

## Architecture

- `app.py`: Streamlit product interface and user flows
- `product.py`: analysis interpretation, reliability, and report generation
- `writing_coach.py`: local error detection, correction, and sentence comparison
- `assessment.py`: balanced question bank and CEFR ability estimation
- `learning.py`: weekly plan generation and learning-context inference
- `storage.py`: transactional SQLite profiles, history, and dashboard metrics
- `utils.py`: deterministic language metrics and text helpers
- `train.py`: reproducible training and independent evaluation
- `datasets/cefr_sp`: versioned CEFR-SP training and test data
- `model_report.json`: transparent model evaluation results

## Local Data and Privacy

Pro English AI currently runs as a local beta workspace. Profile settings, analyses,
and assessment results are stored only when local history is enabled. The
data is written to `app_data/pro_english_ai.db`, which is excluded from version
control. Users can disable persistence or delete all local history from the
Progress Center.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Product Direction

The next production milestones are authenticated cloud profiles, encryption
at rest, organization workspaces, a teacher dashboard, API service, payments,
observability, and a transformer-based model behind a versioned inference
endpoint.
