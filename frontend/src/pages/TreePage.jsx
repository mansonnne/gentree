import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Background,
  BaseEdge,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { api } from '../api'
import {
  buildTreeLayout,
  DEFAULT_LAYOUT_OPTIONS,
  pointsToPath,
} from '../treeLayout'

const {
  personWidth: W,
  personHeight: H,
  familySize: FAM,
} = DEFAULT_LAYOUT_OPTIONS

const PERSON_FOCUS_ZOOM = 1
const PERSON_FOCUS_DURATION = 550

const SEX_LABELS = {
  MALE: 'Мужской',
  FEMALE: 'Женский',
  UNKNOWN: 'Неизвестно',
}

function formatPersonName(person) {
  return [person?.last_name, person?.first_name, person?.middle_name]
    .filter(Boolean)
    .join(' ') || person?.name || 'Без имени'
}

function formatDate(value) {
  if (!value) return 'Не указано'
  const [year, month, day] = value.split('-')
  return year && month && day ? `${day}.${month}.${year}` : value
}

function SidebarField({ label, value }) {
  return (
    <div>
      <div style={{
        color: '#6b7280',
        fontSize: 11,
        fontWeight: 600,
        letterSpacing: '0.04em',
        marginBottom: 3,
        textTransform: 'uppercase',
      }}>
        {label}
      </div>
      <div style={{ color: '#111827', fontSize: 13, lineHeight: 1.45 }}>
        {value || 'Не указано'}
      </div>
    </div>
  )
}

function PersonSidebar({ summary, person, loading, error, onClose, onOpen }) {
  const displayedPerson = person || summary || {}

  return (
    <aside style={{
      width: 'clamp(280px, 25vw, 360px)',
      flexShrink: 0,
      background: '#fff',
      borderRight: '1px solid #e5e7eb',
      display: 'flex',
      flexDirection: 'column',
      minHeight: 0,
      overflowY: 'auto',
    }}>
      <div style={{
        padding: '16px 18px',
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: 12,
      }}>
        <div>
          <div style={{ color: '#6b7280', fontSize: 12, marginBottom: 4 }}>Персона</div>
          <div style={{ color: '#111827', fontSize: 17, fontWeight: 700, lineHeight: 1.3 }}>
            {formatPersonName(displayedPerson)}
          </div>
        </div>
        <button
          type="button"
          className="outline sm"
          aria-label="Закрыть информацию о персоне"
          title="Закрыть"
          onClick={onClose}
          style={{ minWidth: 32, padding: '4px 8px' }}
        >
          ×
        </button>
      </div>

      <div style={{
        padding: 18,
        display: 'flex',
        flexDirection: 'column',
        gap: 18,
        flex: 1,
      }}>
        {loading ? (
          <div style={{ color: '#6b7280', fontSize: 13 }}>Загрузка информации...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : person ? (
          <>
            <SidebarField label="Пол" value={SEX_LABELS[person.sex] || SEX_LABELS.UNKNOWN} />
            <SidebarField label="Дата рождения" value={formatDate(person.birth_date)} />
            <SidebarField label="Место рождения" value={person.birth_place} />

            {(!person.is_living || person.death_date || person.death_place) && (
              <>
                <SidebarField label="Дата смерти" value={formatDate(person.death_date)} />
                <SidebarField label="Место смерти" value={person.death_place} />
              </>
            )}

            {person.notes && (
              <div>
                <div style={{
                  color: '#6b7280',
                  fontSize: 11,
                  fontWeight: 600,
                  letterSpacing: '0.04em',
                  marginBottom: 5,
                  textTransform: 'uppercase',
                }}>
                  Примечания
                </div>
                <div style={{
                  color: '#374151',
                  fontSize: 13,
                  lineHeight: 1.5,
                  whiteSpace: 'pre-wrap',
                  overflowWrap: 'anywhere',
                }}>
                  {person.notes}
                </div>
              </div>
            )}
          </>
        ) : null}
      </div>

      <div style={{ padding: 18, borderTop: '1px solid #e5e7eb' }}>
        <button type="button" onClick={onOpen} style={{ width: '100%' }}>
          Открыть полную карточку
        </button>
      </div>
    </aside>
  )
}

function PersonNode({ data }) {
  const bg = data.sex === 'MALE'
    ? '#dbeafe'
    : data.sex === 'FEMALE'
      ? '#fce7f3'
      : '#f3f4f6'
  const selected = Boolean(data.isSelected)
  return (
    <div style={{
      width: W,
      minHeight: H,
      background: bg,
      border: selected ? '2px solid #4f46e5' : '1px solid #d1d5db',
      borderRadius: 8,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '8px 10px',
      textAlign: 'center',
      boxSizing: 'border-box',
      boxShadow: selected ? '0 0 0 3px rgba(79, 70, 229, 0.15)' : 'none',
      cursor: 'pointer',
    }}>
      <Handle type="target" position={Position.Left} id="left" style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Left} id="source-left" style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Right} id="right" style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Right} id="target-right" style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Top} id="top" style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Top} id="target-top" style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Bottom} id="bottom" style={{ opacity: 0 }} />
      <div style={{ fontWeight: 600, fontSize: 13, lineHeight: 1.3 }}>{data.name}</div>
      <div style={{ fontSize: 11, color: '#6b7280', marginTop: 2 }}>{data.years || '-'}</div>
    </div>
  )
}

