import { useState, useEffect } from 'react'
import { Save, Plus, Trash2, Key, Eye, EyeOff } from 'lucide-react'
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
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    anthropic: '',
  })
  const [apiKeysStatus, setApiKeysStatus] = useState({
    openai_configured: false,
    anthropic_configured: false,
    openai_preview: null as string | null,
    anthropic_preview: null as string | null,
  })
  const [showKeys, setShowKeys] = useState({ openai: false, anthropic: false })
  const [loadingKeys, setLoadingKeys] = useState(true)

  useEffect(() => {
    loadConfigs()
    loadAPIKeysStatus()
  }, [])

  const loadAPIKeysStatus = async () => {
    try {
      const response = await fetch('/api/v1/config/api-keys')
      if (!response.ok) throw new Error('Failed to load API keys status')
      const data = await response.json()
      setApiKeysStatus(data)
    } catch (error) {
      console.error(error)
      toast.error('Failed to load API keys status')
    } finally {
      setLoadingKeys(false)
    }
  }

  const updateAPIKeys = async () => {
    if (!apiKeys.openai && !apiKeys.anthropic) {
      toast.error('Please enter at least one API key')
      return
    }

    try {
      const response = await fetch('/api/v1/config/api-keys', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          openai_key: apiKeys.openai || null,
          anthropic_key: apiKeys.anthropic || null,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to update API keys' }))
        throw new Error(errorData.detail || 'Failed to update API keys')
      }

      const result = await response.json()
      toast.success(result.message || 'API keys updated! Please restart the backend.')
      setApiKeys({ openai: '', anthropic: '' })
      loadAPIKeysStatus()
    } catch (error: any) {
      toast.error(error.message || 'Failed to update API keys')
    }
  }

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
        <p>Manage review settings, custom rules, and API keys</p>
      </div>

      {/* API Keys Section */}
      <div className="config-form" style={{ marginBottom: '30px' }}>
        <h2 style={{ marginBottom: '20px', color: '#2c3e50', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Key size={24} />
          API Keys
        </h2>
        <p style={{ color: '#7f8c8d', marginBottom: '20px', fontSize: '14px' }}>
          Update your API keys here. Changes will require a backend restart to take effect.
        </p>

        {loadingKeys ? (
          <p>Loading API keys status...</p>
        ) : (
          <>
            <div className="form-group">
              <label>OpenAI API Key</label>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <input
                  type={showKeys.openai ? 'text' : 'password'}
                  value={apiKeys.openai}
                  onChange={(e) => setApiKeys({ ...apiKeys, openai: e.target.value })}
                  placeholder={apiKeysStatus.openai_configured ? `Current: ${apiKeysStatus.openai_preview}` : 'Enter OpenAI API key (sk-...)'}
                  className="api-key-input"
                />
                <button
                  type="button"
                  onClick={() => setShowKeys({ ...showKeys, openai: !showKeys.openai })}
                  className="btn-icon"
                  style={{ minWidth: '40px' }}
                >
                  {showKeys.openai ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {apiKeysStatus.openai_configured && (
                <p style={{ fontSize: '12px', color: '#27ae60', marginTop: '4px' }}>
                  ✓ OpenAI key is configured
                </p>
              )}
            </div>

            <div className="form-group">
              <label>Anthropic API Key</label>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <input
                  type={showKeys.anthropic ? 'text' : 'password'}
                  value={apiKeys.anthropic}
                  onChange={(e) => setApiKeys({ ...apiKeys, anthropic: e.target.value })}
                  placeholder={apiKeysStatus.anthropic_configured ? `Current: ${apiKeysStatus.anthropic_preview}` : 'Enter Anthropic API key'}
                  className="api-key-input"
                />
                <button
                  type="button"
                  onClick={() => setShowKeys({ ...showKeys, anthropic: !showKeys.anthropic })}
                  className="btn-icon"
                  style={{ minWidth: '40px' }}
                >
                  {showKeys.anthropic ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {apiKeysStatus.anthropic_configured && (
                <p style={{ fontSize: '12px', color: '#27ae60', marginTop: '4px' }}>
                  ✓ Anthropic key is configured
                </p>
              )}
            </div>

            <button onClick={updateAPIKeys} className="btn-primary">
              <Save size={18} />
              Update API Keys
            </button>

            <div style={{ marginTop: '15px', padding: '12px', background: '#fff3cd', borderRadius: '6px', fontSize: '13px', color: '#856404' }}>
              <strong>Note:</strong> After updating API keys, you need to restart the backend server for changes to take effect.
            </div>
          </>
        )}
      </div>

      {/* Review Configuration Section */}
      <div className="config-form">
        <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>Review Configuration</h2>
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

