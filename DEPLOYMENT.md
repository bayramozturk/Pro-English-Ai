# Pro English AI Single-Service Deployment

## Best Setup

Use one simple path:

```text
GitHub repository
        |
        v
Render Web Service
        |
        v
english.yourdomain.com
```

The user opens only your subdomain. Vercel, a second frontend deployment, and
URL forwarding are not required. Render runs the Streamlit application,
model, assessment, and the low-memory Writing Coach from the included
`Dockerfile`.

## Recommended Plan

Start with Render Free while preparing:

- Custom domains and managed HTTPS are supported.
- The service wakes automatically when a request arrives.
- After 15 minutes without HTTP or WebSocket traffic, it sleeps.
- A cold start takes about one minute.

For a live presentation with no cold-start risk, switch only the web service
to Render Starter shortly before the presentation. Starter currently costs
$7/month, does not spin down, and billing is prorated. The domain and code do
not change. You can return to Free after the presentation.

## 1. Push to GitHub

Create an empty GitHub repository, then run:

```powershell
git add .
git commit -m "Prepare Pro English AI for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Do not upload `.runtime`, `app_data`, virtual environments, or local database
files. They are already excluded by `.gitignore`.

## 2. Create the Render Service

1. Sign in to Render with GitHub.
2. Select **New > Blueprint**.
3. Choose the Pro English AI repository.
4. Render reads `render.yaml`.
5. Confirm the service name and deploy.
6. Wait for the Docker build to finish.
7. Open the assigned `onrender.com` address.
8. Check `https://YOUR_SERVICE.onrender.com/_stcore/health`.

The health endpoint should return:

```text
ok
```

## 3. Connect Your Subdomain

Assume your intended address is:

```text
english.yourdomain.com
```

In Render:

1. Open the Pro English AI web service.
2. Open **Settings > Custom Domains**.
3. Select **Add Custom Domain**.
4. Enter `english.yourdomain.com`.
5. Render displays the DNS target for your service.

In your domain provider's DNS panel, create:

```text
Type:  CNAME
Name:  english
Value: YOUR_SERVICE.onrender.com
TTL:   Auto
```

Remove any conflicting `A`, `AAAA`, or existing `CNAME` record for the same
`english` host. Return to Render and select **Verify**. Render automatically
creates and renews the HTTPS certificate.

If the domain uses Cloudflare, begin with the record in **DNS only** mode.
Enable proxying only after Render verifies the domain and HTTPS works.

## 4. Presentation Stability

Safest option:

1. Upgrade the Render service from Free to Starter before the presentation.
2. Open the custom subdomain once.
3. Run one writing analysis.
4. Verify all Writing Coach tabs.
5. Keep the browser tab open during the presentation.

Budget option:

1. Stay on Free.
2. Open the subdomain 10 minutes before presenting.
3. Wait for the application to load completely.
4. Keep the page open. Active Streamlit WebSocket messages prevent idle
   spin-down.

The permanent `onrender.com` URL remains available as a backup if DNS
propagation is delayed.

## Data Safety

Public deployments use:

```text
PRO_ENGLISH_AI_STORAGE_MODE=session
```

Profiles and results stay in the current browser session and are not written
to a shared SQLite profile. Render's filesystem is temporary, so permanent
user accounts require an external database in a later production phase.

Render also uses:

```text
PRO_ENGLISH_AI_WRITING_ENGINE=fallback
```

This keeps analysis responsive on memory-limited instances by avoiding a
second Java process. Local development continues to use LanguageTool
automatically when `.runtime/LanguageTool-6.5` and Java are available.

## Final Preflight

```powershell
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m py_compile app.py writing_coach.py assessment.py product.py
streamlit run app.py
```

Manual checks:

- Analyze a 50-150 word English text.
- Open all Writing Coach tabs.
- Complete a placement assessment.
- Generate and interact with the learning plan.
- Download the corrected text and JSON report.
- Test the custom subdomain in an incognito window and on a phone.