function FamilyNode({ data }) {
  const former = data.kind === 'former'
  return (
    <div style={{
      width: FAM,
      height: FAM,
      borderRadius: '50%',
      background: former ? '#fff' : '#f43f5e',
      border: former ? '2px solid #9ca3af' : 'none',
      boxSizing: 'border-box',
    }}>
      <Handle type="target" position={Position.Left} id="left" style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Right} id="right" style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Top} id="top" style={{ opacity: 0 }} />
    </div>
  )
}

function RoutedEdge({ id, label, style, data }) {
  return (
    <BaseEdge
      id={id}
      path={pointsToPath(data?.points || [])}
      label={label}
      labelX={data?.labelX}
      labelY={data?.labelY}
      labelStyle={data?.labelStyle || { fontSize: 10, fill: '#6b7280' }}
      labelShowBg={Boolean(label)}
      labelBgStyle={{ fill: '#ffffff', fillOpacity: 1 }}
      labelBgPadding={[4, 2]}
      style={style}
    />
  )
}

function PersonFocusController({ personId }) {
  const { getNode, setCenter, viewportInitialized } = useReactFlow()

  useEffect(() => {
    if (!personId || !viewportInitialized) return undefined

    let secondFrame
    const firstFrame = requestAnimationFrame(() => {
      // Wait until React Flow has measured the area left after opening the sidebar.
      secondFrame = requestAnimationFrame(() => {
        const node = getNode(personId)
        if (!node) return

        const width = node.measured?.width ?? node.width ?? W
        const height = node.measured?.height ?? node.height ?? H
        void setCenter(
          node.position.x + width / 2,
          node.position.y + height / 2,
          {
            zoom: PERSON_FOCUS_ZOOM,
            duration: PERSON_FOCUS_DURATION,
            interpolate: 'smooth',
          },
        )
      })
    })

    return () => {
      cancelAnimationFrame(firstFrame)
      if (secondFrame) cancelAnimationFrame(secondFrame)
    }
  }, [getNode, personId, setCenter, viewportInitialized])

  return null
}

const nodeTypes = { person: PersonNode, family: FamilyNode }
const edgeTypes = { routed: RoutedEdge }

