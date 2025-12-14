import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { AlertCircle, CheckCircle, Info, Lightbulb, BookOpen } from 'lucide-react'
// import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
// import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import toast from 'react-hot-toast'

interface Issue {
  type: string
  severity: string
  line: number
  column?: number
  description: string
  suggestion?: string
  explanation?: string
}

interface ReviewResult {
  review_id?: number
  issues: Issue[]
  summary: {
    total_issues: number
    by_type: Record<string, number>
    by_severity: Record<string, number>
  }
  overall_score: number
  model_used: string
  recommendations: string[]
}

export default function Review() {
  const location = useLocation()
  const navigate = useNavigate()
  const [reviewResult, setReviewResult] = useState<ReviewResult | null>(
    location.state?.reviewResult || null
  )
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!reviewResult) {
      // Try to load from URL params or fetch
      const reviewId = new URLSearchParams(location.search).get('id')
      if (reviewId) {
        loadReview(parseInt(reviewId))
      }
    }
  }, [location])

  const loadReview = async (reviewId: number) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/v1/reviews/${reviewId}`)
      if (!response.ok) throw new Error('Failed to load review')
      const data = await response.json()
      setReviewResult(data.review_results)
    } catch (error) {
      toast.error('Failed to load review')
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = async () => {
    if (!reviewResult?.review_id) {
      toast.error('No review ID available')
      return
    }

    try {
      const response = await fetch(`/api/v1/reviews/${reviewResult.review_id}/report`)
      const html = await response.text()
      const blob = new Blob([html], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `code-review-${reviewResult.review_id}.html`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('Report downloaded!')
    } catch (error) {
      toast.error('Failed to download report')
    }
  }

  if (loading) {
    return <div className="page-container">Loading...</div>
  }

  if (!reviewResult) {
    return (
      <div className="page-container">
        <p>No review data available. Please start a review from the home page.</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Go to Home
        </button>
      </div>
    )
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#c0392b'
      case 'high': return '#e74c3c'
      case 'medium': return '#f39c12'
      case 'low': return '#95a5a6'
      default: return '#7f8c8d'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'bug': return <AlertCircle size={18} />
      case 'security': return <AlertCircle size={18} />
      case 'style': return <Info size={18} />
      case 'documentation': return <BookOpen size={18} />
      default: return <Info size={18} />
    }
  }

  return (
    <div className="page-container">
      <div className="review-header">
        <div>
          <h1>Code Review Results</h1>
          <p>Model: {reviewResult.model_used}</p>
        </div>
        <button onClick={downloadReport} className="btn-primary">
          Download HTML Report
        </button>
      </div>

      <div className="score-card" style={{ background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` }}>
        <div className="score-value">{reviewResult.overall_score.toFixed(0)}</div>
        <div className="score-label">Overall Score</div>
      </div>

      <div className="summary-grid">
        <div className="summary-card">
          <h3>Total Issues</h3>
          <div className="summary-value">{reviewResult.summary.total_issues}</div>
        </div>
        <div className="summary-card">
          <h3>Bugs</h3>
          <div className="summary-value">{reviewResult.summary.by_type.bug || 0}</div>
        </div>
        <div className="summary-card">
          <h3>Security</h3>
          <div className="summary-value">{reviewResult.summary.by_type.security || 0}</div>
        </div>
        <div className="summary-card">
          <h3>Style</h3>
          <div className="summary-value">{reviewResult.summary.by_type.style || 0}</div>
        </div>
        <div className="summary-card">
          <h3>Documentation</h3>
          <div className="summary-value">{reviewResult.summary.by_type.documentation || 0}</div>
        </div>
      </div>

      {reviewResult.issues.length === 0 ? (
        <div className="no-issues">
          <CheckCircle size={64} color="#27ae60" />
          <h2>No Issues Found!</h2>
          <p>Great job! Your code looks clean and well-written.</p>
        </div>
      ) : (
        <div className="issues-list">
          <h2>Issues Found</h2>
          {reviewResult.issues.map((issue, index) => (
            <div key={index} className="issue-card">
              <div className="issue-header">
                <div className="issue-type-badge">
                  {getTypeIcon(issue.type)}
                  <span>{issue.type}</span>
                </div>
                <div
                  className="severity-badge"
                  style={{ backgroundColor: getSeverityColor(issue.severity) }}
                >
                  {issue.severity}
                </div>
              </div>
              <div className="issue-location">
                Line {issue.line}{issue.column ? `, Column ${issue.column}` : ''}
              </div>
              <div className="issue-description">{issue.description}</div>
              {issue.suggestion && (
                <div className="suggestion-box">
                  <Lightbulb size={18} />
                  <div>
                    <strong>Suggestion:</strong>
                    <p>{issue.suggestion}</p>
                  </div>
                </div>
              )}
              {issue.explanation && (
                <div className="explanation-box">
                  <BookOpen size={18} />
                  <div>
                    <strong>Learning:</strong>
                    <p>{issue.explanation}</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {reviewResult.recommendations && reviewResult.recommendations.length > 0 && (
        <div className="recommendations-box">
          <h2>General Recommendations</h2>
          <ul>
            {reviewResult.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

