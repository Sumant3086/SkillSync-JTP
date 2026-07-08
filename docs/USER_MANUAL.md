# SkillSync — User Manual

**Version:** 1.0.0  
**Platform:** Web browser (desktop and tablet recommended)  
**Live URL:** https://skillsync-h76d.onrender.com

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [The Matching Wizard — Step by Step](#3-the-matching-wizard--step-by-step)
   - [Step 1: Your Project](#step-1-your-project)
   - [Step 2: Your Skills](#step-2-your-skills)
   - [Step 3: Ideal Collaborator](#step-3-ideal-collaborator)
   - [Step 4: Working Style](#step-4-working-style)
   - [Step 5: Review & Match](#step-5-review--match)
4. [Understanding Your Results](#4-understanding-your-results)
   - [Match Score](#match-score)
   - [Score Colours](#score-colours)
   - [Score Breakdown](#score-breakdown)
   - [Radar Chart](#radar-chart)
   - [Match Reasons and Considerations](#match-reasons-and-considerations)
5. [Sorting and Filtering Results](#5-sorting-and-filtering-results)
6. [Adjusting Your Preferences](#6-adjusting-your-preferences)
7. [Frequently Asked Questions](#7-frequently-asked-questions)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Introduction

SkillSync helps you find compatible project collaborators by going beyond simple skill matching. It evaluates eight dimensions of compatibility and returns the top 10 profiles ranked by overall fit, with a transparent explanation of why each person was recommended.

**What makes SkillSync different:**
- You see exactly _why_ each person was ranked where they were — not just a number.
- Trade-offs and potential incompatibilities are shown alongside strengths.
- Every input field is optional — you get useful results even with minimal input.

**The collaborator pool:** SkillSync includes 40 diverse synthetic profiles covering a wide range of skills, experience levels, working styles, and timezones. These are representative professional personas created for the platform.

---

## 2. Getting Started

### Opening the App

1. Open a web browser and go to **https://skillsync-h76d.onrender.com**
2. You will see the SkillSync landing page with an overview of how the platform works.

### First Visit — Service Warm-Up

The application runs on a free hosting tier that pauses the backend service when it has not been used for 15 minutes. On your very first visit (or after a period of inactivity), you may see a brief loading screen with the message:

> *"The service is waking up — first load can take 20–40 s on the free tier."*

This is normal. The page will load automatically once the service is ready — you do not need to refresh.

### Starting the Matching Process

Click the **Start Matching →** button on the landing page to open the 5-step preference wizard.

---

## 3. The Matching Wizard — Step by Step

The wizard collects your preferences across five screens. You can move forward with **Next →** and go back with **← Back** at any point. No data is lost when navigating between steps.

---

### Step 1: Your Project

**Question:** What domains are you working in?

Select one or more project domains that describe the area your project focuses on. Examples:

| Domain | What it covers |
|---|---|
| Web Development | Browser-based applications, websites, web tools |
| Mobile Apps | iOS, Android, or cross-platform mobile applications |
| SaaS Products | Subscription software delivered over the internet |
| AI & Machine Learning | Intelligent systems, models, data-driven features |
| FinTech | Financial technology, payment systems, banking apps |
| Healthcare Tech | Medical software, HIPAA-relevant applications |
| E-commerce | Online shopping, inventory, payment flows |
| DevOps & Infrastructure | Cloud, CI/CD, container orchestration |
| Data Science | Data pipelines, analytics, visualisation |
| Blockchain | Decentralised applications, smart contracts |
| Open Source | Community-driven, publicly maintained projects |
| Startup MVPs | Early-stage products, rapid prototyping |

**Tip:** Select all domains that genuinely apply. The algorithm rewards collaborators whose interests overlap with yours — a more accurate selection produces better matches.

**This field is optional.** If you skip it, interest compatibility defaults to a neutral score and other dimensions carry more weight.

---

### Step 2: Your Skills

**Question:** What skills do you already bring to the project?

Select the technical skills you already have. This tells the algorithm what you _don't_ need from a collaborator.

**Category filter:** Use the buttons at the top (All, Frontend, Backend, Database, DevOps, Data & AI, Design, Mobile, Tools & Practices) to narrow the skill list to a specific category. The selected category filters the visible options but does not remove your existing selections from other categories.

**Available skill categories:**

| Category | Example skills |
|---|---|
| Frontend | React, TypeScript, Next.js, Vue.js, Tailwind CSS |
| Backend | Python, Node.js, FastAPI, Django, Java, Go |
| Database | PostgreSQL, MongoDB, Redis, Elasticsearch |
| DevOps | Docker, Kubernetes, AWS, Terraform, CI/CD |
| Data & AI | Machine Learning, TensorFlow, PyTorch, Pandas, SQL |
| Design | UI/UX Design, Figma, Prototyping, Adobe XD |
| Mobile | React Native, Flutter, iOS, Android |
| Tools | Git, REST APIs, GraphQL, Testing, Agile, Scrum |

**Tip:** Be honest — selecting skills you don't really have skews the algorithm toward collaborators who share your weaknesses rather than filling your gaps.

**This field is optional.** Leaving it blank means all skills are treated as potential complementary additions.

---

### Step 3: Ideal Collaborator

**Question:** What do you need from a partner?

This step has two parts:

#### Skills You Need

Select the skills you want your collaborator to bring. This is the most heavily weighted input in the algorithm (33% of the total score).

Use the same category filter buttons as Step 2 to browse by category.

**Tip:** Be specific. If you need someone who can build and deploy a FastAPI backend, select `FastAPI`, `Python`, and `Docker` rather than selecting all backend skills.

#### Preferred Experience Level

Select the seniority level you are looking for:

| Level | Typical profile |
|---|---|
| Junior | 0–2 years of experience; eager to learn, needs guidance |
| Mid-level | 3–5 years; works independently on defined tasks |
| Senior | 6–9 years; can lead technical decisions |
| Lead | 10+ years; architects systems, mentors others |

**Note:** The algorithm is slightly forgiving of over-experienced collaborators (e.g., requesting mid-level but matching with a senior scores better than the reverse). A more experienced partner rarely hurts; a less experienced one may create extra support overhead.

**Both fields are optional.** Leaving them blank applies neutral scoring for these sub-dimensions.

---

### Step 4: Working Style

**Question:** How do you like to collaborate?

This step captures four practical compatibility factors:

#### Weekly Availability

Drag the slider to indicate how many hours per week you expect to collaborate.

- Range: 1 to 60 hours per week
- Default: 20 hours

The algorithm compares your value against each collaborator's stated availability. A small surplus (collaborator offers slightly more than you need) is ideal. A large surplus or a deficit both reduce the score.

#### Your Timezone

Select your UTC offset from the dropdown. This is used to calculate how many hours apart you are from each collaborator.

- Profiles are spread across UTC-8 (Pacific) to UTC+9 (Japan)
- If you are in India, select `UTC+5:30`
- Timezone difference is scored on a smooth decay — every hour apart matters

#### Preferred Team Size

Select the team structure you are comfortable working in:

| Option | Meaning |
|---|---|
| Small (2–3) | You and one or two others — tight collaboration, everyone knows everything |
| Medium (4–6) | Small team with some specialisation |
| Large (7+) | Larger organisation, more roles, clearer separation of concerns |

#### Collaboration Style

| Style | Meaning |
|---|---|
| Collaborative | You prefer frequent pair programming, discussions, shared ownership |
| Independent | You prefer clear tasks and working autonomously; check in at milestones |
| Flexible | You adapt to whatever style your partner prefers |

**Matching note:** Flexible collaborators match well with all styles (score 90). Collaborative and independent have lower mutual compatibility (score 55).

#### Communication Preference

| Preference | Meaning |
|---|---|
| Async | You prefer messages, PRs, comments — respond when available |
| Sync | You prefer real-time calls, live pair sessions |
| Hybrid | You mix both depending on context |

**Matching note:** Hybrid communicators match well with both async and sync partners (score 85). Async and sync have lower mutual compatibility (score 45).

**All four fields are optional.** Leaving them blank applies neutral scoring for those dimensions.

---

### Step 5: Review & Match

This screen shows a summary of all your selected preferences before submitting.

| Field | Your selection |
|---|---|
| Project Domains | (your selections or "None selected") |
| Your Skills | (your selections or "None selected") |
| Skills Needed | (your selections or "None selected") |
| Experience Preference | (your selection or "Any") |
| Weekly Availability | X hours |
| Timezone | UTC+X |
| Team Size | (your selection or "No preference") |
| Collaboration Style | (your selection or "No preference") |
| Communication | (your selection or "No preference") |

Review your choices. Use **← Back** to return to any previous step and adjust.

When you are satisfied, click **Find My Matches**. The algorithm evaluates all 40 profiles (typically in under a second on a warm backend) and takes you to the Results screen.

---

## 4. Understanding Your Results

### Match Score

Each collaborator card shows an **overall match score** as a percentage (0–100%). This is the weighted sum of all eight compatibility dimensions, plus a small consistency adjustment (±3 pts) that rewards balanced profiles.

```
Overall Score = 
  Skills ×33% + Interests ×18% + Availability ×14% + 
  Collaboration ×9% + Communication ×9% + Team Size ×7% + 
  Timezone ×5% + Experience ×5%  ±  Consistency bonus
```

A score of 84% means the collaborator scored an average of 84 points across all dimensions, weighted by importance.

### Score Colours

| Colour | Range | Meaning |
|---|---|---|
| Green | 70–100% | Strong match — high compatibility across most dimensions |
| Amber | 45–69% | Moderate match — strong on some dimensions, weaker on others |
| Red | 0–44% | Weak match — notable compatibility concerns |

### Score Breakdown

Click **+ Show Score Breakdown** on any card to expand a detailed view. You will see:

- A **radar chart** visualising all eight dimensions at once
- **Progress bars** for each dimension with its raw score and weighting

This lets you answer questions like: *"This person scored 91% on skills but only 45% on timezone — is the timezone gap a dealbreaker for me?"*

### Radar Chart

The radar chart is an octagonal spider diagram. Each axis represents one scoring dimension. The coloured polygon shows how the collaborator scored:

- A large, even polygon → balanced, high compatibility
- A large polygon on some axes and small on others → specialist match (strong in certain areas)
- A small polygon → generally lower compatibility

Grid rings at 25%, 50%, and 75% help read the scale.

### Match Reasons and Considerations

Every card includes two lists:

**Why This Match** — specific reasons the collaborator scored well. Examples:
- "Covers 3 required skills: Python, FastAPI, PostgreSQL"
- "Same or very close timezone — easy real-time collaboration"
- "Communication preference matches"

**Considerations** — honest notes about where compatibility is lower. Examples:
- "Availability may not meet your weekly hours requirement"
- "Significant timezone gap — async-first collaboration recommended"
- "Different preferred collaboration styles"

Both lists are generated from the actual dimension scores — they reflect exactly what the algorithm computed.

---

## 5. Sorting and Filtering Results

### Sort By

Use the sort pills at the top of the results page to re-order your matches:

| Sort option | Orders by |
|---|---|
| Overall Match | Highest total weighted score (default) |
| Best Skills | Highest skill dimension score |
| Best Availability | Highest availability dimension score |
| Closest Timezone | Highest timezone dimension score |
| Most Shared Interests | Highest interests dimension score |

Switching sort order is instant — no new API request is made.

### Minimum Score Filter

The **Min score** slider (below the sort pills) hides all matches below a score threshold.

- Range: 0% to 80%, in 5% steps
- Default: 0% (all matches shown)

**Example:** Setting it to 60% shows only collaborators with an overall score of 60% or higher. If no results remain, the page shows:
> *"No matches above X%. Try lowering the minimum score filter."*

---

## 6. Adjusting Your Preferences

### From the Results Page

Click **Adjust Preferences** to return to the wizard. This re-opens the wizard pre-filled with your previous preferences — you can modify any step and re-submit.

### Full Reset

Click **SkillSync** in the header to return to the landing page. Clicking **Start Matching →** again opens a fresh wizard with blank defaults.

---

## 7. Frequently Asked Questions

**Q: All fields say "optional" — what happens if I fill in nothing?**  
A: Every blank field defaults to a neutral score of 50 pts. Results are still ranked, but the differences between profiles will be smaller since no strong preferences were expressed. For the most useful results, fill in at least "Skills You Need" and your timezone.

**Q: Why do some matches show a Considerations list even when the overall score is high?**  
A: A high overall score is a weighted average. A collaborator might score 95% on skills (the most heavily weighted dimension) but 40% on timezone, producing an overall score of ~80%. The platform surfaces the timezone gap explicitly so you can decide if it matters for your specific situation.

**Q: The results are the same every time — is the algorithm random?**  
A: No. The algorithm is fully deterministic: the same preferences always produce the same ranking. This is intentional — it makes the system predictable and auditable.

**Q: Can I save my results or share them?**  
A: Not currently. Results exist for the duration of your browser session. Closing the tab or refreshing loses the results, but you can re-run the same preferences to get identical results.

**Q: Why are there only 40 profiles?**  
A: SkillSync was built as a project-round submission with a curated synthetic dataset. The algorithm is designed to scale to any dataset size — the 40-profile pool is sufficient to demonstrate all features.

**Q: I need a skill that isn't in the list — what do I do?**  
A: The skill list is fixed to the 55 skills included in the platform. For this version, there is no way to add custom skills.

**Q: What does "complementary skills" mean on a match card?**  
A: These are skills the collaborator has that you neither listed as your own skills nor explicitly requested. They are extra value the collaboration would bring — things you didn't ask for but could benefit from.

**Q: The score breakdown weights don't add up to the labels I see in the radar chart.**  
A: The radar chart uses simplified display weights (rounded to the nearest percent for readability). The actual calculation uses the precise weights shown in the project algorithm table. The scores themselves are always computed with the precise weights.

---

## 8. Troubleshooting

### "Loading options…" takes a very long time

The backend service on Render's free tier can take 20–40 seconds to wake up after a period of inactivity. Wait for the warm-up message to appear and then wait a further 10–30 seconds. The page will load automatically — do not refresh.

If the loading persists for more than 60 seconds, try refreshing the page once.

### "Failed to load options. Please refresh the page."

The backend could not be reached. Possible causes:
- Temporary Render service outage
- Network interruption on your end

**Action:** Refresh the page. If the error persists, wait 2–3 minutes and try again.

### "Failed to find matches" after clicking Find My Matches

The match request reached the backend but an error occurred.

**Action:** Click **← Back** and then **Find My Matches** again. If the error persists, return to the landing page and start a new session.

### Results page shows "No matches above X%"

Your minimum score filter is set too high for the matches returned.

**Action:** Drag the Min score slider to the left to lower the threshold. Results will appear immediately.

### The radar chart is not visible

The radar chart requires a browser that supports inline SVG (all modern browsers do). If the chart is missing, try:
- Refreshing the page
- Switching to Chrome, Firefox, Edge, or Safari (latest version)
- Disabling browser extensions that may block inline content

### The app looks broken on mobile

SkillSync is optimised for desktop and tablet viewports (1024px+). It is usable on mobile but the multi-step wizard and results table are most comfortable on a wider screen.
