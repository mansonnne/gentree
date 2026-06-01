import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ReactFlow, Background, Controls, MiniMap, useNodesState, useEdgesState } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { api } from '../api'

const W = 160, H = 56

function layoutNodes(rawNodes, rawEdges) {
  const parentEdges = rawEdges.filter(e => e.data?.relType === 'PARENT_CHILD')

  // Build parent→children map
  const children = {}
  const hasParent = new Set()
  parentEdges.forEach(e => {
    if (!children[e.source]) children[e.source] = []
    children[e.source].push(e.target)
    hasParent.add(e.target)
  })

  // Assign depth via BFS from roots
  const roots = rawNodes.filter(n => !hasParent.has(n.id)).map(n => n.id)
  const depth = {}
  const queue = roots.map(r => [r, 0])
  while (queue.length) {
    const [id, d] = queue.shift()
    depth[id] = Math.max(depth[id] ?? 0, d);
    (children[id] || []).forEach(c => queue.push([c, d + 1]))
  }

  // Group by depth
  const byDepth = {}
  rawNodes.forEach(n => {
    const d = depth[n.id] ?? 0
    if (!byDepth[d]) byDepth[d] = []
    byDepth[d].push(n.id)
  })

  // Assign positions
  const pos = {}
  Object.entries(byDepth).forEach(([d, ids]) => {
    const y = parseInt(d) * 110
    const totalW = ids.length * (W + 40) - 40
    ids.forEach((id, i) => {
      pos[id] = { x: i * (W + 40) - totalW / 2, y }
    })
  })

  return rawNodes.map(n => ({ ...n, position: pos[n.id] ?? { x: 0, y: 0 } }))
}

export default function TreePage() {
  const { id } = useParams()
  const nav = useNavigate()
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getTree(id).then(tree => {
      const rawNodes = tree.nodes.map(n => {
        const nm = n.primary_name
        const name = nm ? `${nm.given_name} ${nm.family_name}` : '—'
        const years = [n.birth_date?.slice(0,4), n.death_date?.slice(0,4)].filter(Boolean).join('–')
        return {
          id: n.id,
          data: { label: <div><div style={{ fontWeight: 600 }}>{name}</div><div style={{ fontSize: 11, color: '#6b7280' }}>{years || '—'}</div></div> },
          style: {
            background: n.sex === 'MALE' ? '#dbeafe' : n.sex === 'FEMALE' ? '#fce7f3' : '#f3f4f6',
            border: '1px solid #d1d5db',
            borderRadius: 6,
            width: W,
            height: H,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '6px 10px',
          },
          position: { x: 0, y: 0 },
        }
      })

      const rawEdges = tree.edges.map(e => ({
        id: e.id,
        source: e.source_person_id,
        target: e.target_person_id,
        data: { relType: e.relationship_type },
        label: e.relationship_type === 'SPOUSE' ? '♥' : '',
        style: { stroke: e.relationship_type === 'SPOUSE' ? '#f43f5e' : '#9ca3af' },
        animated: e.relationship_type === 'SPOUSE',
        type: 'smoothstep',
      }))

      setNodes(layoutNodes(rawNodes, rawEdges))
      setEdges(rawEdges)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '8px 16px', borderBottom: '1px solid #e5e7eb', background: '#fff', display: 'flex', gap: 12, alignItems: 'center' }}>
        <button className="outline sm" onClick={() => nav(`/profiles/${id}`)}>← Назад</button>
        <strong>Генеалогическое дерево</strong>
        <span className="muted" style={{ fontSize: 12 }}>
          Синий — мужчины, розовый — женщины · пунктир — супруги
        </span>
      </div>
      <div style={{ flex: 1 }}>
        {loading ? (
          <div style={{ padding: 24, color: '#6b7280' }}>Загрузка...</div>
        ) : nodes.length === 0 ? (
          <div style={{ padding: 24, color: '#6b7280' }}>Нет персон в профиле.</div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            fitViewOptions={{ padding: 0.2 }}
          >
            <Background gap={20} color="#e5e7eb" />
            <Controls />
            <MiniMap nodeColor={n => n.style?.background ?? '#f3f4f6'} />
          </ReactFlow>
        )}
      </div>
    </div>
  )
}
