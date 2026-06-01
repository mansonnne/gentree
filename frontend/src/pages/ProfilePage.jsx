import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'

const SEX_LABEL = { MALE: 'М', FEMALE: 'Ж', UNKNOWN: '?' }
const SEX_OPT = ['MALE', 'FEMALE', 'UNKNOWN']
const STATUS_LABEL = {
  DRAFT: 'Черновик', PREPARED: 'Подготовлен', SENT: 'Отправлен',
  IN_PROGRESS: 'В обработке', RESPONSE_RECEIVED: 'Получен ответ',
  COMPLETED: 'Завершён', CANCELLED: 'Отменён',
}

const EMPTY_PERSON = { sex: 'UNKNOWN', birth_date: '', death_date: '', birth_place: '', is_living: true,
  family_name: '', given_name: '', patronymic: '' }
const EMPTY_REQ = { title: '', request_goal: '', requested_archive_name: '' }

export default function ProfilePage() {
  const { id } = useParams()
  const nav = useNavigate()
  const [profile, setProfile] = useState(null)
  const [persons, setPersons] = useState([])
  const [requests, setRequests] = useState([])
  const [tab, setTab] = useState('persons')
  const [showPersonForm, setShowPersonForm] = useState(false)
  const [showReqForm, setShowReqForm] = useState(false)
  const [personForm, setPersonForm] = useState(EMPTY_PERSON)
  const [reqForm, setReqForm] = useState(EMPTY_REQ)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getProfile(id).then(setProfile)
    api.listPersons(id).then(setPersons)
    api.listRequests(id).then(setRequests)
  }, [id])

  const primaryName = (p) => {
    const n = p.names?.find(n => n.is_primary) ?? p.names?.[0]
    if (!n) return '—'
    return [n.given_name, n.patronymic, n.family_name].filter(Boolean).join(' ')
  }

  const addPerson = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { family_name, given_name, patronymic, sex, birth_date, death_date, birth_place, is_living } = personForm
      const p = await api.createPerson(id, {
        sex, birth_date: birth_date || null, death_date: death_date || null,
        birth_place: birth_place || null, is_living,
        primary_name: { family_name, given_name, patronymic: patronymic || null },
      })
      setPersons(prev => [...prev, p])
      setShowPersonForm(false)
      setPersonForm(EMPTY_PERSON)
    } catch (err) { setError(err.message) }
  }

  const addRequest = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const r = await api.createRequest(id, {
        title: reqForm.title,
        request_goal: reqForm.request_goal || null,
        requested_archive_name: reqForm.requested_archive_name || null,
      })
      setRequests(prev => [r, ...prev])
      setShowReqForm(false)
      setReqForm(EMPTY_REQ)
    } catch (err) { setError(err.message) }
  }

  const pf = (k) => (e) => setPersonForm(f => ({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))
  const rf = (k) => (e) => setReqForm(f => ({ ...f, [k]: e.target.value }))

  if (!profile) return <div className="page muted">Загрузка...</div>

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 4, justifyContent: 'space-between' }}>
        <span className="link" onClick={() => nav('/')}>← Исследования</span>
        <button className="outline sm" onClick={() => nav(`/profiles/${id}/tree`)}>🌳 Дерево</button>
      </div>

      <div className="row" style={{ marginBottom: 20, marginTop: 8, justifyContent: 'space-between' }}>
        <h1>{profile.title}</h1>
        <span className={`badge ${profile.status.toLowerCase()}`}>{profile.status}</span>
      </div>

      {/* Tabs */}
      <div className="row" style={{ marginBottom: 16, borderBottom: '1px solid #e5e7eb', paddingBottom: 0 }}>
        {['persons', 'requests'].map(t => (
          <button
            key={t}
            className="outline"
            style={{ borderBottom: tab === t ? '2px solid #6366f1' : '2px solid transparent', borderRadius: '4px 4px 0 0' }}
            onClick={() => setTab(t)}
          >
            {t === 'persons' ? `Персоны (${persons.length})` : `Запросы (${requests.length})`}
          </button>
        ))}
      </div>

      {error && <p className="error" style={{ marginBottom: 12 }}>{error}</p>}

      {/* Persons tab */}
      {tab === 'persons' && (
        <>
          <div className="row" style={{ justifyContent: 'space-between', marginBottom: 12 }}>
            <h2>Персоны</h2>
            <button onClick={() => setShowPersonForm(!showPersonForm)}>
              {showPersonForm ? 'Отмена' : '+ Добавить'}
            </button>
          </div>

          {showPersonForm && (
            <form onSubmit={addPerson} className="card col" style={{ marginBottom: 16 }}>
              <h3>Новая персона</h3>
              <div className="row">
                <div className="col" style={{ flex: 1 }}>
                  <label className="label">Фамилия *</label>
                  <input value={personForm.family_name} onChange={pf('family_name')} required />
                </div>
                <div className="col" style={{ flex: 1 }}>
                  <label className="label">Имя *</label>
                  <input value={personForm.given_name} onChange={pf('given_name')} required />
                </div>
                <div className="col" style={{ flex: 1 }}>
                  <label className="label">Отчество</label>
                  <input value={personForm.patronymic} onChange={pf('patronymic')} />
                </div>
              </div>
              <div className="row">
                <div className="col" style={{ flex: 1 }}>
                  <label className="label">Пол</label>
                  <select value={personForm.sex} onChange={pf('sex')}>
                    {SEX_OPT.map(s => <option key={s} value={s}>{SEX_LABEL[s]} {s}</option>)}
                  </select>
                </div>
                <div className="col" style={{ flex: 1 }}>
                  <label className="label">Дата рождения</label>
                  <input type="date" value={personForm.birth_date} onChange={pf('birth_date')} />
                </div>
                <div className="col" style={{ flex: 1 }}>
                  <label className="label">Место рождения</label>
                  <input value={personForm.birth_place} onChange={pf('birth_place')} />
                </div>
              </div>
              <div className="row">
                <label style={{ display: 'flex', gap: 6, alignItems: 'center', cursor: 'pointer' }}>
                  <input type="checkbox" checked={personForm.is_living} onChange={pf('is_living')} style={{ width: 'auto' }} />
                  Живёт
                </label>
              </div>
              <div className="row">
                <button type="submit">Сохранить</button>
                <button type="button" className="outline" onClick={() => setShowPersonForm(false)}>Отмена</button>
              </div>
            </form>
          )}

          {persons.length === 0 ? (
            <p className="muted">Нет персон.</p>
          ) : (
            <table>
              <thead>
                <tr><th>ФИО</th><th>Пол</th><th>Дата рождения</th><th>Место рождения</th></tr>
              </thead>
              <tbody>
                {persons.map(p => (
                  <tr key={p.id} style={{ cursor: 'pointer' }}
                    onClick={() => nav(`/profiles/${id}/persons/${p.id}`)}>
                    <td><strong>{primaryName(p)}</strong></td>
                    <td>{SEX_LABEL[p.sex]}</td>
                    <td>{p.birth_date ?? '—'}</td>
                    <td>{p.birth_place ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}

      {/* Requests tab */}
      {tab === 'requests' && (
        <>
          <div className="row" style={{ justifyContent: 'space-between', marginBottom: 12 }}>
            <h2>Архивные запросы</h2>
            <button onClick={() => setShowReqForm(!showReqForm)}>
              {showReqForm ? 'Отмена' : '+ Создать'}
            </button>
          </div>

          {showReqForm && (
            <form onSubmit={addRequest} className="card col" style={{ marginBottom: 16 }}>
              <h3>Новый запрос</h3>
              <div className="col">
                <label className="label">Название *</label>
                <input value={reqForm.title} onChange={rf('title')} required />
              </div>
              <div className="col">
                <label className="label">Цель запроса</label>
                <textarea value={reqForm.request_goal} onChange={rf('request_goal')} rows={2} />
              </div>
              <div className="col">
                <label className="label">Название архива</label>
                <input value={reqForm.requested_archive_name} onChange={rf('requested_archive_name')} />
              </div>
              <div className="row">
                <button type="submit">Создать</button>
                <button type="button" className="outline" onClick={() => setShowReqForm(false)}>Отмена</button>
              </div>
            </form>
          )}

          {requests.length === 0 ? (
            <p className="muted">Нет запросов.</p>
          ) : (
            <table>
              <thead>
                <tr><th>Название</th><th>Архив</th><th>Статус</th></tr>
              </thead>
              <tbody>
                {requests.map(r => (
                  <tr key={r.id} style={{ cursor: 'pointer' }}
                    onClick={() => nav(`/profiles/${id}/requests/${r.id}`)}>
                    <td><strong>{r.title}</strong></td>
                    <td className="muted">{r.requested_archive_name ?? '—'}</td>
                    <td><span className={`badge ${r.current_status.toLowerCase()}`}>
                      {STATUS_LABEL[r.current_status] ?? r.current_status}
                    </span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  )
}
