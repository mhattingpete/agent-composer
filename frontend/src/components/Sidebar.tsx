import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'

const navItems = [
  { path: '/', label: 'Chat', icon: '💬' },
  { path: '/studio', label: 'Agent Studio', icon: '🔧' },
  { path: '/teams', label: 'Team Builder', icon: '👥' },
  { path: '/mcp', label: 'MCP Manager', icon: '🔌' },
  { path: '/settings', label: 'Settings', icon: '⚙️' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 border-r border-gray-200 bg-white dark:border-dark-700 dark:bg-dark-800">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center border-b border-gray-200 px-6 dark:border-dark-700">
          <span className="text-xl font-bold text-primary-600">Agent Composer</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-4">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400'
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-dark-700'
                )
              }
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 dark:border-dark-700">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            v0.1.0 - Local-first AI Agents
          </p>
        </div>
      </div>
    </aside>
  )
}
