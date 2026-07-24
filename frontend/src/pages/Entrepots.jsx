import { useEffect, useState } from 'react'
import { endpoints } from '../api'

export default function Entrepots() {
  const [commercant, setCommercant] = useState(null)
  const [entrepots, setEntrepots] = useState([])
  const [form, setForm] = useState({ nom: '', adresse: '', contact: '' })

  useEffect(() => {
    init()
  }, [])

  const init = async () => {
    const commercants = await endpoints.commercants.list()
    if (commercants.data.length > 0) {
      const c = commercants.data[0]
      setCommercant(c)
      loadEntrepots(c.id)
    }
  }

  const loadEntrepots = async (id) => {
    const res = await endpoints.entrepots.list(id)
    setEntrepots(res.data)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!commercant) return
    try {
      console.log('Création entrepôt:', form)
      const res = await endpoints.entrepots.create(commercant.id, form)
      console.log('Réponse création entrepôt:', res.status, res.data)
      setForm({ nom: '', adresse: '', contact: '' })
      await loadEntrepots(commercant.id)
    } catch (err) {
      console.error('Erreur création entrepôt:', err)
      alert(err.response?.data?.detail || err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!commercant) return
    await endpoints.entrepots.delete(commercant.id, id)
    await loadEntrepots(commercant.id)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Entrepôts</h1>
      <form onSubmit={handleSubmit} className="bg-white p-4 rounded shadow mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <input placeholder="Nom" value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })} className="border p-2 rounded" required />
        <input placeholder="Adresse" value={form.adresse} onChange={(e) => setForm({ ...form, adresse: e.target.value })} className="border p-2 rounded" />
        <input placeholder="Contact" value={form.contact} onChange={(e) => setForm({ ...form, contact: e.target.value })} className="border p-2 rounded" />
        <button type="submit" className="md:col-span-3 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">Créer l'entrepôt</button>
      </form>

      <div className="bg-white rounded shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 text-left">Nom</th>
              <th className="p-3 text-left">Adresse</th>
              <th className="p-3 text-left">Contact</th>
              <th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {entrepots.map((e) => (
              <tr key={e.id} className="border-t">
                <td className="p-3">{e.nom}</td>
                <td className="p-3">{e.adresse || '-'}</td>
                <td className="p-3">{e.contact || '-'}</td>
                <td className="p-3">
                  <button onClick={() => handleDelete(e.id)} className="text-red-600 hover:underline">Supprimer</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
