import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../App'

const STATUS_LABEL = {
  DRAFT: 'Черновик', IN_PROGRESS: 'В работе',
  COMPLETED: 'Завершён', ARCHIVED: 'Архив',
}

export default function ProfilesPage() {
  const [profiles, setProfiles] = useState([])
  const [title, setTitle] = useState('')
  const [error, setError] = useState('')
  const { logout } = useAuth()
  const nav = useNavigate()

  useEffect(() => {
    api.myProfiles().then(setProfiles).catch(e => setError(e.message))
  }, [])

  const create = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const p = await api.createProfile({ title: title.trim() })
      setProfiles(prev => [p, ...prev])
      setTitle('')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 24, justifyContent: 'space-between' }}>
        <h1>Мои исследования</h1>
        <button className="outline" onClick={logout}>Выйти</button>
      </div>

      <form onSubmit={create} className="row" style={{ marginBottom: 24 }}>
        <input
          style={{ flex: 1 }}
          placeholder="Название нового исследования"
          value={title}
          onChange={e => setTitle(e.target.value)}
          required
        />
        <button type="submit">Создать</button>
      </form>

      {error && <p className="error" style={{ marginBottom: 12 }}>{error}</p>}

      {profiles.length === 0 ? (
        <p className="muted">Нет исследований. Создайте первое.</p>
      ) : (
        <div className="col">
          {profiles.map(p => (
            <div
              key={p.id}
              className="card"
              style={{ cursor: 'pointer' }}
              onClick={() => nav(`/profiles/${p.id}`)}
            >
              <div className="row" style={{ justifyContent: 'space-between' }}>
                <strong>{p.title}</strong>
                <span className={`badge ${p.status.toLowerCase()}`}>
                  {STATUS_LABEL[p.status] ?? p.status}
                </span>
              </div>
              {p.description && (
                <p className="muted" style={{ marginTop: 4, fontSize: 13 }}>{p.description}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
