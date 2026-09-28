import { useEffect, useState } from 'react'
import { useHardwareStore } from '../store/hardwareStore'
import axios from 'axios'

interface HardwareCard {
  label: string
  value: string | boolean | null
  icon: string
}

export default function Dashboard() {
  const { hardware, loading, fetchHardware } = useHardwareStore()
  const [stats, setStats] = useState({
    documents: 0,
    tasks: 0,
    models: 0,
    backends: 0
  })

  useEffect(() => {
    fetchHardware()
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const [docsRes, tasksRes, modelsRes, backendsRes] = await Promise.all([
        axios.get('/api/documents/list').catch(() => ({ data: { documents: [] } })),
        axios.get('/api/tasks/list').catch(() => ({ data: { tasks: [] } })),
        axios.get('/api/models').catch(() => ({ data: { total_models: 0 } })),
        axios.get('/api/backends').catch(() => ({ data: { total: 0 } }))
      ])

      setStats({
        documents: docsRes.data.documents?.length || 0,
        tasks: tasksRes.data.tasks?.length || 0,
        models: modelsRes.data.total_models || 0,
        backends: backendsRes.data.total || 0
      })
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Welcome to SnapFlow AI - Your private on-device AI copilot
        </p>
      </div>

      {/* Hardware Status Card */}
      {!loading && hardware && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">🖥️ Hardware Status</h2>
            <span className={`badge ${hardware.mode.includes('Snapdragon') ? 'badge-success' : 'badge-warning'}`}>
              {hardware.mode}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Platform</p>
              <p className="font-semibold text-lg">{hardware.platform}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Architecture</p>
              <p className="font-semibold text-lg">{hardware.architecture}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">NPU Available</p>
              <p className="font-semibold text-lg">
                {hardware.npu_available ? '✓ Yes' : '✗ No'}
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">GPU Available</p>
              <p className="font-semibold text-lg">
                {hardware.gpu_available ? '✓ Yes' : '✗ No'}
              </p>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600 mb-2">Available Backends</p>
            <div className="flex gap-2">
              {hardware.available_backends.map((backend) => (
                <span
                  key={backend}
                  className={`badge ${
                    backend === hardware.preferred_backend
                      ? 'badge-success'
                      : 'badge-info'
                  }`}
                >
                  {backend} {backend === hardware.preferred_backend && '(Preferred)'}
                </span>
              ))}
            </div>
          </div>

          {hardware.snapdragon_model && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm font-medium">
                🎯 Snapdragon Model: <span className="font-bold">{hardware.snapdragon_model}</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Optimized for Snapdragon AI acceleration
              </p>
            </div>
          )}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="text-3xl mb-2">📄</div>
          <p className="text-sm text-gray-600">Documents</p>
          <p className="text-2xl font-bold">{stats.documents}</p>
        </div>
        <div className="card">
          <div className="text-3xl mb-2">✓</div>
          <p className="text-sm text-gray-600">Tasks</p>
          <p className="text-2xl font-bold">{stats.tasks}</p>
        </div>
        <div className="card">
          <div className="text-3xl mb-2">🤖</div>
          <p className="text-sm text-gray-600">Models</p>
          <p className="text-2xl font-bold">{stats.models}</p>
        </div>
        <div className="card">
          <div className="text-3xl mb-2">⚙️</div>
          <p className="text-sm text-gray-600">Backends</p>
          <p className="text-2xl font-bold">{stats.backends}</p>
        </div>
      </div>

      {/* Privacy Indicator */}
      <div className="card border-l-4 border-green-500 bg-green-50">
        <div className="flex items-start gap-3">
          <div className="text-2xl">🔒</div>
          <div className="flex-1">
            <h3 className="font-bold text-green-900">Private by Default</h3>
            <ul className="text-sm text-green-800 mt-2 space-y-1">
              <li>✓ Documents stay on device</li>
              <li>✓ AI inference runs locally when supported</li>
              <li>✓ No document uploaded to cloud servers</li>
              <li>✓ Local knowledge base</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Quick Start */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">🚀 Quick Start</h2>
        <div className="space-y-3">
          <p className="text-gray-700">
            Get started with SnapFlow AI by:
          </p>
          <ol className="space-y-2 text-gray-700">
            <li><span className="font-semibold">1. Upload Documents</span> - PDF, images, text files</li>
            <li><span className="font-semibold">2. Ask Questions</span> - Use AI Assistant for RAG queries</li>
            <li><span className="font-semibold">3. Extract Tasks</span> - Automatically create action items</li>
            <li><span className="font-semibold">4. Monitor Performance</span> - Check benchmarks</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
