import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Code, GitBranch } from 'lucide-react'
import toast from 'react-hot-toast'

interface ModelOption {
  value: string
  label: string
  provider: string
}

export default function Home() {
  const navigate = useNavigate()
  const [code, setCode] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState<string>('gpt-3.5-turbo')
  const [availableModels, setAvailableModels] = useState<ModelOption[]>([])
  const [loadingModels, setLoadingModels] = useState(true)

  useEffect(() => {
    // Load available models on component mount
    const loadModels = async () => {
      try {
        const response = await fetch('/api/v1/config/available-models')
        if (!response.ok) throw new Error('Failed to load models')
        const data = await response.json()
        if (data.models && data.models.length > 0) {
          setAvailableModels(data.models)
          setSelectedModel(data.default || data.models[0].value)
        } else {
          toast.error(data.message || 'No API keys configured')
        }
      } catch (error) {
        console.error('Error loading models:', error)
        toast.error('Failed to load available models')
      } finally {
        setLoadingModels(false)
      }
    }
    loadModels()
  }, [])

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      const reader = new FileReader()
      reader.onload = (event) => {
        setCode(event.target?.result as string)
      }
      reader.readAsText(selectedFile)
    }
  }

  const handleReview = async () => {
    if (!code.trim() && !file) {
      toast.error('Please provide code to review')
      return
    }

    setLoading(true)
    try {
      let result;
      const currentFile = file; // Store in variable to help TypeScript
      
      // If file is uploaded, use file upload endpoint
      if (currentFile) {
        const formData = new FormData()
        formData.append('file', currentFile)
        formData.append('model', selectedModel)

        const response = await fetch('/api/v1/files/review', {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Review failed' }))
          throw new Error(errorData.detail || `Review failed: ${response.status} ${response.statusText}`)
        }

        result = await response.json()
      } else {
        // Use code paste endpoint
        const response = await fetch('/api/v1/reviews/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            code,
            file_path: undefined,
            model: selectedModel,
          }),
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Review failed' }))
          throw new Error(errorData.detail || `Review failed: ${response.status} ${response.statusText}`)
        }

        result = await response.json()
      }

      navigate('/review', { state: { reviewResult: result } })
      toast.success('Review completed!')
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to review code'
      toast.error(errorMessage)
      console.error('Review error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>AI Code Review Tool</h1>
        <p>Review your code for bugs, security issues, style problems, and documentation gaps</p>
      </div>

      <div className="model-selector">
        <label htmlFor="model-select">AI Model:</label>
        <select
          id="model-select"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="model-dropdown"
          disabled={loadingModels || availableModels.length === 0}
        >
          {loadingModels ? (
            <option>Loading models...</option>
          ) : availableModels.length === 0 ? (
            <option>No models available</option>
          ) : (
            availableModels.map((model) => (
              <option key={model.value} value={model.value}>
                {model.label} ({model.provider})
              </option>
            ))
          )}
        </select>
        {availableModels.length === 0 && !loadingModels && (
          <p className="model-warning">
            ⚠️ No API keys configured. Add OPENAI_API_KEY or ANTHROPIC_API_KEY to backend/.env
          </p>
        )}
      </div>

      <div className="review-options">
        <div className="option-card">
          <Code size={32} />
          <h3>Paste Code</h3>
          <textarea
            className="code-input"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here..."
            rows={15}
          />
          <button 
            onClick={handleReview} 
            className="btn-primary" 
            disabled={loading || availableModels.length === 0}
          >
            {loading ? 'Reviewing...' : 'Review Code'}
          </button>
        </div>

        <div className="option-card">
          <Upload size={32} />
          <h3>Upload File</h3>
          <input
            type="file"
            onChange={handleFileUpload}
            className="file-input"
            accept=".py,.js,.ts,.java,.go,.rs,.cpp,.c,.jsx,.tsx"
          />
          {file && (
            <div className="file-info">
              <p>Selected: {file.name}</p>
              <button 
                onClick={handleReview} 
                className="btn-primary" 
                disabled={loading || availableModels.length === 0}
              >
                {loading ? 'Reviewing...' : 'Review File'}
              </button>
            </div>
          )}
        </div>

        <div className="option-card">
          <GitBranch size={32} />
          <h3>Git Integration</h3>
          <p>Review git diffs and pull requests</p>
          <button
            onClick={() => navigate('/review?mode=git')}
            className="btn-secondary"
          >
            Review Git Changes
          </button>
        </div>
      </div>
    </div>
  )
}

