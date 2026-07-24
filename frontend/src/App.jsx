import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Produits from './pages/Produits'
import Entrepots from './pages/Entrepots'
import Mouvements from './pages/Mouvements'
import Transferts from './pages/Transferts'
import Reservations from './pages/Reservations'
import Commandes from './pages/Commandes'
import Alertes from './pages/Alertes'
import Utilisateurs from './pages/Utilisateurs'

function PrivateRoute({ children }) {
  const apiKey = localStorage.getItem('api_key')
  return apiKey ? children : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="produits" element={<Produits />} />
          <Route path="entrepots" element={<Entrepots />} />
          <Route path="mouvements" element={<Mouvements />} />
          <Route path="transferts" element={<Transferts />} />
          <Route path="reservations" element={<Reservations />} />
          <Route path="commandes" element={<Commandes />} />
          <Route path="alertes" element={<Alertes />} />
          <Route path="utilisateurs" element={<Utilisateurs />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
