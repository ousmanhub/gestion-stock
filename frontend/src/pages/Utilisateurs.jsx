import { useEffect, useState } from 'react'
import { endpoints } from '../api'

export default function Utilisateurs() {
  const [commercant, setCommercant] = useState(null)
  const [utilisateurs, setUtilisateurs] = useState([])
  const [form, setForm] = useState({ nom: '', email: '', role: 'employe' })

  useEffect(() => {
    init()
  }, [])

  const init = async () => {
    const commercants = await endpoints.commercants.list()
    if (commercants.data.length > 0) {
      const c = commercants.data[0]
      setCommercant(c)
      await loadUsers(c.id)
    }
  }

  const loadUsers = async (id) => {
    const res = await endpoints.commercants.get(id)
    // API n'expose pas encore list utilisateurs directement; on récupère via GET commercant detail
    // Pour l'instant on laisse vide, affichage création seule
    setUtilisateurs([])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!commercant) return
    const res = await endpoints.commercants.createUser(commercant.id, form)
    setForm({ nom: '', email: '', role: 'employe' })
    if (res.status === 201) {
      alert(`Utilisateur créé. Clé API : ${res.data.api_key}`)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Utilisateurs</h1>
      <form onSubmit={handleSubmit} className="bg-white p-4 rounded shadow mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <input placeholder="Nom" value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })} className="border p-2 rounded" required />
        <input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="border p-2 rounded" />
        <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} className="border p-2 rounded">
          <option value="employe">Employé</option>
          <option value="responsable_logistique">Responsable logistique</option>
        </select>
        <button type="submit" className="md:col-span-4 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">Créer l'utilisateur</button>
      </form>

      {utilisateurs.length > 0 && (
        <div className="bg-white rounded shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="p-3 text-left">Nom</th>
                <th className="p-3 text-left">Email</th>
                <th className="p-3 text-left">Rôle</th>
              </tr>
            </thead>
            <tbody>
              {utilisateurs.map((u) => (
                <tr key={u.id} className="border-t">
                  <td className="p-3">{u.nom}</td>
                  <td className="p-3">{u.email || '-'}</td>
                  <td className="p-3">{u.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
