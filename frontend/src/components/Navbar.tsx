import { Link, useLocation } from 'react-router-dom'
import { FileCode, History, Settings, BarChart3 } from 'lucide-react'

export default function Navbar() {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Review', icon: FileCode },
    { path: '/history', label: 'History', icon: History },
    { path: '/config', label: 'Config', icon: Settings },
    { path: '/audit', label: 'Audit', icon: BarChart3 },
  ]

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <FileCode size={24} />
          <span>AI Code Review</span>
        </Link>
        <div className="navbar-links">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`navbar-link ${isActive ? 'active' : ''}`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}

