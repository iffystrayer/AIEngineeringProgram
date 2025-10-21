# Playwright E2E Test - Quick Reference

## 🚀 Quick Start

```bash
cd frontend
npm install
npm run dev              # Terminal 1: Start dev server
npm run e2e             # Terminal 2: Run tests
```

## 📝 Test Commands

| Command | Purpose |
|---------|---------|
| `npm run e2e` | Run all E2E tests |
| `npm run e2e -- simple-flow.spec.ts` | Run specific test |
| `npm run e2e:ui` | Interactive UI mode |
| `npm run e2e:headed` | See browser during test |
| `npm run e2e:debug` | Debug mode |
| `npx playwright show-report` | View HTML report |

## 📂 Key Files

| File | Purpose |
|------|---------|
| `frontend/playwright.config.ts` | Playwright configuration |
| `frontend/e2e/simple-flow.spec.ts` | E2E test suite |
| `frontend/package.json` | NPM scripts |

## 🧪 Test Phases

```
Phase 1: Landing Page Verification
Phase 2: Questionnaire Initialization
Phase 3: Project Details Entry
Phase 4: Session Creation
Phase 5: Progress Tracking
Phase 6: Landing Page State
Phase 7: Session Resumption
```

## 📊 Test Data

```
User ID: test-user-{timestamp}
Project Name: AI-Powered Customer Analytics Platform
Description: Build an AI system to analyze customer behavior and predict churn
```

## 🔍 Selectors Used

```typescript
// Test IDs
page.getByTestId('start-new-button')
page.getByTestId('resume-button')

// Element IDs
page.locator('#user_id')
page.locator('#project_name')
page.locator('#description')

// Text
page.locator('h1')
page.locator('button:has-text("Start Session")')
```

## ✅ Assertions

```typescript
// Visibility
await expect(element).toBeVisible()

// Text content
await expect(element).toContainText('text')

// Count
await expect(elements).toHaveCount(5)

// Enabled/Disabled
await expect(button).toBeEnabled()
```

## 🎯 Test Flow

```
1. Navigate to http://localhost:5173
2. Verify landing page loads
3. Click "Start New Questionnaire"
4. Fill form with project details
5. Click "Start Session"
6. Verify session created
7. Verify landing page state
8. Click "View Sessions"
9. Verify session list
```

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Tests timeout | Increase timeout in config |
| Element not found | Check selector in browser DevTools |
| Backend errors | Start API: `python -m src.api.app` |
| Port already in use | Kill process on port 5173 |

## 📈 Test Metrics

- **Duration**: ~30 seconds per browser
- **Browsers**: 3 (Chromium, Firefox, WebKit)
- **Total Time**: ~90 seconds
- **Phases**: 7
- **Assertions**: 20+

## 🎨 Landing Page Elements

```
Header
├─ Title: "U-AIP Scoping Assistant"
└─ Subtitle: "Universal AI Project Scoping and Framing Protocol"

Main Content
├─ Card 1: Start New Project
│  └─ Button: "Start New Questionnaire"
├─ Card 2: Resume Session
│  └─ Button: "View Sessions"
└─ 5-Stage Process
   ├─ Business Translation
   ├─ Value Quantification
   ├─ Data Feasibility
   ├─ User Centricity
   └─ Ethical Governance
```

## 📋 Form Fields

```
User ID
├─ ID: user_id
├─ Type: text
└─ Placeholder: "Enter your user ID"

Project Name
├─ ID: project_name
├─ Type: text
└─ Placeholder: "Enter project name"

Description
├─ ID: description
├─ Type: textarea
└─ Placeholder: "Enter project description"
```

## 🔗 URLs

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | Frontend app |
| http://localhost:8000 | Backend API |
| http://localhost:9323 | Test report |

## 📚 Documentation Files

- `E2E_TEST_SUMMARY.md` - Detailed test documentation
- `PLAYWRIGHT_E2E_TEST_GUIDE.md` - Test guide
- `PLAYWRIGHT_IMPLEMENTATION_COMPLETE.md` - Implementation details
- `PLAYWRIGHT_E2E_COMPLETE_GUIDE.md` - Complete guide
- `FINAL_E2E_SUMMARY.md` - Final summary
- `PLAYWRIGHT_QUICK_REFERENCE.md` - This file

## 🎯 Test Objectives

✅ Verify landing page loads correctly
✅ Test questionnaire initialization
✅ Test form input and validation
✅ Test session creation
✅ Test progress tracking
✅ Test session management
✅ Test cross-browser compatibility

## 💡 Tips

1. **Use test IDs**: More reliable than text selectors
2. **Wait for elements**: Use `waitForSelector` for dynamic content
3. **Check console**: Look for errors in browser console
4. **Use headed mode**: See what's happening during test
5. **Debug mode**: Step through test execution
6. **Screenshots**: Captured on failure automatically

## 🚀 Next Steps

1. Run tests: `npm run e2e`
2. View report: `npx playwright show-report`
3. Debug failures: `npm run e2e:debug`
4. Add more tests: Create new `.spec.ts` files
5. Integrate CI/CD: Add to GitHub Actions

## 📞 Support

For issues or questions:
1. Check browser console for errors
2. Run in debug mode: `npm run e2e:debug`
3. View test report: `npx playwright show-report`
4. Check documentation files
5. Review test code: `frontend/e2e/simple-flow.spec.ts`

---

**Status**: 🟢 **READY FOR PRODUCTION**

