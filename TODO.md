# PullPeek: Simplified 2-Phase Development Plan

## 🎯 Reality Check
- **Team Size**: Alone
- **Timeline**: Quick to market
- **Focus**: Core value proposition only

---

## Phase 1: Working MVP (4-5 weeks)
**Goal: GitHub PR → AI-Generated Slides → Export**

### Backend Essentials
- [ ] **GitHub Integration**
  - OAuth authentication 
  - Single PR data fetching
  - Basic error handling
  - Repository access validation

- [ ] **AI Slide Generation**
  - OpenAI/Claude API integration
  - PR analysis (title, description, file changes, comments)
  - Generate 5-7 slides: Overview, Problem, Solution, Key Changes, Code Examples, Next Steps
  - Simple prompt engineering for technical content

- [ ] **Export System**
  - Generate Slidev markdown
  - Basic slide template (one clean, professional template)
  - File download functionality

### Frontend Core
- [ ] **Simple User Flow**
  - Landing page with GitHub OAuth
  - Dashboard: paste PR URL → generate → download
  - Progress indicator during generation
  - Basic slide preview (read-only)

- [ ] **Essential UI**
  - Clean, minimal interface
  - PR URL input with validation
  - Download button for markdown
  - Error states and loading states

### Tech Stack (Keep Simple)
- **Frontend**: Next.js + Tailwind + Shadcn/UI
- **Backend**: FastAPI
- **Database**: MongoDB
- **AI**: Gemini
- **Deployment**: Vercel

### Phase 1 Deliverables
✅ User can login with GitHub  
✅ Paste PR URL and get slides generated  
✅ Download Slidev markdown file  
✅ One clean, professional template  
✅ Working deployed app  

---

## Phase 2: Polish & Growth (3-4 weeks)  
**Goal: Better UX + Basic Monetization**

### Enhanced Experience
- [ ] **Improved AI Generation**
  - [ ] Better PR analysis (code complexity, impact assessment)
  - [ ] 2-3 slide templates (Technical Review, Feature Demo, Bug Fix)
  - [ ] Template auto-selection based on PR type
  - [ ] Chat-based slide editing
  - [ ] Include code snippets and diff highlights

- [ ] **Better UX**
  - [ ] Multi-input support (commits, branches, PR ranges)
  - [ ] Live slide preview with navigation
  - [ ] Slide reordering (simple drag-drop)
  - [ ] Better loading states with steps
  - [ ] Export to PDF (via Slidev)
  - [ ] Hosted presentation links (simple sharing)

- [ ] **Basic Monetization**
  - [ ] BYOK (Bring Your Own Key) system
  - [ ] Free tier: 5 generations/month with rate-limited system key

### Additional Features
- [ ] **Recent Presentations**
  - [ ] Save user's generated presentations
  - [ ] Simple dashboard to re-download/view previous slides
  - [ ] Basic presentation metadata (PR title, date, template used)

- [ ] **Social Proof**
  - [ ] Simple analytics (presentations generated, user count)
  - [ ] Basic testimonials/feedback system
  - [ ] GitHub star/fork counters on landing page

### Phase 2 Deliverables  
✅ 3 slide templates with auto-selection  
✅ Live slide preview and basic editing  
✅ PDF export and hosted links  
✅ BYOK system with simple pricing  
✅ User dashboard with presentation history  

---

## 🏗️ Simple Architecture

### API Endpoints (Simple)
```
POST /api/auth/github     # OAuth callback
GET  /api/presentations   # User's presentations
POST /api/generate        # Generate slides from PR
GET  /api/export/:id      # Download/view presentation
```

---

## 🚀 Development Timeline

### Phase 1 (4-5 weeks)
- **Week 1**: GitHub OAuth + basic UI setup
- **Week 2**: PR fetching + AI integration  
- **Week 3**: Slide generation + template creation
- **Week 4**: Export functionality + basic preview
- **Week 5**: Testing, bug fixes, deployment

### Phase 2 (3-4 weeks)  
- **Week 1**: Multiple templates + auto-selection
- **Week 2**: Live preview + basic editing
- **Week 3**: BYOK system + Stripe integration
- **Week 4**: Polish, analytics, final testing

**Total Development Time**: 7-9 weeks (~2 months)

---

## ✅ What We ARE Building
- ✅ GitHub PR → AI slides → export (core value)
- ✅ Clean, fast, reliable user experience
- ✅ Simple monetization that works
- ✅ Professional slide templates
- ✅ BYOK system for power users
- ✅ Basic user dashboard

---

## 🎯 Launch Strategy

### Phase 1 Launch (MVP)
- Post on Product Hunt, Hacker News, Reddit
- Share in developer communities
- Focus on "Show HN" type posts
- Target: 100+ signups in first week

### Phase 2 Launch (Monetization)
- Email existing users about new features
- Create content (blog posts, Twitter threads)
- Developer newsletter sponsorships
- Target: Convert 10-15% of free users to paid

**Focus**: Build something developers actually want to use, not enterprise features nobody needs.