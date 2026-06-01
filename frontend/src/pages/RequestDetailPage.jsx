import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'

const STATUS_LABEL = {
  DRAFT: 'Черновик', PREPARED: 'Подготовлен', SENT: 'Отправлен',
  IN_PROGRESS: 'В обработке', RESPONSE_RECEIVED: 'Получен ответ',
  COMPLETED: 'Завершён', CANCELLED: 'Отменён',
}

const TRANSITIONS = {
  DRAFT: ['PREPARED', 'CANCELLED'],
  PREPARED: ['SENT', 'CANCELLED'],
  SENT: ['IN_PROGRESS', 'CANCELLED'],
  IN_PROGRESS: ['RESPONSE_RECEIVED', 'CANCELLED'],
  RESPONSE_RECEIVED: ['COMPLETED'],
  COMPLETED: [],
  CANCELLED: [],
}

export default function RequestDetailPage() {
  const { profileId, requestId } = useParams()
  const nav = useNavigate()
  const [req, setReq] = useState(null)
  const [history, setHistory] = useState([])
  const [docs, setDocs] = useState([])
  const [comment, setComment] = useState('')
  const [nextStatus, setNextStatus] = useState('')
  const [error, setError] = useState('')
  const fileRef = useRef()

  const load = () => {
    api.getRequest(requestId).then(r => {
      setReq(r)
      const allowed = TRANSITIONS[r.current_status] ?? []
      if (allowed.length) setNextStatus(allowed[0])
    })
    api.getHistory(requestId).then(setHistory)
    api.listDocsByRequest(requestId).then(setDocs)
  }

  useEffect(load, [requestId])

  const changeStatus = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const updated = await api.changeStatus(requestId, { new_status: nextStatus, comment: comment || null })
      setReq(updated)
      setComment('')
      api.getHistory(requestId).then(setHistory)
    } catch (err) { setError(err.message) }
  }

  const uploadDoc = async (e) => {
    e.preventDefault()
    const file = fileRef.current?.files?.[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    fd.append('document_kind', 'ATTACHMENT')
    fd.append('archive_request_id', requestId)
    try {
      const doc = await api.uploadDoc(fd)
      setDocs(prev => [doc, ...prev])
      fileRef.current.value = ''
    } catch (err) { setError(err.message) }
  }

  if (!req) return <div className="page muted">Загрузка...</div>

  const allowed = TRANSITIONS[req.current_status] ?? []

  return (
    <div className="page">
      <div style={{ marginBottom: 16 }}>
        <span className="link" onClick={() => nav(`/profiles/${profileId}`)}>← Профиль</span>
      </div>

      <div className="row" style={{ justifyContent: 'space-between', marginBottom: 4 }}>
        <h1 style={{ fontSize: 18 }}>{req.title}</h1>
        <span className={`badge ${req.current_status.toLowerCase()}`}>
          {STATUS_LABEL[req.current_status]}
        </span>
      </div>
      {req.requested_archive_name && (
        <p className="muted" style={{ marginBottom: 8 }}>Архив: {req.requested_archive_name}</p>
      )}
      {req.request_goal && (
        <p style={{ marginBottom: 16 }}>{req.request_goal}</p>
      )}

      <hr />

      {/* Status change */}
      {allowed.length > 0 && (
        <div style={{ margin: '16px 0' }}>
          <h2 style={{ marginBottom: 10 }}>Сменить статус</h2>
          <form onSubmit={changeStatus} className="col" style={{ maxWidth: 400 }}>
            <select value={nextStatus} onChange={e => setNextStatus(e.target.value)}>
              {allowed.map(s => <option key={s} value={s}>{STATUS_LABEL[s]}</option>)}
            </select>
            <input
              placeholder="Комментарий (необязательно)"
              value={comment}
              onChange={e => setComment(e.target.value)}
            />
            {error && <p className="error">{error}</p>}
            <div><button type="submit">Применить</button></div>
          </form>
        </div>
      )}

      <hr />

      {/* History */}
      <h2 style={{ margin: '16px 0 10px' }}>История статусов</h2>
      {history.length === 0 ? (
        <p className="muted">Нет истории.</p>
      ) : (
        <table>
          <thead>
            <tr><th>Из</th><th>В</th><th>Комментарий</th><th>Дата</th></tr>
          </thead>
          <tbody>
            {history.map(h => (
              <tr key={h.id}>
                <td className="muted">{h.from_status ? STATUS_LABEL[h.from_status] : '—'}</td>
                <td><span className={`badge ${h.to_status.toLowerCase()}`}>{STATUS_LABEL[h.to_status]}</span></td>
                <td>{h.comment ?? '—'}</td>
                <td className="muted">{new Date(h.created_at).toLocaleDateString('ru-RU')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <hr />

      {/* Documents */}
      <h2 style={{ margin: '16px 0 10px' }}>Документы</h2>
      <form onSubmit={uploadDoc} className="row" style={{ marginBottom: 12 }}>
        <input type="file" ref={fileRef} style={{ flex: 1 }} required />
        <button type="submit">Загрузить</button>
      </form>

      {docs.length === 0 ? (
        <p className="muted">Нет документов.</p>
      ) : (
        <table>
          <thead>
            <tr><th>Файл</th><th>Тип</th><th>Размер</th><th></th></tr>
          </thead>
          <tbody>
            {docs.map(d => (
              <tr key={d.id}>
                <td>{d.file_name}</td>
                <td className="muted">{d.mime_type}</td>
                <td className="muted">{(d.file_size_bytes / 1024).toFixed(1)} KB</td>
                <td>
                  <a
                    href={`/api/v1/documents/${d.id}/download`}
                    target="_blank"
                    rel="noreferrer"
                    onClick={e => {
                      e.preventDefault()
                      const token = localStorage.getItem('token')
                      fetch(`/api/v1/documents/${d.id}/download`, {
                        headers: { Authorization: `Bearer ${token}` }
                      }).then(r => r.blob()).then(blob => {
                        const url = URL.createObjectURL(blob)
                        const a = document.createElement('a')
                        a.href = url; a.download = d.file_name; a.click()
                        URL.revokeObjectURL(url)
                      })
                    }}
                  >Скачать</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
