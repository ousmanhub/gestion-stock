import { useEffect, useState } from 'react'
import { endpoints } from '../api'

export default function Reservations() {
  const [commercant, setCommercant] = useState(null)
  const [produits, setProduits] = useState([])
  const [entrepots, setEntrepots] = useState([])
  const [reservations, setReservations] = useState([])
  const [form, setForm] = useState({ produit_id: '', entrepot_id: '', quantite: '', reference_client: '', reference_dossier: '' })

  useEffect(() => {
    init()
  }, [])

  const init = async () => {
    const commercants = await endpoints.commercants.list()
    if (commercants.data.length > 0) {
      const c = commercants.data[0]
      setCommercant(c)
      const [p, e, r] = await Promise.all([
        endpoints.produits.list(c.id),
        endpoints.entrepots.list(c.id),
        endpoints.reservations.list(c.id),
      ])
      setProduits(p.data)
      setEntrepots(e.data)
      setReservations(r.data)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!commercant) return
    await endpoints.reservations.create(commercant.id, {
      produit_id: Number(form.produit_id),
      entrepot_id: Number(form.entrepot_id),
      quantite: form.quantite,
      reference_client: form.reference_client,
      reference_dossier: form.reference_dossier,
    })
    setForm({ produit_id: '', entrepot_id: '', quantite: '', reference_client: '', reference_dossier: '' })
    const r = await endpoints.reservations.list(commercant.id)
    setReservations(r.data)
  }

  const handleCancel = async (id) => {
    if (!commercant) return
    await endpoints.reservations.cancel(commercant.id, id)
    const r = await endpoints.reservations.list(commercant.id)
    setReservations(r.data)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Réservations</h1>
      <form onSubmit={handleSubmit} className="bg-white p-4 rounded shadow mb-6 grid grid-cols-1 md:grid-cols-6 gap-4">
        <select value={form.produit_id} onChange={(e) => setForm({ ...form, produit_id: e.target.value })} className="border p-2 rounded" required>
          <option value="">Produit...</option>
          {produits.map((p) => (
            <option key={p.id} value={p.id}>{p.sku} - {p.libelle}</option>
          ))}
        </select>
        <select value={form.entrepot_id} onChange={(e) => setForm({ ...form, entrepot_id: e.target.value })} className="border p-2 rounded" required>
          <option value="">Entrepôt...</option>
          {entrepots.map((e) => (
            <option key={e.id} value={e.id}>{e.nom}</option>
          ))}
        </select>
        <input placeholder="Quantité" value={form.quantite} onChange={(e) => setForm({ ...form, quantite: e.target.value })} className="border p-2 rounded" required />
        <input placeholder="Réf. client" value={form.reference_client} onChange={(e) => setForm({ ...form, reference_client: e.target.value })} className="border p-2 rounded" />
        <input placeholder="Réf. dossier" value={form.reference_dossier} onChange={(e) => setForm({ ...form, reference_dossier: e.target.value })} className="border p-2 rounded" />
        <button type="submit" className="md:col-span-6 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">Créer la réservation</button>
      </form>

      <div className="bg-white rounded shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 text-left">Produit</th>
              <th className="p-3 text-left">Entrepôt</th>
              <th className="p-3 text-left">Quantité</th>
              <th className="p-3 text-left">Statut</th>
              <th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {reservations.map((r) => (
              <tr key={r.id} className="border-t">
                <td className="p-3">{produits.find((p) => p.id === r.produit_id)?.sku || r.produit_id}</td>
                <td className="p-3">{entrepots.find((e) => e.id === r.entrepot_id)?.nom || r.entrepot_id}</td>
                <td className="p-3">{r.quantite}</td>
                <td className="p-3 capitalize">{r.statut}</td>
                <td className="p-3">
                  {r.statut === 'en_cours' && (
                    <button onClick={() => handleCancel(r.id)} className="text-red-600 hover:underline">Annuler</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
