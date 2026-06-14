const BASE = '/api/v1'

function token() { return localStorage.getItem('token') }

async function req(method, path, body) {
  const headers = {}
  if (token()) headers['Authorization'] = `Bearer ${token()}`
  if (body) headers['Content-Type'] = 'application/json'

  const res = await fetch(BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (res.status === 204) return null
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export const api = {
  // auth
  register: (d)  => req('POST', '/auth/register', d),
  login: (d)     => req('POST', '/auth/login', d),
  me: ()         => req('GET', '/auth/me'),
  updateMe: (d)  => req('PATCH', '/auth/me', d),

  // profiles
  createProfile: (d)    => req('POST', '/profiles', d),
  myProfiles: ()        => req('GET', '/profiles/my'),
  getProfile: (id)      => req('GET', `/profiles/${id}`),
  updateProfile: (id,d) => req('PATCH', `/profiles/${id}`, d),

  // persons
  createPerson: (pid,d)  => req('POST', `/profiles/${pid}/persons`, d),
  listPersons: (pid)     => req('GET', `/profiles/${pid}/persons`),
  getPerson: (id)        => req('GET', `/persons/${id}`),
  updatePerson: (id,d)   => req('PATCH', `/persons/${id}`, d),
  deletePerson: (id)     => req('DELETE', `/persons/${id}`),
  deletePersonPhoto: (id) => req('DELETE', `/persons/${id}/photo`),
  uploadPersonPhoto: async (id, blob) => {
    const form = new FormData()
    form.append('file', blob, 'photo.jpg')
    const res = await fetch(`${BASE}/persons/${id}/photo`, {
      method: 'POST',
      headers: token() ? { Authorization: `Bearer ${token()}` } : {},
      body: form,
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
    return data
  },

  // relationships
  createRelationship: (pid,d) => req('POST', `/profiles/${pid}/relationships`, d),
  listRelationships: (pid)    => req('GET', `/profiles/${pid}/relationships`),
  deleteRelationship: (id)    => req('DELETE', `/relationships/${id}`),
  getTree: (pid)              => req('GET', `/profiles/${pid}/tree`),

  // facts
  createFact: (pid,d)  => req('POST', `/persons/${pid}/facts`, d),
  listFacts: (pid)     => req('GET', `/persons/${pid}/facts`),
  updateFact: (id,d)   => req('PATCH', `/facts/${id}`, d),
  deleteFact: (id)     => req('DELETE', `/facts/${id}`),

  // archive requests
  createRequest: (pid,d) => req('POST', `/profiles/${pid}/archive-requests`, d),
  listRequests: (pid)    => req('GET', `/profiles/${pid}/archive-requests`),
  getRequest: (id)       => req('GET', `/archive-requests/${id}`),
  updateRequest: (id,d)  => req('PATCH', `/archive-requests/${id}`, d),
  changeStatus: (id,d)   => req('PATCH', `/archive-requests/${id}/status`, d),
  getHistory: (id)       => req('GET', `/archive-requests/${id}/history`),

  // notifications
  listNotifications: ()  => req('GET', '/notifications'),
  unreadCount: ()        => req('GET', '/notifications/unread-count'),
  markRead: (id)         => req('PATCH', `/notifications/${id}/read`),

  // books
  createBook: (pid,d) => req('POST', `/profiles/${pid}/book`, d),
  listBooks: (pid)   => req('GET', `/profiles/${pid}/books`),

  // documents
  deleteDoc: (id)          => req('DELETE', `/documents/${id}`),
  listDocsByPerson: (pid)  => req('GET', `/documents/by-person/${pid}`),
  uploadDoc: (formData) => {
    const headers = {}
    if (token()) headers['Authorization'] = `Bearer ${token()}`
    return fetch(BASE + '/documents', { method: 'POST', headers, body: formData })
      .then(r => r.ok ? r.json() : r.json().then(e => Promise.reject(new Error(e.detail))))
  },
  listDocsByRequest: (rid) => req('GET', `/documents/by-archive-request/${rid}`),
  downloadUrl: (id) => `${BASE}/documents/${id}/download?token=${token()}`,
}
