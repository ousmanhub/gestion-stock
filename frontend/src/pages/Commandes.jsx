import { useEffect, useState } from 'react'
import { endpoints } from '../api'

export default function Commandes() {
  const [commercant, setCommercant] = useState(null)
  const [produits, setProduits] = useState([])
  const [entrepots, setEntrepots] = useState([])
  const [commandes, setCommandes] = useState([])
  const [form, setForm] = useState({
    produit_id: '',
    entrepot_destination_id: '',
    fournisseur_nom: '',
    fournisseur_contact: '',
    quantite_commandee: '',
    prix_unitaire_prevu: '',
    date_livraison_estimee: '',
    reference_commande: '',
  })

  useEffect(() => {
    init()
  }, [])

  const init = async () => {
    const commercants = await endpoints.commercants.list()
    if (commercants.data.length > 0) {
      const c = commercants.data[0]
      setCommercant(c)
      const [p, e, cmd] = await Promise.all([
        endpoints.produits.list(c.id),
        endpoints.entrepots.list(c.id),
        endpoints.commandes.list(c.id),
      ])
      setProduits(p.data)
      setEntrepots(e.data)
      setCommandes(cmd.data)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!commercant) return
    await endpoints.commandes.create(commercant.id, {
      produit_id: Number(form.produit_id),
      entrepot_destination_id: Number(form.entrepot_destination_id),
      fournisseur_nom: form.fournisseur_nom,
      fournisseur_contact: form.fournisseur_contact,
      quantite_commandee: form.quantite_commandee,
      prix_unitaire_prevu: form.prix_unitaire_prevu || null,
      date_livraison_estimee: form.date_livraison_estimee || null,
      reference_commande: form.reference_commande,
    })
    setForm({
      produit_id: '',
      entrepot_destination_id: '',
      fournisseur_nom: '',
      fournisseur_contact: '',
      quantite_commandee: '',
      prix_unitaire_prevu: '',
      date_livraison_estimee: '',
      reference_commande: '',
    })
    const cmd = await endpoints.commandes.list(commercant.id)
    setCommandes(cmd.data)
  }

  const action = async (id, fn, extra = {}) => {
    if (!commercant) return
    await fn(commercant.id, id, extra)
    const cmd = await endpoints.commandes.list(commercant.id)
    setCommandes(cmd.data)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Commandes fournisseurs</h1>
      <form onSubmit={handleSubmit} className="bg-white p-4 rounded shadow mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <select value={form.produit_id} onChange={(e) => setForm({ ...form, produit_id: e.target.value })} className="border p-2 rounded" required>
          <option value="">Produit...</option>
          {produits.map((p) => (
            <option key={p.id} value={p.id}>{p.sku} - {p.libelle}</option>
          ))}
        </select>
        <select value={form.entrepot_destination_id} onChange={(e) => setForm({ ...form, entrepot_destination_id: e.target.value })} className="border p-2 rounded" required>
          <option value="">Entrepôt destination...</option>
          {entrepots.map((e) => (
            <option key={e.id} value={e.id}>{e.nom}</option>
          ))}
        </select>
        <input placeholder="Fournisseur" value={form.fournisseur_nom} onChange={(e) => setForm({ ...form, fournisseur_nom: e.target.value })} className="border p-2 rounded" required />
        <input placeholder="Contact fournisseur" value={form.fournisseur_contact} onChange={(e) => setForm({ ...form, fournisseur_contact: e.target.value })} className="border p-2 rounded" />
        <input placeholder="Quantité" value={form.quantite_commandee} onChange={(e) => setForm({ ...form, quantite_commandee: e.target.value })} className="border p-2 rounded" required />
        <input placeholder="Prix unitaire prévu" value={form.prix_unitaire_prevu} onChange={(e) => setForm({ ...form, prix_unitaire_prevu: e.target.value })} className="border p-2 rounded" />
        <input type="date" value={form.date_livraison_estimee} onChange={(e) => setForm({ ...form, date_livraison_estimee: e.target.value })} className="border p-2 rounded" />
        <input placeholder="Référence commande" value={form.reference_commande} onChange={(e) => setForm({ ...form, reference_commande: e.target.value })} className="border p-2 rounded" />
        <button type="submit" className="md:col-span-4 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">Créer la commande</button>
      </form>

      <div className="bg-white rounded shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 text-left">Réf.</th>
              <th className="p-3 text-left">Fournisseur</th>
              <th className="p-3 text-left">Produit</th>
              <th className="p-3 text-left">Qté commandée</th>
              <th className="p-3 text-left">Qté reçue</th>
              <th className="p-3 text-left">Statut</th>
              <th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {commandes.map((c) => (
              <tr key={c.id} className="border-t">
                <td className="p-3">{c.reference_commande || c.id}</td>
                <td className="p-3">{c.fournisseur_nom}</td>
                <td className="p-3">{produits.find((p) => p.id === c.produit_id)?.sku || c.produit_id}</td>
                <td className="p-3">{c.quantite_commandee}</td>
                <td className="p-3">{c.quantite_recue}</td>
                <td className="p-3 capitalize">{c.statut.replace('_', ' ')}</td>
                <td className="p-3 space-x-2">
                  {c.statut === 'brouillon' && (
                    <button onClick={() => action(c.id, endpoints.commandes.send)} className="text-blue-600 hover:underline">Envoyer</button>
                  )}
                  {(c.statut === 'envoyee' || c.statut === 'partiellement_recue') && (
                    <button
                      onClick={() => {
                        const qte = prompt('Quantité reçue ?')
                        if (qte) action(c.id, endpoints.commandes.receive, { quantite: qte })
                      }}
                      className="text-green-600 hover:underline"
                    >
                      Réceptionner
                    </button>
                  )}
                  {c.statut !== 'annulee' && c.statut !== 'recue' && (
                    <button onClick={() => action(c.id, endpoints.commandes.cancel)} className="text-red-600 hover:underline">Annuler</button>
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
