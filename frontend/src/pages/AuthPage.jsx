import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../App'

export default function AuthPage() {
  const [tab, setTab] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [firstName, setFirstName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const nav = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (tab === 'register') {
        await api.register({ email, password, first_name: firstName || null })
      }
      const { access_token } = await api.login({ email, password })
      login(access_token)
      nav('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: '100px auto', padding: '0 16px' }}>
      <h1 style={{ marginBottom: 8 }}>dinastia</h1>
      <p className="muted" style={{ marginBottom: 24 }}>Система генеалогических исследований</p>

      <div className="row" style={{ marginBottom: 16 }}>
        <button className={tab === 'login' ? '' : 'outline'} onClick={() => setTab('login')}>
          Войти
        </button>
        <button className={tab === 'register' ? '' : 'outline'} onClick={() => setTab('register')}>
          Регистрация
        </button>
      </div>

      <form onSubmit={submit} className="col">
        {tab === 'register' && (
          <input
            placeholder="Имя (необязательно)"
            value={firstName}
            onChange={e => setFirstName(e.target.value)}
          />
        )}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Пароль (минимум 8 символов)"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? '...' : tab === 'login' ? 'Войти' : 'Зарегистрироваться'}
        </button>
      </form>
    </div>
  )
}
