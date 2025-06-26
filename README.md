# PullPeek: GitHub PR to Presentation Generator

## 🚀 Project Overview

**PullPeek** is a focused AI-powered application that automatically generates professional technical presentations from GitHub Pull Requests using Slidev. Transform your PR demos and code reviews into polished presentations in seconds.

### 🎯 Problem Statement

- Developers spend hours manually creating slides for PR demos and reviews
- Technical presentations lack consistency across teams
- Engineering teams need better ways to communicate code changes to stakeholders
- No simple tool exists to convert GitHub PRs into presentation-ready content

### 💡 Solution

A streamlined platform that:
- Analyzes GitHub PRs with AI (Gemini)
- Generates 5-7 professional slides automatically
- Exports clean Slidev markdown files
- Provides a simple, fast user experience

---

## 🏗️ Technical Architecture

### Simplified Tech Stack

**Frontend:**
- Next.js 14 with TypeScript
- Tailwind CSS + Shadcn/UI
- Simple, clean interface focused on core workflow

**Backend:**
- FastAPI (Python)
- MongoDB (document storage)
- GitHub API integration
- Gemini AI integration

**Infrastructure:**
- Vercel deployment
- Docker containerization
- Simple CI/CD pipeline

### Core Features (Phase 1 - MVP)

1. **GitHub Integration**
   - OAuth authentication
   - Single PR data fetching
   - Repository access validation
   - Basic error handling

2. **AI-Powered Slide Generation**
   - PR analysis (title, description, file changes, comments)
   - Generate structured slides: Overview, Problem, Solution, Key Changes, Code Examples, Next Steps
   - Simple prompt engineering for technical content

3. **Export System**
   - Generate Slidev markdown
   - One clean, professional template
   - File download functionality

4. **Simple User Flow**
   - GitHub OAuth login
   - Paste PR URL → Generate → Download
   - Basic slide preview (read-only)
   - Progress indicators and error states

---

## 🎯 Key Principles

### What We ARE Building
✅ **Core Value:** GitHub PR → Professional slides in under 30 seconds  
✅ **Simple UX:** Clean, fast, reliable experience  
✅ **Developer-Focused:** Built by developers, for developers  
✅ **Monetization Ready:** BYOK system for sustainable growth  

---

## 🤝 Contributing

This is currently a solo project focused on rapid development and market validation. Once the MVP is established, contributions will be welcomed.

### Development Philosophy
- **Ship fast, iterate faster**
- **User feedback drives features**
- **Simple solutions over complex ones**
- **Developer experience first**

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🔗 Links

- **Live Demo:** [Coming Soon]
- **Product Hunt:** [Coming Soon]
- **Documentation:** [Coming Soon]
- **Feedback:** [GitHub Issues](https://github.com/yourusername/pullpeek/issues)

---

*Built with ❤️ for developers who want to spend less time on slides and more time on code.*