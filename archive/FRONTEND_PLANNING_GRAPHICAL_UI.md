# Graphical Frontend Planning: Non-Technical User Interface
**Date:** October 19, 2025 | **Phase:** Post-Phase 1 | **Target Users:** Non-technical AI stakeholders

---

## 🎯 VISION

Transform the CLI-only interface into a **professional web application** that enables non-technical users (executives, product managers, ethics officers) to:
- Start new U-AIP scoping sessions without training
- Understand complex AI evaluation concepts through visual guidance
- Track progress with clear visual indicators
- Export professional charters with one click
- Collaborate with team members (future)

---

## 📊 USER PERSONAS

### 1. AI Product Manager (Primary)
- **Tech Level:** Medium (understands APIs, not developers)
- **Goals:** Quickly scope AI projects, get governance decisions
- **Pain Points:** CLI is intimidating, wants visual progress
- **Needs:** Clear UI, progress tracking, export functionality

### 2. Executive Stakeholder (Primary)
- **Tech Level:** Low (non-technical)
- **Goals:** Review project charters, make go/no-go decisions
- **Pain Points:** Doesn't understand technical jargon
- **Needs:** Plain language, visual dashboards, summary reports

### 3. Ethics Officer (Secondary)
- **Tech Level:** Medium (understands ethics, not tech)
- **Goals:** Review ethical risk assessments, approve governance decisions
- **Pain Points:** Complex risk calculations, unclear rationale
- **Needs:** Risk visualization, decision rationale, audit trail

### 4. Data Science Lead (Secondary)
- **Tech Level:** High (technical, wants details)
- **Goals:** Validate data feasibility, review metrics
- **Pain Points:** Wants to drill into details
- **Needs:** Detailed views, export options, technical depth

---

## 🏗️ ARCHITECTURE

### Tech Stack Recommendation
```
Frontend:
  - Framework: React 18 + TypeScript (modern, component-based)
  - Build Tool: Vite (fast, modern)
  - UI Library: shadcn/ui (accessible, professional)
  - State Management: TanStack Query (server state)
  - Styling: Tailwind CSS (utility-first, responsive)
  - Charts: Recharts (React-native, accessible)
  - Forms: React Hook Form + Zod (type-safe)

Backend:
  - Existing: Python FastAPI (add REST API layer)
  - Database: PostgreSQL (existing)
  - Authentication: JWT tokens
  - API Documentation: OpenAPI/Swagger

Deployment:
  - Frontend: Vercel or Netlify (serverless)
  - Backend: Docker + Kubernetes (existing)
  - Database: PostgreSQL (existing)
```

---

## 📱 USER FLOWS

### Flow 1: Start New Session
```
1. User lands on homepage
2. Clicks "Start New Session"
3. Enters basic info (name, email, project title)
4. System creates session
5. Redirects to Stage 1 interview
```

### Flow 2: Resume Session
```
1. User lands on homepage
2. Clicks "My Sessions"
3. Sees list of sessions with status
4. Clicks "Resume" on desired session
5. Redirects to current stage
```

### Flow 3: View Charter
```
1. User completes all 5 stages
2. System generates charter
3. User sees charter preview
4. Clicks "Export" to download (PDF/Markdown/JSON)
5. Charter downloaded
```

### Flow 4: Review Governance Decision
```
1. User completes Stage 5 (Ethics)
2. System shows governance decision (Proceed/Revise/Halt)
3. User sees risk breakdown visualization
4. User can drill into specific risks
5. User can export decision report
```

---

## 🎨 UI COMPONENTS & SCREENS

### Screen 1: Homepage/Dashboard
**Purpose:** Entry point, session management
**Components:**
- Header with logo, user menu
- Hero section: "Welcome to U-AIP Scoping Assistant"
- CTA buttons: "Start New Session", "My Sessions"
- Recent sessions list (if logged in)
- Help section with video tutorials

