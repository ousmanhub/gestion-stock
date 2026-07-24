import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { Package, Warehouse, ArrowLeftRight, Calendar, Truck, Bell, Users, LogOut, Home, Box } from 'lucide-react'
import { logout } from '../api'

const menu = [
  { path: '/', label: 'Tableau de bord', icon: Home },
  { path: '/produits', label: 'Produits', icon: Package },
  { path: '/entrepots', label: 'Entrepôts', icon: Warehouse },
  { path: '/mouvements', label: 'Mouvements', icon: ArrowLeftRight },
  { path: '/transferts', label: 'Transferts', icon: Box },
  { path: '/reservations', label: 'Réservations', icon: Calendar },
  { path: '/commandes', label: 'Commandes fournisseurs', icon: Truck },
  { path: '/alertes', label: 'Alertes', icon: Bell },
  { path: '/utilisateurs', label: 'Utilisateurs', icon: Users },
]

export default function Layout() {
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-gray-100">
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 text-xl font-bold">Gestion Stock</div>
        <nav className="flex-1 px-4 space-y-2">
          {menu.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2 rounded ${isActive ? 'bg-blue-600' : 'hover:bg-slate-800'}`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <button
          onClick={handleLogout}
          className="m-4 flex items-center gap-3 px-4 py-2 rounded hover:bg-slate-800"
        >
          <LogOut size={18} />
          Déconnexion
        </button>
      </aside>
      <main className="flex-1 p-8 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
