import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, FileCode, TrendingUp } from 'lucide-react'

interface ReviewHistoryItem {
  id: number
  file_path: string
  language: string
  overall_score: number
  model_used: string
  created_at: string
  repository?: string
}

export default function History() {
  const navigate = useNavigate()
  const [history, setHistory] = useState<ReviewHistoryItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const response = await fetch('/api/v1/history/')
      if (!response.ok) throw new Error('Failed to load history')
      const data = await response.json()
      setHistory(data)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  if (loading) {
    return <div className="page-container">Loading...</div>
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Review History</h1>
        <p>View your past code reviews</p>
      </div>

      {history.length === 0 ? (
        <div className="empty-state">
          <Clock size={64} color="#95a5a6" />
          <h2>No Reviews Yet</h2>
          <p>Start reviewing code to see your history here</p>
        </div>
      ) : (
        <div className="history-list">
          {history.map((item) => (
            <div
              key={item.id}
              className="history-card"
              onClick={() => navigate(`/review?id=${item.id}`)}
            >
              <div className="history-card-header">
                <FileCode size={20} />
                <div>
                  <h3>{item.file_path || 'Untitled'}</h3>
                  <p className="history-meta">
                    {item.language} • {item.model_used} • {formatDate(item.created_at)}
                  </p>
                </div>
              </div>
              <div className="history-score">
                <TrendingUp size={20} />
                <span>{item.overall_score.toFixed(0)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

