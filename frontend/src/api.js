import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('api_key')
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey
  }
  return config
})

export default api

export async function login(apiKey) {
  const response = await api.get('/commercants/', { headers: { 'X-API-Key': apiKey } })
  if (response.status === 200) {
    localStorage.setItem('api_key', apiKey)
    return true
  }
  return false
}

export function logout() {
  localStorage.removeItem('api_key')
}

export function getApiKey() {
  return localStorage.getItem('api_key')
}

export const endpoints = {
  health: () => api.get('/health'),
  commercants: {
    list: () => api.get('/commercants/'),
    create: (data) => api.post('/commercants/', data),
    get: (id) => api.get(`/commercants/${id}`),
    update: (id, data) => api.patch(`/commercants/${id}`, data),
    delete: (id) => api.delete(`/commercants/${id}`),
    createUser: (id, data) => api.post(`/commercants/${id}/utilisateurs`, data),
  },
  produits: {
    list: (commercantId) => api.get(`/commercants/${commercantId}/produits/`),
    create: (commercantId, data) => api.post(`/commercants/${commercantId}/produits/`, data),
    update: (commercantId, id, data) => api.patch(`/commercants/${commercantId}/produits/${id}`, data),
    delete: (commercantId, id) => api.delete(`/commercants/${commercantId}/produits/${id}`),
  },
  entrepots: {
    list: (commercantId) => api.get(`/commercants/${commercantId}/entrepots/`),
    create: (commercantId, data) => api.post(`/commercants/${commercantId}/entrepots/`, data),
    update: (commercantId, id, data) => api.patch(`/commercants/${commercantId}/entrepots/${id}`, data),
    delete: (commercantId, id) => api.delete(`/commercants/${commercantId}/entrepots/${id}`),
  },
  mouvements: {
    list: (commercantId) => api.get(`/commercants/${commercantId}/mouvements/`),
    create: (commercantId, data) => api.post(`/commercants/${commercantId}/mouvements/`, data),
  },
  transferts: {
    create: (commercantId, data) => api.post(`/commercants/${commercantId}/transferts/`, data),
  },
  reservations: {
    list: (commercantId) => api.get(`/commercants/${commercantId}/reservations/`),
    create: (commercantId, data) => api.post(`/commercants/${commercantId}/reservations/`, data),
    cancel: (commercantId, id) => api.post(`/commercants/${commercantId}/reservations/${id}/annuler`),
  },
  commandes: {
    list: (commercantId) => api.get(`/commercants/${commercantId}/commandes-fournisseurs`),
    create: (commercantId, data) => api.post(`/commercants/${commercantId}/commandes-fournisseurs`, data),
    send: (commercantId, id) => api.post(`/commercants/${commercantId}/commandes-fournisseurs/${id}/envoyer`),
    receive: (commercantId, id, data) => api.post(`/commercants/${commercantId}/commandes-fournisseurs/${id}/receptionner`, data),
    cancel: (commercantId, id) => api.post(`/commercants/${commercantId}/commandes-fournisseurs/${id}/annuler`),
  },
  alertes: {
    list: (commercantId) => api.get(`/commercants/${commercantId}/alertes/`),
    resume: (commercantId) => api.get(`/commercants/${commercantId}/alertes/resume`),
  },
}
