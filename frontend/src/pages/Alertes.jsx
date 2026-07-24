import { useEffect, useState } from 'react'
import { endpoints } from '../api'

export default function Alertes() {
  const [commercant, setCommercant] = useState(null)
  const [alertes, setAlertes] = useState([])

  useEffect(() => {
    init()
  }, [])

  const init = async () => {
    const commercants = await endpoints.commercants.list()
    if (commercants.data.length > 0) {
      const c = commercants.data[0]
      setCommercant(c)
      const res = await endpoints.alertes.list(c.id)
      setAlertes(res.data)
    }
  }

  const badgeClass = (type) => {
    switch (type) {
      case 'negatif':
        return 'bg-red-100 text-red-700'
      case 'sous_seuil':
        return 'bg-orange-100 text-orange-700'
      case 'peremption':
        return 'bg-yellow-100 text-yellow-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Alertes</h1>
      <div className="bg-white rounded shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 text-left">Type</th>
              <th className="p-3 text-left">Produit</th>
              <th className="p-3 text-left">Entrepôt</th>
              <th className="p-3 text-left">Message</th>
            </tr>
          </thead>
          <tbody>
            {alertes.map((a, idx) => (
              <tr key={idx} className="border-t">
                <td className="p-3">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${badgeClass(a.type)}`}>
                    {a.type.replace('_', ' ')}
                  </span>
                </td>
                <td className="p-3">{a.produit_sku}</td>
                <td className="p-3">{a.entrepot_nom || '-'}</td>
                <td className="p-3">{a.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
