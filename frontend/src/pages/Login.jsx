import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { endpoints, logout } from '../api'

export default function Login() {
  const [apiKey, setApiKey] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await endpoints.health()
      const response = await endpoints.commercants.list()
      if (response.status === 200) {
        localStorage.setItem('api_key', apiKey)
        navigate('/')
      }
    } catch (err) {
      setError('Clé API invalide ou serveur inaccessible')
    }
  }

  logout()

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Gestion de Stock</h1>
        {error && <div className="mb-4 text-red-600 text-sm">{error}</div>}
        <label className="block text-sm font-medium mb-2">X-API-Key</label>
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          className="w-full border p-2 rounded mb-4"
          placeholder="Collez votre clé API"
          required
        />
        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          Connexion
        </button>
      </form>
    </div>
  )
}