function DiagnosticsBanner({ diagnostics }) {
  if (!diagnostics.length) return null
  return (
    <div style={{
      padding: '8px 16px',
      background: '#fff7ed',
      borderBottom: '1px solid #fed7aa',
      color: '#9a3412',
      fontSize: 12,
    }}>
      <strong>Проблемы в связях: {diagnostics.length}.</strong>
      <ul style={{ margin: '4px 0 0', paddingLeft: 18 }}>
        {diagnostics.map(item => (
          <li key={`${item.code}-${item.relationshipIds.join('-')}`}>
            {item.personNames.join(' — ') || 'Неизвестные персоны'}
            {' · связь '}
            {item.relationshipIds.map(id => String(id).slice(0, 8)).join(', ')}
            {'. '}
            {item.message}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function TreePage() {
  const { id } = useParams()
  const nav = useNavigate()
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [diagnostics, setDiagnostics] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedPersonId, setSelectedPersonId] = useState(null)
  const [selectedPerson, setSelectedPerson] = useState(null)
  const [personLoading, setPersonLoading] = useState(false)
  const [personError, setPersonError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    setSelectedPersonId(null)
    api.getTree(id).then(tree => {
      const layout = buildTreeLayout(tree)
      setNodes(layout.nodes)
      setEdges(layout.edges)
      setDiagnostics(layout.diagnostics)
    }).catch(err => {
      setError(err.message || 'Не удалось построить дерево.')
    }).finally(() => setLoading(false))
  }, [id, setEdges, setNodes])

  useEffect(() => {
    if (!selectedPersonId) {
      setSelectedPerson(null)
      setPersonLoading(false)
      setPersonError('')
      return undefined
    }

    let active = true
    setSelectedPerson(null)
    setPersonLoading(true)
    setPersonError('')

    api.getPerson(selectedPersonId).then(person => {
      if (active) setSelectedPerson(person)
    }).catch(err => {
      if (active) setPersonError(err.message || 'Не удалось загрузить информацию о персоне.')
    }).finally(() => {
      if (active) setPersonLoading(false)
    })

    return () => {
      active = false
    }
  }, [selectedPersonId])

  const displayedNodes = useMemo(() => nodes.map(node => {
    if (node.type !== 'person') return node
    return {
      ...node,
      data: {
        ...node.data,
        isSelected: node.id === selectedPersonId,
      },
    }
  }), [nodes, selectedPersonId])

  const selectedSummary = nodes.find(node => node.id === selectedPersonId)?.data

  const closePersonSidebar = () => {
    setSelectedPersonId(null)
  }

  return (
    <div style={{ height: 'calc(100vh - 48px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{
        padding: '8px 16px',
        borderBottom: '1px solid #e5e7eb',
        background: '#fff',
        display: 'flex',
        gap: 12,
        alignItems: 'center',
      }}>
        <button className="outline sm" onClick={() => nav(`/profiles/${id}`)}>← Назад</button>
        <strong>Генеалогическое дерево</strong>
        <span style={{ fontSize: 12, color: '#6b7280' }}>
          Новейшие сверху · Синий — мужчины · Розовый — женщины · Красная — супруги · Пунктир — иные связи
        </span>
      </div>
      <DiagnosticsBanner diagnostics={diagnostics} />
      <div style={{ flex: 1, minHeight: 0, display: 'flex' }}>
        {selectedPersonId && (
          <PersonSidebar
            summary={selectedSummary}
            person={selectedPerson}
            loading={personLoading}
            error={personError}
            onClose={closePersonSidebar}
            onOpen={() => nav(`/profiles/${id}/persons/${selectedPersonId}`)}
          />
        )}
        <div style={{ flex: 1, minWidth: 0, minHeight: 0 }}>
          {loading ? (
            <div style={{ padding: 24, color: '#6b7280' }}>Загрузка...</div>
          ) : error ? (
            <div className="error" style={{ padding: 24 }}>{error}</div>
          ) : nodes.filter(node => node.type === 'person').length === 0 ? (
            <div style={{ padding: 24, color: '#6b7280' }}>Нет персон в профиле.</div>
          ) : (
            <ReactFlow
              nodes={displayedNodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={(_, node) => {
                if (node.type === 'person') setSelectedPersonId(node.id)
              }}
              onPaneClick={closePersonSidebar}
              nodeTypes={nodeTypes}
              edgeTypes={edgeTypes}
              nodesDraggable={false}
              fitView
              fitViewOptions={{ padding: 0.3 }}
              minZoom={0.1}
            >
              <PersonFocusController personId={selectedPersonId} />
              <Background gap={24} color="#e5e7eb" />
              <Controls />
              <MiniMap nodeColor={node =>
                node.type === 'family' && node.data?.kind === 'former' ? '#9ca3af' :
                  node.type === 'family' ? '#f43f5e' :
                    node.data?.sex === 'MALE' ? '#dbeafe' :
                      node.data?.sex === 'FEMALE' ? '#fce7f3' : '#f3f4f6'
              } />
            </ReactFlow>
          )}
        </div>
      </div>
    </div>
  )
}
