import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'

const FACT_TYPES = ['BIRTH','DEATH','MARRIAGE','RESIDENCE','SERVICE','NOTE']
const FACT_LABELS = { BIRTH:'Рождение', DEATH:'Смерть', MARRIAGE:'Брак', RESIDENCE:'Проживание', SERVICE:'Служба', NOTE:'Заметка' }
const CONF_LABELS = { UNVERIFIED:'Не проверено', HYPOTHESIS:'Гипотеза', PROBABLE:'Вероятно', CONFIRMED:'Подтверждено' }
const CONF_OPT = ['UNVERIFIED','HYPOTHESIS','PROBABLE','CONFIRMED']
const SEX_LABEL = { MALE: 'Мужской', FEMALE: 'Женский', UNKNOWN: 'Неизвестно' }

const EMPTY_FACT = { fact_type: 'NOTE', fact_date: '', place: '', value_text: '', confidence: 'UNVERIFIED' }

export default function PersonPage() {
  const { profileId, personId } = useParams()
  const nav = useNavigate()
  const [person, setPerson] = useState(null)
  const [facts, setFacts] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FACT)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getPerson(personId).then(setPerson)
    api.listFacts(personId).then(setFacts)
  }, [personId])

  const primaryName = (p) => {
    const n = p.names?.find(n => n.is_primary) ?? p.names?.[0]
    if (!n) return '—'
    return [n.given_name, n.patronymic, n.family_name].filter(Boolean).join(' ')
  }

  const addFact = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const f = await api.createFact(personId, {
        fact_type: form.fact_type,
        fact_date: form.fact_date || null,
        place: form.place || null,
        value_text: form.value_text || null,
        confidence: form.confidence,
      })
      setFacts(prev => [...prev, f])
      setShowForm(false)
      setForm(EMPTY_FACT)
    } catch (err) { setError(err.message) }
  }

  const deleteFact = async (id) => {
    if (!confirm('Удалить факт?')) return
    await api.deleteFact(id)
    setFacts(prev => prev.filter(f => f.id !== id))
  }

  const ff = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  if (!person) return <div className="page muted">Загрузка...</div>

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 16, justifyContent: 'space-between' }}>
        <span className="link" onClick={() => nav(`/profiles/${profileId}`)}>← Профиль</span>
        <button className="danger sm" onClick={async () => {
          if (!confirm('Удалить персону?')) return
          await api.deletePerson(personId)
          nav(`/profiles/${profileId}`)
        }}>Удалить персону</button>
      </div>

      <h1 style={{ marginBottom: 4 }}>{primaryName(person)}</h1>
      <p className="muted" style={{ marginBottom: 16 }}>
        {SEX_LABEL[person.sex]}
        {person.birth_date && ` · р. ${person.birth_date}`}
        {person.death_date && ` · ум. ${person.death_date}`}
        {person.birth_place && ` · ${person.birth_place}`}
      </p>

      <hr />

      <div className="row" style={{ justifyContent: 'space-between', margin: '16px 0 12px' }}>
        <h2>Факты</h2>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Отмена' : '+ Добавить факт'}
        </button>
      </div>

      {error && <p className="error" style={{ marginBottom: 8 }}>{error}</p>}

      {showForm && (
        <form onSubmit={addFact} className="card col" style={{ marginBottom: 16 }}>
          <div className="row">
            <div className="col" style={{ flex: 1 }}>
              <label className="label">Тип</label>
              <select value={form.fact_type} onChange={ff('fact_type')}>
                {FACT_TYPES.map(t => <option key={t} value={t}>{FACT_LABELS[t]}</option>)}
              </select>
            </div>
            <div className="col" style={{ flex: 1 }}>
              <label className="label">Дата</label>
              <input type="date" value={form.fact_date} onChange={ff('fact_date')} />
            </div>
            <div className="col" style={{ flex: 1 }}>
              <label className="label">Место</label>
              <input value={form.place} onChange={ff('place')} />
            </div>
          </div>
          <div className="col">
            <label className="label">Описание</label>
            <textarea value={form.value_text} onChange={ff('value_text')} rows={2} />
          </div>
          <div className="col" style={{ maxWidth: 200 }}>
            <label className="label">Достоверность</label>
            <select value={form.confidence} onChange={ff('confidence')}>
              {CONF_OPT.map(c => <option key={c} value={c}>{CONF_LABELS[c]}</option>)}
            </select>
          </div>
          <div className="row">
            <button type="submit">Сохранить</button>
            <button type="button" className="outline" onClick={() => setShowForm(false)}>Отмена</button>
          </div>
        </form>
      )}

      {facts.length === 0 ? (
        <p className="muted">Нет фактов.</p>
      ) : (
        <table>
          <thead>
            <tr><th>Тип</th><th>Дата</th><th>Место</th><th>Описание</th><th>Достоверность</th><th></th></tr>
          </thead>
          <tbody>
            {facts.map(f => (
              <tr key={f.id}>
                <td><strong>{FACT_LABELS[f.fact_type]}</strong></td>
                <td>{f.fact_date ?? '—'}</td>
                <td>{f.place ?? '—'}</td>
                <td>{f.value_text ?? '—'}</td>
                <td><span className="badge">{CONF_LABELS[f.confidence]}</span></td>
                <td>
                  <button className="danger sm" onClick={() => deleteFact(f.id)}>×</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
