import { useState, useEffect } from 'react'
import { Save, Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

interface Config {
  id?: number
  name: string
  config_data: {
    min_severity: string
    ignore_patterns: string[]
    custom_prompt?: string
    coding_standards?: Record<string, any>
    custom_rules?: string[]
  }
  is_default: boolean
}

export default function Config() {
  const [configs, setConfigs] = useState<Config[]>([])
  const [currentConfig, setCurrentConfig] = useState<Config>({
    name: '',
    config_data: {
      min_severity: 'low',
      ignore_patterns: [],
      custom_rules: [],
    },
    is_default: false,
  })
  const [newPattern, setNewPattern] = useState('')
  const [newRule, setNewRule] = useState('')

  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      const response = await fetch('/api/v1/config/')
      if (!response.ok) throw new Error('Failed to load configs')
      const data = await response.json()
      setConfigs(data)
    } catch (error) {
      console.error(error)
    }
  }

  const saveConfig = async () => {
    try {
      const response = await fetch('/api/v1/config/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentConfig),
      })
      if (!response.ok) throw new Error('Failed to save config')
      toast.success('Configuration saved!')
      loadConfigs()
    } catch (error) {
      toast.error('Failed to save configuration')
    }
  }

  const addIgnorePattern = () => {
    if (newPattern.trim()) {
      setCurrentConfig({
        ...currentConfig,
        config_data: {
          ...currentConfig.config_data,
          ignore_patterns: [...(currentConfig.config_data.ignore_patterns || []), newPattern.trim()],
        },
      })
      setNewPattern('')
    }
  }

  const removeIgnorePattern = (index: number) => {
    const patterns = [...(currentConfig.config_data.ignore_patterns || [])]
    patterns.splice(index, 1)
    setCurrentConfig({
      ...currentConfig,
      config_data: {
        ...currentConfig.config_data,
        ignore_patterns: patterns,
      },
    })
  }

  const addCustomRule = () => {
    if (newRule.trim()) {
      setCurrentConfig({
        ...currentConfig,
        config_data: {
          ...currentConfig.config_data,
          custom_rules: [...(currentConfig.config_data.custom_rules || []), newRule.trim()],
        },
      })
      setNewRule('')
    }
  }

  const removeCustomRule = (index: number) => {
    const rules = [...(currentConfig.config_data.custom_rules || [])]
    rules.splice(index, 1)
    setCurrentConfig({
      ...currentConfig,
      config_data: {
        ...currentConfig.config_data,
        custom_rules: rules,
      },
    })
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Configuration</h1>
        <p>Manage review settings and custom rules</p>
      </div>

      <div className="config-form">
        <div className="form-group">
          <label>Configuration Name</label>
          <input
            type="text"
            value={currentConfig.name}
            onChange={(e) => setCurrentConfig({ ...currentConfig, name: e.target.value })}
            placeholder="e.g., my-team-config"
          />
        </div>

        <div className="form-group">
          <label>Minimum Severity</label>
          <select
            value={currentConfig.config_data.min_severity}
            onChange={(e) =>
              setCurrentConfig({
                ...currentConfig,
                config_data: { ...currentConfig.config_data, min_severity: e.target.value },
              })
            }
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>

        <div className="form-group">
          <label>Ignore Patterns</label>
          <div className="pattern-input">
            <input
              type="text"
              value={newPattern}
              onChange={(e) => setNewPattern(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addIgnorePattern()}
              placeholder="e.g., node_modules, *.pyc"
            />
            <button onClick={addIgnorePattern} className="btn-icon">
              <Plus size={18} />
            </button>
          </div>
          <div className="pattern-list">
            {currentConfig.config_data.ignore_patterns?.map((pattern, index) => (
              <div key={index} className="pattern-item">
                <span>{pattern}</span>
                <button onClick={() => removeIgnorePattern(index)} className="btn-icon-small">
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Custom Prompt</label>
          <textarea
            value={currentConfig.config_data.custom_prompt || ''}
            onChange={(e) =>
              setCurrentConfig({
                ...currentConfig,
                config_data: { ...currentConfig.config_data, custom_prompt: e.target.value },
              })
            }
            placeholder="Optional custom prompt for AI review..."
            rows={5}
          />
        </div>

        <div className="form-group">
          <label>Custom Rules</label>
          <div className="pattern-input">
            <input
              type="text"
              value={newRule}
              onChange={(e) => setNewRule(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addCustomRule()}
              placeholder="Add a custom rule..."
            />
            <button onClick={addCustomRule} className="btn-icon">
              <Plus size={18} />
            </button>
          </div>
          <div className="pattern-list">
            {currentConfig.config_data.custom_rules?.map((rule, index) => (
              <div key={index} className="pattern-item">
                <span>{rule}</span>
                <button onClick={() => removeCustomRule(index)} className="btn-icon-small">
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>

        <button onClick={saveConfig} className="btn-primary">
          <Save size={18} />
          Save Configuration
        </button>
      </div>

      {configs.length > 0 && (
        <div className="configs-list">
          <h2>Saved Configurations</h2>
          {configs.map((config) => (
            <div key={config.id} className="config-item">
              <div>
                <h3>{config.name}</h3>
                {config.is_default && <span className="badge">Default</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

