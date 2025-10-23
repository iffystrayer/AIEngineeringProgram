import { Outlet, Link, useLocation } from 'react-router-dom'
import { ReactNode } from 'react'

interface LayoutProps {
  children?: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar Navigation */}
      <nav
        data-testid="sidebar"
        className="w-64 bg-white border-r border-gray-200 shadow-sm"
      >
        <div className="h-full flex flex-col">
          {/* Logo/Brand */}
          <div className="px-6 py-8 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-indigo-600">Charter AI</h1>
            <p className="text-sm text-gray-600 mt-1">
              Data Governance Framework
            </p>
          </div>

          {/* Navigation Links */}
          <ul className="flex-1 px-4 py-8 space-y-2">
            <li>
              <Link
                to="/dashboard"
                className={`block px-4 py-3 rounded-lg font-medium transition-colors ${
                  isActive('/dashboard')
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                Dashboard
              </Link>
            </li>
            <li>
              <Link
                to="/sessions"
                className={`block px-4 py-3 rounded-lg font-medium transition-colors ${
                  isActive('/sessions')
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                All Sessions
              </Link>
            </li>
          </ul>

          {/* Footer/User info placeholder */}
          <div className="px-6 py-4 border-t border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                <span className="text-sm font-bold text-indigo-600">U</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  User
                </p>
                <p className="text-xs text-gray-500 truncate">user@example.com</p>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main role="main" className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto px-6 py-8">
          {children || <Outlet />}
        </div>
      </main>
    </div>
  )
}
