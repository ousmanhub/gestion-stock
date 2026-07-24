import { useEffect, useState } from 'react'
import { endpoints } from '../api'

export default function Produits() {
  const [commercant, setCommercant] = useState(null)
  const [produits, setProduits] = useState([])
  const [form, setForm] = useState({ sku: '', libelle: '', categorie: '', unite: 'pièce', prix_unitaire: '', stock_minimal: '' })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    init()
  }, [])

  const init = async () => {
    const commercants = await endpoints.commercants.list()
    if (commercants.data.length > 0) {
      const c = commercants.data[0]
      setCommercant(c)
      loadProduits(c.id)
    }
  }

  const loadProduits = async (id) => {
    const res = await endpoints.produits.list(id)
    setProduits(res.data)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!commercant) return
    setLoading(true)
    await endpoints.produits.create(commercant.id, {
      ...form,
      prix_unitaire: form.prix_unitaire || '0.00',
      stock_minimal: form.stock_minimal || '0.00',
    })
    setForm({ sku: '', libelle: '', categorie: '', unite: 'pièce', prix_unitaire: '', stock_minimal: '' })
    await loadProduits(commercant.id)
    setLoading(false)
  }

  const handleDelete = async (id) => {
    if (!commercant) return
    await endpoints.produits.delete(commercant.id, id)
    await loadProduits(commercant.id)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Produits</h1>
      <form onSubmit={handleSubmit} className="bg-white p-4 rounded shadow mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <input placeholder="SKU" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} className="border p-2 rounded" required />
        <input placeholder="Libellé" value={form.libelle} onChange={(e) => setForm({ ...form, libelle: e.target.value })} className="border p-2 rounded" required />
        <input placeholder="Catégorie" value={form.categorie} onChange={(e) => setForm({ ...form, categorie: e.target.value })} className="border p-2 rounded" />
        <input placeholder="Unité" value={form.unite} onChange={(e) => setForm({ ...form, unite: e.target.value })} className="border p-2 rounded" />
        <input placeholder="Prix unitaire" value={form.prix_unitaire} onChange={(e) => setForm({ ...form, prix_unitaire: e.target.value })} className="border p-2 rounded" />
        <input placeholder="Stock minimal" value={form.stock_minimal} onChange={(e) => setForm({ ...form, stock_minimal: e.target.value })} className="border p-2 rounded" />
        <button type="submit" disabled={loading} className="md:col-span-3 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          {loading ? 'Création...' : 'Créer le produit'}
        </button>
      </form>

      <div className="bg-white rounded shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 text-left">SKU</th>
              <th className="p-3 text-left">Libellé</th>
              <th className="p-3 text-left">Catégorie</th>
              <th className="p-3 text-left">Prix</th>
              <th className="p-3 text-left">Stock minimal</th>
              <th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {produits.map((p) => (
              <tr key={p.id} className="border-t">
                <td className="p-3">{p.sku}</td>
                <td className="p-3">{p.libelle}</td>
                <td className="p-3">{p.categorie || '-'}</td>
                <td className="p-3">{p.prix_unitaire}</td>
                <td className="p-3">{p.stock_minimal}</td>
                <td className="p-3">
                  <button onClick={() => handleDelete(p.id)} className="text-red-600 hover:underline">Supprimer</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
