import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useHardwareStore } from '../store/hardwareStore'
import { useEffect } from 'react'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()
  const { hardware, loading, fetchHardware } = useHardwareStore()

  useEffect(() => {
    fetchHardware()
  }, [fetchHardware])

  const navItems = [
    { name: 'Dashboard', path: '/', icon: '📊' },
    { name: 'Documents', path: '/documents', icon: '📄' },
    { name: 'Assistant', path: '/assistant', icon: '💬' },
    { name: 'Images', path: '/images', icon: '🖼️' },
    { name: 'Voice', path: '/voice', icon: '🎤' },
    { name: 'Tasks', path: '/tasks', icon: '✓' },
    { name: 'Benchmarks', path: '/benchmarks', icon: '⚡' },
    { name: 'Hardware', path: '/hardware', icon: '🔧' },
    { name: 'Privacy', path: '/privacy', icon: '🔒' },
    { name: 'Settings', path: '/settings', icon: '⚙️' },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-snapflow-900 text-white transition-all duration-300 overflow-hidden flex flex-col`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-snapflow-800">
          <div className="flex items-center gap-3">
            <div className="text-2xl">⚡</div>
            {sidebarOpen && (
              <div>
                <h1 className="text-lg font-bold">SnapFlow</h1>
                <p className="text-xs text-snapflow-300">AI Copilot</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition
                ${isActive(item.path)
                  ? 'bg-snapflow-600 text-white'
                  : 'text-snapflow-200 hover:bg-snapflow-800'
                }
              `}
              title={!sidebarOpen ? item.name : ''}
            >
              <span className="text-xl">{item.icon}</span>
              {sidebarOpen && <span className="text-sm font-medium">{item.name}</span>}
            </Link>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-snapflow-800">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full p-2 hover:bg-snapflow-800 rounded transition text-sm"
          >
            {sidebarOpen ? '←' : '→'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
          <h1 className="text-2xl font-bold text-gray-900">SnapFlow AI</h1>
          
          {/* Status Indicator */}
          <div className="flex items-center gap-4">
            {!loading && hardware && (
              <div className="flex items-center gap-2">
                <div
                  className={`w-3 h-3 rounded-full ${
                    hardware.mode.includes('Snapdragon') ? 'bg-green-500' : 'bg-yellow-500'
                  }`}
                />
                <span className="text-sm font-medium text-gray-700">
                  {hardware.mode.split(' ')[0]}
                </span>
              </div>
            )}
            <div className="text-sm text-gray-500">
              {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-auto">
          <div className="p-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}
