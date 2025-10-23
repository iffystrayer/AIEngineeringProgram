import { Routes, Route, Navigate } from 'react-router-dom'
import { LandingPage } from './LandingPage'
import Layout from './Layout'
import Dashboard from './pages/Dashboard'
import SessionsList from './pages/SessionsList'

export default function AppRouter() {
  return (
    <Routes>
      {/* Public route - Landing page */}
      <Route path="/" element={<LandingPage />} />

      {/* Protected routes with layout */}
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/sessions" element={<SessionsList />} />
        {/* Additional routes will be added in Phase 2 */}
        {/* <Route path="/sessions/:id" element={<SessionDetail />} /> */}
        {/* <Route path="/sessions/:id/stage/:stageId" element={<StageExecution />} /> */}
        {/* <Route path="/charter/:id" element={<CharterView />} /> */}
        {/* <Route path="/settings" element={<Settings />} /> */}
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
