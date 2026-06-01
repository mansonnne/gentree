import { createContext, useContext, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AuthPage from './pages/AuthPage'
import ProfilesPage from './pages/ProfilesPage'
import ProfilePage from './pages/ProfilePage'
import PersonPage from './pages/PersonPage'
import TreePage from './pages/TreePage'
import RequestDetailPage from './pages/RequestDetailPage'

const AuthCtx = createContext(null)
export const useAuth = () => useContext(AuthCtx)

function Guard({ children }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/auth" replace />
}

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token'))

  const login = (t) => { setToken(t); localStorage.setItem('token', t) }
  const logout = () => { setToken(null); localStorage.removeItem('token') }

  return (
    <AuthCtx.Provider value={{ token, login, logout }}>
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/" element={<Guard><ProfilesPage /></Guard>} />
          <Route path="/profiles/:id" element={<Guard><ProfilePage /></Guard>} />
          <Route path="/profiles/:profileId/persons/:personId" element={<Guard><PersonPage /></Guard>} />
          <Route path="/profiles/:id/tree" element={<Guard><TreePage /></Guard>} />
          <Route path="/profiles/:profileId/requests/:requestId" element={<Guard><RequestDetailPage /></Guard>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthCtx.Provider>
  )
}
