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
  const [editingReq, setEditingReq] = useState(false)
  const [editReqForm, setEditReqForm] = useState({})
  const [fileName, setFileName] = useState('')
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

  const startEditReq = () => {
    setEditReqForm({
      title: req.title,
      request_goal: req.request_goal ?? '',
      requested_archive_name: req.requested_archive_name ?? '',
    })
    setEditingReq(true)
  }

  const saveEditReq = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const updated = await api.updateRequest(requestId, {
        title: editReqForm.title || null,
        request_goal: editReqForm.request_goal || null,
        requested_archive_name: editReqForm.requested_archive_name || null,
      })
      setReq(updated)
      setEditingReq(false)
    } catch (err) { setError(err.message) }
  }

  const erf = (k) => (e) => setEditReqForm(f => ({ ...f, [k]: e.target.value }))

  const deleteDoc = async (id) => {
    if (!confirm('Удалить документ?')) return
    try {
      await api.deleteDoc(id)
      setDocs(prev => prev.filter(d => d.id !== id))
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
      setFileName('')
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
        <h2>{req.title}</h2>
        <div className="row" style={{ gap: 8 }}>
          <span className={`badge ${req.current_status.toLowerCase()}`}>
            {STATUS_LABEL[req.current_status]}
          </span>
          {!editingReq && (
            <button className="outline sm" onClick={startEditReq}>Редактировать</button>
          )}
        </div>
      </div>
      {req.requested_archive_name && (
        <p className="muted" style={{ marginBottom: 8 }}>Архив: {req.requested_archive_name}</p>
      )}
      {req.request_goal && (
        <p style={{ marginBottom: 16 }}>{req.request_goal}</p>
      )}

      {editingReq && (
        <form onSubmit={saveEditReq} className="card col" style={{ marginBottom: 16 }}>
          <h3 style={{ marginBottom: 10 }}>Редактирование запроса</h3>
          <div className="col">
            <label className="label">Название</label>
            <input value={editReqForm.title} onChange={erf('title')} required />
          </div>
          <div className="col">
            <label className="label">Цель запроса</label>
            <textarea value={editReqForm.request_goal} onChange={erf('request_goal')} rows={2} />
          </div>
          <div className="col">
            <label className="label">Название архива</label>
            <input value={editReqForm.requested_archive_name} onChange={erf('requested_archive_name')} />
          </div>
          {error && <p className="error">{error}</p>}
          <div className="row">
            <button type="submit">Сохранить</button>
            <button type="button" className="outline" onClick={() => setEditingReq(false)}>Отмена</button>
          </div>
        </form>
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
        <input
          type="file"
          ref={fileRef}
          style={{ display: 'none' }}
          onChange={e => setFileName(e.target.files?.[0]?.name || '')}
          required
        />
        <button type="button" className="outline" onClick={() => fileRef.current?.click()}>
          Выбрать файл
        </button>
        <span style={{ flex: 1, color: fileName ? '#1a1208' : '#7a6e62', fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {fileName || 'Файл не выбран'}
        </span>
        <button type="submit" disabled={!fileName}>Загрузить</button>
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
                <td style={{ whiteSpace: 'nowrap' }}>
                  <a
                    href="#"
                    style={{ marginRight: 12 }}
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
                  <button className="danger sm" onClick={() => deleteDoc(d.id)}>×</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
