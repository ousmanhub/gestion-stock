import { useEffect, useState } from 'react'
import { endpoints } from '../api'

export default function Dashboard() {
  const [resume, setResume] = useState(null)
  const [commercant, setCommercant] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const commercants = await endpoints.commercants.list()
        if (commercants.data.length > 0) {
          const first = commercants.data[0]
          setCommercant(first)
          const alertes = await endpoints.alertes.resume(first.id)
          setResume(alertes.data)
        }
      } catch (err) {
        console.error(err)
      }
    }
    fetchData()
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Tableau de bord</h1>
      {commercant && (
        <div className="mb-6 text-gray-600">
          Commerçant : <span className="font-semibold">{commercant.nom}</span>
        </div>
      )}
      {resume && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded shadow">
            <div className="text-sm text-gray-500">Total alertes</div>
            <div className="text-2xl font-bold">{resume.total_alertes}</div>
          </div>
          <div className="bg-white p-4 rounded shadow text-red-600">
            <div className="text-sm">Stocks négatifs</div>
            <div className="text-2xl font-bold">{resume.stocks_negatifs}</div>
          </div>
          <div className="bg-white p-4 rounded shadow text-orange-600">
            <div className="text-sm">Sous seuils</div>
            <div className="text-2xl font-bold">{resume.sous_seuils}</div>
          </div>
          <div className="bg-white p-4 rounded shadow text-yellow-600">
            <div className="text-sm">Péremptions</div>
            <div className="text-2xl font-bold">{resume.peremptions}</div>
          </div>
        </div>
      )}
    </div>
  )
}
