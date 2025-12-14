import { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, DollarSign } from 'lucide-react'

interface UsageStats {
  period_days: number
  total_requests: number
  by_model: Record<string, number>
  total_cost: number
  average_per_day: number
}

export default function Audit() {
  const [stats, setStats] = useState<UsageStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const response = await fetch('/api/v1/audit/usage?days=30')
      if (!response.ok) throw new Error('Failed to load stats')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="page-container">Loading...</div>
  }

  if (!stats) {
    return <div className="page-container">No data available</div>
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>API Usage Audit</h1>
        <p>Track your AI API usage and costs</p>
      </div>

      <div className="audit-stats">
        <div className="stat-card">
          <BarChart3 size={32} />
          <div>
            <h3>Total Requests</h3>
            <div className="stat-value">{stats.total_requests}</div>
            <p>Last {stats.period_days} days</p>
          </div>
        </div>

        <div className="stat-card">
          <TrendingUp size={32} />
          <div>
            <h3>Average per Day</h3>
            <div className="stat-value">{stats.average_per_day.toFixed(1)}</div>
            <p>Requests per day</p>
          </div>
        </div>

        <div className="stat-card">
          <DollarSign size={32} />
          <div>
            <h3>Total Cost</h3>
            <div className="stat-value">${stats.total_cost.toFixed(2)}</div>
            <p>Estimated cost</p>
          </div>
        </div>
      </div>

      <div className="model-breakdown">
        <h2>Usage by Model</h2>
        <div className="model-list">
          {Object.entries(stats.by_model).map(([model, count]) => (
            <div key={model} className="model-item">
              <div className="model-name">{model}</div>
              <div className="model-count">{count} requests</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

