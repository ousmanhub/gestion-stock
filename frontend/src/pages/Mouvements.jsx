import { useEffect, useState } from 'react'
import { endpoints } from '../api'

export default function Mouvements() {
  const [commercant, setCommercant] = useState(null)
  const [produits, setProduits] = useState([])
  const [entrepots, setEntrepots] = useState([])
  const [mouvements, setMouvements] = useState([])
  const [form, setForm] = useState({
    produit_id: '',
    entrepot_id: '',
    type_mouvement: 'entree',
    quantite: '',
    prix_unitaire_mouvement: '',
    reference_document: '',
  })

  useEffect(() => {
    init()
  }, [])

  const init = async () => {
    const commercants = await endpoints.commercants.list()
    if (commercants.data.length > 0) {
      const c = commercants.data[0]
      setCommercant(c)
      const [p, e, m] = await Promise.all([
        endpoints.produits.list(c.id),
        endpoints.entrepots.list(c.id),
        endpoints.mouvements.list(c.id),
      ])
      setProduits(p.data)
      setEntrepots(e.data)
      setMouvements(m.data)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!commercant) return
    await endpoints.mouvements.create(commercant.id, {
      ...form,
      quantite: form.quantite,
      prix_unitaire_mouvement: form.prix_unitaire_mouvement || null,
    })
    setForm({ produit_id: '', entrepot_id: '', type_mouvement: 'entree', quantite: '', prix_unitaire_mouvement: '', reference_document: '' })
    const m = await endpoints.mouvements.list(commercant.id)
    setMouvements(m.data)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Mouvements de stock</h1>
      <form onSubmit={handleSubmit} className="bg-white p-4 rounded shadow mb-6 grid grid-cols-1 md:grid-cols-6 gap-4">
        <select
          value={form.produit_id}
          onChange={(e) => setForm({ ...form, produit_id: Number(e.target.value) })}
          className="border p-2 rounded"
          required
        >
          <option value="">Produit...</option>
          {produits.map((p) => (
            <option key={p.id} value={p.id}>{p.sku} - {p.libelle}</option>
          ))}
        </select>
        <select
          value={form.entrepot_id}
          onChange={(e) => setForm({ ...form, entrepot_id: Number(e.target.value) })}
          className="border p-2 rounded"
          required
        >
          <option value="">Entrepôt...</option>
          {entrepots.map((e) => (
            <option key={e.id} value={e.id}>{e.nom}</option>
          ))}
        </select>
        <select
          value={form.type_mouvement}
          onChange={(e) => setForm({ ...form, type_mouvement: e.target.value })}
          className="border p-2 rounded"
        >
          <option value="entree">Entrée</option>
          <option value="sortie">Sortie</option>
          <option value="ajustement">Ajustement</option>
        </select>
        <input placeholder="Quantité" value={form.quantite} onChange={(e) => setForm({ ...form, quantite: e.target.value })} className="border p-2 rounded" required />
        <input placeholder="Prix unitaire" value={form.prix_unitaire_mouvement} onChange={(e) => setForm({ ...form, prix_unitaire_mouvement: e.target.value })} className="border p-2 rounded" />
        <input placeholder="Référence doc" value={form.reference_document} onChange={(e) => setForm({ ...form, reference_document: e.target.value })} className="border p-2 rounded" />
        <button type="submit" className="md:col-span-6 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">Enregistrer le mouvement</button>
      </form>

      <div className="bg-white rounded shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 text-left">Type</th>
              <th className="p-3 text-left">Produit</th>
              <th className="p-3 text-left">Entrepôt</th>
              <th className="p-3 text-left">Quantité</th>
              <th className="p-3 text-left">Date</th>
            </tr>
          </thead>
          <tbody>
            {mouvements.map((m) => (
              <tr key={m.id} className="border-t">
                <td className="p-3 capitalize">{m.type_mouvement}</td>
                <td className="p-3">{produits.find((p) => p.id === m.produit_id)?.sku || m.produit_id}</td>
                <td className="p-3">{entrepots.find((e) => e.id === m.entrepot_id)?.nom || m.entrepot_id}</td>
                <td className="p-3">{m.quantite}</td>
                <td className="p-3">{new Date(m.date_mouvement).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