**Wireframe:**
```
┌─────────────────────────────────────────┐
│ Logo          [User Menu]               │
├─────────────────────────────────────────┤
│                                         │
│  Welcome to U-AIP Scoping Assistant    │
│                                         │
│  [Start New Session]  [My Sessions]    │
│                                         │
├─────────────────────────────────────────┤
│ Recent Sessions:                        │
│ ┌─────────────────────────────────────┐ │
│ │ Project: Churn Prediction           │ │
│ │ Stage: 3/5  Status: In Progress     │ │
│ │ [Resume] [View] [Delete]            │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Screen 2: Interview Stage
**Purpose:** Conduct interview for each stage
**Components:**
- Progress bar (Stage X of 5)
- Current question display
- Response input (textarea)
- Quality feedback (if score <7)
- Navigation buttons (Previous, Next, Save)
- Help panel (collapsible)

**Wireframe:**
```
┌─────────────────────────────────────────┐
│ Stage 1: Business Translation  [?]      │
│ ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
├─────────────────────────────────────────┤
│                                         │
│ Question 1 of 4:                        │
│ "What is the core business problem?"    │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ [Your response here...]             │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ⚠️ Response quality: 5/10               │
│ "Too vague. Please be more specific"    │
│                                         │
│ [Previous] [Next] [Save & Exit]         │
└─────────────────────────────────────────┘
```

### Screen 3: Stage Summary
**Purpose:** Review stage deliverable before progression
**Components:**
- Stage deliverable (formatted)
- Quality metrics
- Validation status
- Edit button
- Proceed button

**Wireframe:**
```
┌─────────────────────────────────────────┐
│ Stage 1 Summary: Problem Statement      │
├─────────────────────────────────────────┤
│                                         │
│ Problem Statement:                      │
│ ┌─────────────────────────────────────┐ │
│ │ [Generated problem statement]       │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ML Archetype: Classification            │
│ AI Suitability: High                    │
│ Validation: ✅ PASSED                   │
│                                         │
│ [Edit] [Proceed to Stage 2]             │
└─────────────────────────────────────────┘
```

### Screen 4: Charter Preview
**Purpose:** Show final charter before export
**Components:**
- Charter sections (tabbed)
- Governance decision (prominent)
- Risk visualization
- Export buttons
- Print button

**Wireframe:**
```
┌─────────────────────────────────────────┐
│ AI Project Charter                      │
├─────────────────────────────────────────┤
│ [Overview] [Metrics] [Data] [Users]     │
│ [Ethics] [Decision] [Export]            │
├─────────────────────────────────────────┤
│                                         │
│ Governance Decision: PROCEED ✅         │
│                                         │
│ Risk Assessment:                        │
│ ┌─────────────────────────────────────┐ │
│ │ Fairness:      ████░░░░░░ 0.3      │ │
│ │ Transparency:  ██░░░░░░░░ 0.2      │ │
│ │ Accountability:███░░░░░░░ 0.4      │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Export PDF] [Export Markdown] [Print]  │
└─────────────────────────────────────────┘
```

### Screen 5: Risk Dashboard
**Purpose:** Visualize ethical risks and governance decision
**Components:**
- Risk gauge (0-1 scale)
- Risk breakdown by principle
- High-risk flags
- Decision rationale
- Drill-down capability

**Wireframe:**
```
┌─────────────────────────────────────────┐
│ Ethical Risk Assessment                 │
├─────────────────────────────────────────┤
│                                         │
│ Overall Risk Level:                     │
│ ┌─────────────────────────────────────┐ │
│ │        ████░░░░░░░░░░░░░░░░░░░░░░ │ │
│ │        0.35 (ACCEPTABLE)            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Risk by Principle:                      │
│ • Fairness: 0.3 (Acceptable)            │
│ • Transparency: 0.2 (Low)               │
│ • Accountability: 0.4 (Acceptable)      │
│ • Privacy: 0.25 (Low)                   │
│ • Security: 0.15 (Low)                  │
│                                         │
│ Decision: PROCEED                       │
│ Rationale: All risks within acceptable  │
│ thresholds. Project approved.           │
└─────────────────────────────────────────┘
```

---

## 🔌 API ENDPOINTS NEEDED

### Session Management
```
POST   /api/sessions              - Create new session
GET    /api/sessions              - List user sessions
GET    /api/sessions/{id}         - Get session details
PUT    /api/sessions/{id}         - Update session
DELETE /api/sessions/{id}         - Delete session
POST   /api/sessions/{id}/resume  - Resume session
```

### Interview Flow
```
POST   /api/sessions/{id}/stages/{stage}/questions  - Get questions
POST   /api/sessions/{id}/stages/{stage}/responses  - Submit response
GET    /api/sessions/{id}/stages/{stage}/summary    - Get stage summary
POST   /api/sessions/{id}/stages/{stage}/validate   - Validate stage
```

### Charter & Export
```
GET    /api/sessions/{id}/charter           - Get charter
POST   /api/sessions/{id}/charter/export    - Export charter
GET    /api/sessions/{id}/charter/preview   - Preview charter
```

### Governance & Risk
```
GET    /api/sessions/{id}/governance-decision  - Get decision
GET    /api/sessions/{id}/risk-assessment      - Get risk data
```

---

## 📋 IMPLEMENTATION PHASES

### Phase 2A: Backend API Layer (1-2 weeks)
- Create FastAPI REST endpoints
- Add authentication (JWT)
- Add request/response validation
- Add error handling
- Add API documentation (Swagger)

### Phase 2B: Frontend Foundation (1-2 weeks)
- Set up React + TypeScript project
- Create component library
- Implement routing
- Set up state management
- Create authentication flow

### Phase 2C: Core Screens (2-3 weeks)
- Homepage/Dashboard
- Interview Stage screen
- Stage Summary screen
- Charter Preview screen

### Phase 2D: Advanced Features (1-2 weeks)
- Risk Dashboard
- Export functionality
- Session management
- Help/Tutorial system

### Phase 2E: Polish & Testing (1-2 weeks)
- UI/UX refinement
- Accessibility (WCAG 2.1 AA)
- Performance optimization
- E2E testing
- User testing

---

## 🎯 SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to start session | <2 min | User testing |
| Session completion rate | >85% | Analytics |
| User satisfaction (NPS) | >50 | Post-session survey |
| Page load time | <2 sec | Lighthouse |
| Accessibility score | >95 | axe DevTools |
| Mobile responsiveness | 100% | Responsive testing |

---

## 🔐 Security Considerations

- ✅ JWT authentication
- ✅ HTTPS only
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Input validation
- ✅ PII sanitization
- ✅ Session timeout
- ✅ Audit logging

---

## 📊 ESTIMATED EFFORT

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 2A (Backend API) | 1-2 weeks | 40-60 hours |
| Phase 2B (Frontend Foundation) | 1-2 weeks | 40-60 hours |
| Phase 2C (Core Screens) | 2-3 weeks | 80-120 hours |
| Phase 2D (Advanced Features) | 1-2 weeks | 40-60 hours |
| Phase 2E (Polish & Testing) | 1-2 weeks | 40-60 hours |
| **TOTAL** | **6-11 weeks** | **240-360 hours** |

---

## 🚀 RECOMMENDATION

**After Phase 1 (2-3 days):** System is functionally complete with CLI
**Phase 2 (6-11 weeks):** Add professional web UI for non-technical users
**Result:** Production-ready system accessible to all stakeholders

---

**Next Steps:**
1. Complete Phase 1 (atomic tasks)
2. Review Phase 2 planning
3. Prioritize Phase 2 phases based on user feedback
4. Begin Phase 2A (Backend API) in parallel with Phase 1 completion

