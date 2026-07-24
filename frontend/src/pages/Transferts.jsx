import { useEffect, useState } from 'react'
import { endpoints } from '../api'

export default function Transferts() {
  const [commercant, setCommercant] = useState(null)
  const [produits, setProduits] = useState([])
  const [entrepots, setEntrepots] = useState([])
  const [form, setForm] = useState({ produit_id: '', entrepot_source_id: '', entrepot_destination_id: '', quantite: '' })

  useEffect(() => {
    init()
  }, [])

  const init = async () => {
    const commercants = await endpoints.commercants.list()
    if (commercants.data.length > 0) {
      const c = commercants.data[0]
      setCommercant(c)
      const [p, e] = await Promise.all([endpoints.produits.list(c.id), endpoints.entrepots.list(c.id)])
      setProduits(p.data)
      setEntrepots(e.data)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!commercant) return
    await endpoints.transferts.create(commercant.id, {
      produit_id: Number(form.produit_id),
      entrepot_source_id: Number(form.entrepot_source_id),
      entrepot_destination_id: Number(form.entrepot_destination_id),
      quantite: form.quantite,
    })
    setForm({ produit_id: '', entrepot_source_id: '', entrepot_destination_id: '', quantite: '' })
    alert('Transfert effectué')
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Transferts inter-entrepôts</h1>
      <form onSubmit={handleSubmit} className="bg-white p-4 rounded shadow mb-6 grid grid-cols-1 md:grid-cols-5 gap-4">
        <select value={form.produit_id} onChange={(e) => setForm({ ...form, produit_id: e.target.value })} className="border p-2 rounded" required>
          <option value="">Produit...</option>
          {produits.map((p) => (
            <option key={p.id} value={p.id}>{p.sku} - {p.libelle}</option>
          ))}
        </select>
        <select value={form.entrepot_source_id} onChange={(e) => setForm({ ...form, entrepot_source_id: e.target.value })} className="border p-2 rounded" required>
          <option value="">Source...</option>
          {entrepots.map((e) => (
            <option key={e.id} value={e.id}>{e.nom}</option>
          ))}
        </select>
        <select value={form.entrepot_destination_id} onChange={(e) => setForm({ ...form, entrepot_destination_id: e.target.value })} className="border p-2 rounded" required>
          <option value="">Destination...</option>
          {entrepots.map((e) => (
            <option key={e.id} value={e.id}>{e.nom}</option>
          ))}
        </select>
        <input placeholder="Quantité" value={form.quantite} onChange={(e) => setForm({ ...form, quantite: e.target.value })} className="border p-2 rounded" required />
        <button type="submit" className="md:col-span-5 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">Effectuer le transfert</button>
      </form>
    </div>
  )
}
