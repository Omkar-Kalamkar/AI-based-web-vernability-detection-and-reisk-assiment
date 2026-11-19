import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import Dashboard from './pages/Dashboard'
import NewScan from './pages/NewScan'
import Vulnerabilities from './pages/Vulnerabilities'
import RiskAssessment from './pages/RiskAssessment'
import Reports from './pages/Reports'
import History from './pages/History'
import Settings from './pages/Settings'
import Login from './pages/Login'
import Register from './pages/Register'
import { PageLoader } from './components/Loader'
import { useAuth } from './hooks/useAuth'

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()
  if (loading) return <PageLoader />
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="/scan" element={<NewScan />} />
        <Route path="/vulnerabilities" element={<Vulnerabilities />} />
        <Route path="/ai" element={<RiskAssessment />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/history" element={<History />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
