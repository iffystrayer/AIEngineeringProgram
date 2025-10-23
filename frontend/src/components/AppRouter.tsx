import { Routes, Route, Navigate } from 'react-router-dom'
import { LandingPage } from './LandingPage'
import Layout from './Layout'
import Dashboard from './pages/Dashboard'
import SessionsList from './pages/SessionsList'
import SessionDetail from './pages/SessionDetail'
import StageExecution from './pages/StageExecution'
import CharterView from './pages/CharterView'
import ConsistencyCheckPage from './pages/ConsistencyCheckPage'

export default function AppRouter() {
  return (
    <Routes>
      {/* Public route - Landing page */}
      <Route path="/" element={<LandingPage />} />

      {/* Protected routes with layout */}
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/sessions" element={<SessionsList />} />
        <Route path="/sessions/:id" element={<SessionDetail />} />
        <Route path="/sessions/:id/stage/:stageId" element={<StageExecution />} />
        <Route path="/sessions/:id/consistency" element={<ConsistencyCheckPage />} />
        <Route path="/charter/:id" element={<CharterView />} />
        {/* Additional routes for future phases */}
        {/* <Route path="/settings" element={<Settings />} /> */}
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
