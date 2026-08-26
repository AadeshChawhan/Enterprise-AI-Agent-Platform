import { useEffect, useRef, useState } from 'react'
import MarkdownMessage from './components/MarkdownMessage'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function App() {
  // ==================================================
  // PROVIDERS
  // ==================================================

  const [providers, setProviders] = useState([])
  const [loadingProviders, setLoadingProviders] = useState(true)

  const [providerStatus, setProviderStatus] = useState({})
  const [checkingProviders, setCheckingProviders] = useState(true)

  // ==================================================
  // AGENTS
  // ==================================================

  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [loadingAgents, setLoadingAgents] = useState(true)

  // ==================================================
  // MODELS
  // ==================================================

  const [models, setModels] = useState([])
  const [loadingModels, setLoadingModels] = useState(false)

  // ==================================================
  // AGENT FORMS
  // ==================================================

  const [showCreateForm, setShowCreateForm] = useState(false)
  const [showEditForm, setShowEditForm] = useState(false)

  const [newAgentName, setNewAgentName] = useState('')
  const [newAgentProvider, setNewAgentProvider] = useState('')
  const [newAgentModel, setNewAgentModel] = useState('')
  const [newAgentTemperature, setNewAgentTemperature] = useState(0.7)
  const [newAgentSystemPrompt, setNewAgentSystemPrompt] = useState('')

  const [editAgentName, setEditAgentName] = useState('')
  const [editAgentProvider, setEditAgentProvider] = useState('')
  const [editAgentModel, setEditAgentModel] = useState('')
  const [editAgentTemperature, setEditAgentTemperature] = useState(0.7)
  const [editAgentSystemPrompt, setEditAgentSystemPrompt] = useState('')

  const [creatingAgent, setCreatingAgent] = useState(false)
  const [editingAgent, setEditingAgent] = useState(false)
  const [deletingAgent, setDeletingAgent] = useState(false)

  // ==================================================
  // KNOWLEDGE BASES
  // ==================================================

  const [knowledgeBases, setKnowledgeBases] = useState([])
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState(null)
  const [knowledgeDocuments, setKnowledgeDocuments] = useState([])

  const [loadingKnowledgeBases, setLoadingKnowledgeBases] = useState(true)
  const [loadingKnowledgeDocuments, setLoadingKnowledgeDocuments] = useState(false)
  const [showKnowledgePanel, setShowKnowledgePanel] = useState(false)

  const [newKnowledgeBaseName, setNewKnowledgeBaseName] = useState('')
  const [newKnowledgeBaseDescription, setNewKnowledgeBaseDescription] = useState('')
  const [creatingKnowledgeBase, setCreatingKnowledgeBase] = useState(false)
  const [deletingKnowledgeBase, setDeletingKnowledgeBase] = useState(false)
  const [uploadingDocument, setUploadingDocument] = useState(false)

  const [newAgentKnowledgeBaseId, setNewAgentKnowledgeBaseId] = useState('')
  const [editAgentKnowledgeBaseId, setEditAgentKnowledgeBaseId] = useState('')

  // ==================================================
  // CONVERSATIONS
  // ==================================================

  const [conversations, setConversations] = useState([])
  const [selectedConversation, setSelectedConversation] = useState(null)

  const [loadingConversations, setLoadingConversations] = useState(false)
  const [creatingConversation, setCreatingConversation] = useState(false)
  const [deletingConversation, setDeletingConversation] = useState(false)

  // ==================================================
  // CHAT
  // ==================================================

  const [messages, setMessages] = useState([])
  const [prompt, setPrompt] = useState('')

  const [loadingMessages, setLoadingMessages] = useState(false)
  const [runningAgent, setRunningAgent] = useState(false)

  const chatEndRef = useRef(null)

  // ==================================================
  // GENERAL
  // ==================================================

  const [error, setError] = useState('')

  // ==================================================
  // PROVIDER HELPERS
  // ==================================================

  const getProviderMeta = providerId => {
    return providers.find(
      provider => provider.id === providerId
    )
  }

  const getProviderType = providerId => {
    return getProviderMeta(providerId)?.type || 'unknown'
  }

  const providerSupportsStreaming = providerId => {
    return (
      getProviderMeta(providerId)?.supports_streaming !== false
    )
  }

  const providerSupportsSystemPrompt = providerId => {
    return (
      getProviderMeta(providerId)?.supports_system_prompt !== false
    )
  }

  // ==================================================
  // AUTO SCROLL
  // ==================================================

  const scrollToBottom = (behavior = 'smooth') => {
    chatEndRef.current?.scrollIntoView({
      behavior,
      block: 'end',
    })
  }

  useEffect(() => {
    if (!loadingMessages) {
      scrollToBottom('smooth')
    }
  }, [messages, runningAgent, loadingMessages])

  // ==================================================
  // LOAD PROVIDERS
  // ==================================================

  const loadProviders = async () => {
    try {
      setLoadingProviders(true)

      const response = await fetch(
        `${API_BASE_URL}/providers`
      )

      if (!response.ok) {
        throw new Error('Failed to load providers')
      }

      const data = await response.json()

      setProviders(data)

      if (data.length > 0) {
        setNewAgentProvider(prev =>
          prev || data[0].id
        )
      }

      return data
    } catch (err) {
      console.error(
        'Unable to load providers:',
        err
      )

      setError(
        'Unable to load AI providers.'
      )

      return []
    } finally {
      setLoadingProviders(false)
    }
  }

  // ==================================================
  // PROVIDER HEALTH
  // ==================================================

  const checkProviderStatus = async () => {
    try {
      setCheckingProviders(true)

      const response = await fetch(
        `${API_BASE_URL}/health`
      )

      if (!response.ok) {
        throw new Error(
          `Health check failed: ${response.status}`
        )
      }

      const data = await response.json()

      setProviderStatus(
        data.providers || {}
      )
    } catch (err) {
      console.error(
        'Provider health check failed:',
        err
      )

      const offlineStatuses = {}

      providers.forEach(provider => {
        offlineStatuses[provider.id] = false
      })

      setProviderStatus(
        offlineStatuses
      )
    } finally {
      setCheckingProviders(false)
    }
  }

  // ==================================================
  // LOAD AGENTS
  // ==================================================

  const loadAgents = async () => {
    try {
      setLoadingAgents(true)

      const response = await fetch(
        `${API_BASE_URL}/agents`
      )

      if (!response.ok) {
        throw new Error(
          'Failed to load agents'
        )
      }

      const data = await response.json()

      setAgents(data)

      if (
        data.length > 0 &&
        !selectedAgent
      ) {
        setSelectedAgent(
          data[0]
        )
      }
    } catch (err) {
      console.error(err)

      setError(
        'Unable to load agents from the backend.'
      )
    } finally {
      setLoadingAgents(false)
    }
  }

  // ==================================================
  // LOAD MODELS
  // ==================================================

  const loadModels = async provider => {
    if (!provider) {
      setModels([])
      return []
    }

    try {
      setLoadingModels(true)

      const response = await fetch(
        `${API_BASE_URL}/models?provider=${encodeURIComponent(provider)}`
      )

      if (!response.ok) {
        const data = await response
          .json()
          .catch(() => null)

        throw new Error(
          data?.detail ||
          `Unable to load models for ${provider}`
        )
      }

      const data = await response.json()

      setModels(data)

      return data
    } catch (err) {
      console.error(
        'Unable to load models:',
        err
      )

      setModels([])

      return []
    } finally {
      setLoadingModels(false)
    }
  }

  // ==================================================
  // LOAD KNOWLEDGE BASES
  // ==================================================

  const loadKnowledgeBases = async () => {
    try {
      setLoadingKnowledgeBases(true)

      const response = await fetch(
        `${API_BASE_URL}/knowledge-bases`
      )

      if (!response.ok) {
        throw new Error(
          'Failed to load knowledge bases'
        )
      }

      const data = await response.json()

      setKnowledgeBases(data)

      setSelectedKnowledgeBase(prev => {
        if (
          prev &&
          data.some(
            knowledgeBase =>
              knowledgeBase.id === prev.id
          )
        ) {
          return prev
        }

        return data.length > 0
          ? data[0]
          : null
      })

      return data
    } catch (err) {
      console.error(
        'Unable to load knowledge bases:',
        err
      )

      setError(
        'Unable to load knowledge bases.'
      )

      return []
    } finally {
      setLoadingKnowledgeBases(false)
    }
  }

  // ==================================================
  // LOAD KNOWLEDGE DOCUMENTS
  // ==================================================

  const loadKnowledgeDocuments = async knowledgeBaseId => {
    if (!knowledgeBaseId) {
      setKnowledgeDocuments([])
      return []
    }

    try {
      setLoadingKnowledgeDocuments(true)

      const response = await fetch(
        `${API_BASE_URL}/knowledge-bases/${knowledgeBaseId}/documents`
      )

      if (!response.ok) {
        throw new Error(
          'Failed to load knowledge-base documents'
        )
      }

      const data = await response.json()

      setKnowledgeDocuments(data)

      return data
    } catch (err) {
      console.error(
        'Unable to load knowledge-base documents:',
        err
      )

      setKnowledgeDocuments([])

      setError(
        'Unable to load knowledge-base documents.'
      )

      return []
    } finally {
      setLoadingKnowledgeDocuments(false)
    }
  }

  // ==================================================
  // CREATE KNOWLEDGE BASE
  // ==================================================

  const handleCreateKnowledgeBase = async event => {
    event.preventDefault()

    const name =
      newKnowledgeBaseName.trim()

    if (!name) {
      setError(
        'Knowledge base name is required.'
      )
      return
    }

    try {
      setCreatingKnowledgeBase(true)
      setError('')

      const response = await fetch(
        `${API_BASE_URL}/knowledge-bases`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',
          },

          body: JSON.stringify({
            name,
            description:
              newKnowledgeBaseDescription.trim(),
          }),
        }
      )

      if (!response.ok) {
        const data = await response
          .json()
          .catch(() => null)

        throw new Error(
          data?.detail ||
          'Failed to create knowledge base'
        )
      }

      const createdKnowledgeBase =
        await response.json()

      setKnowledgeBases(prev => [
        createdKnowledgeBase,
        ...prev,
      ])

      setSelectedKnowledgeBase(
        createdKnowledgeBase
      )

      setKnowledgeDocuments([])
      setNewKnowledgeBaseName('')
      setNewKnowledgeBaseDescription('')
    } catch (err) {
      console.error(err)

      setError(
        err.message ||
        'Unable to create knowledge base.'
      )
    } finally {
      setCreatingKnowledgeBase(false)
    }
  }

  // ==================================================
  // DELETE KNOWLEDGE BASE
  // ==================================================

  const handleDeleteKnowledgeBase = async knowledgeBase => {
    if (!knowledgeBase) {
      return
    }

    const confirmed =
      window.confirm(
        `Delete "${knowledgeBase.name}" and its document records?`
      )

    if (!confirmed) {
      return
    }

    try {
      setDeletingKnowledgeBase(true)
      setError('')

      const response = await fetch(
        `${API_BASE_URL}/knowledge-bases/${knowledgeBase.id}`,
        {
          method: 'DELETE',
        }
      )

      if (!response.ok) {
        const data = await response
          .json()
          .catch(() => null)

        throw new Error(
          data?.detail ||
          'Failed to delete knowledge base'
        )
      }

      const remaining =
        knowledgeBases.filter(
          item =>
            item.id !== knowledgeBase.id
        )

      setKnowledgeBases(remaining)

      if (
        selectedKnowledgeBase?.id ===
        knowledgeBase.id
      ) {
        const nextKnowledgeBase =
          remaining[0] || null

        setSelectedKnowledgeBase(
          nextKnowledgeBase
        )

        if (nextKnowledgeBase) {
          await loadKnowledgeDocuments(
            nextKnowledgeBase.id
          )
        } else {
          setKnowledgeDocuments([])
        }
      }

      setAgents(prev =>
        prev.map(agent =>
          agent.knowledge_base_id ===
          knowledgeBase.id
            ? {
                ...agent,
                knowledge_base_id: null,
              }
            : agent
        )
      )

      setSelectedAgent(prev =>
        prev?.knowledge_base_id ===
        knowledgeBase.id
          ? {
              ...prev,
              knowledge_base_id: null,
            }
          : prev
      )
    } catch (err) {
      console.error(err)

      setError(
        err.message ||
        'Unable to delete knowledge base.'
      )
    } finally {
      setDeletingKnowledgeBase(false)
    }
  }

  // ==================================================
  // UPLOAD KNOWLEDGE DOCUMENT
  // ==================================================

  const handleUploadKnowledgeDocument =
    async event => {
      const file =
        event.target.files?.[0]

      event.target.value = ''

      if (
        !file ||
        !selectedKnowledgeBase
      ) {
        return
      }

      const extension =
        file.name
          .split('.')
          .pop()
          ?.toLowerCase()

      if (
        !['pdf', 'txt', 'docx'].includes(
          extension
        )
      ) {
        setError(
          'Only PDF, TXT, and DOCX files are supported.'
        )
        return
      }

      const formData =
        new FormData()

      formData.append(
        'file',
        file
      )

      try {
        setUploadingDocument(true)
        setError('')

        const response = await fetch(
          `${API_BASE_URL}/knowledge-bases/${selectedKnowledgeBase.id}/documents`,
          {
            method: 'POST',
            body: formData,
          }
        )

        if (!response.ok) {
          const data = await response
            .json()
            .catch(() => null)

          throw new Error(
            data?.detail ||
            'Document upload failed'
          )
        }

        await loadKnowledgeDocuments(
          selectedKnowledgeBase.id
        )
      } catch (err) {
        console.error(err)

        setError(
          err.message ||
          'Unable to upload document.'
        )
      } finally {
        setUploadingDocument(false)
      }
    }

  // ==================================================
  // OPEN KNOWLEDGE PANEL
  // ==================================================

  const openKnowledgePanel = knowledgeBase => {
    setError('')
    setShowCreateForm(false)
    setShowEditForm(false)
    setShowKnowledgePanel(true)

    if (knowledgeBase) {
      setSelectedKnowledgeBase(
        knowledgeBase
      )
    }
  }

  // ==================================================
  // LOAD CONVERSATIONS
  // ==================================================

  const loadConversations = async (
    agentId,
    preferredConversationId = null
  ) => {
    if (!agentId) {
      setConversations([])
      return
    }

    try {
      setLoadingConversations(true)

      const response = await fetch(
        `${API_BASE_URL}/agents/${agentId}/conversations`
      )

      if (!response.ok) {
        throw new Error(
          'Failed to load conversations'
        )
      }

      const data = await response.json()

      setConversations(data)

      if (preferredConversationId) {
        const preferred = data.find(
          conversation =>
            conversation.id ===
            preferredConversationId
        )

        if (preferred) {
          setSelectedConversation(preferred)
          return
        }
      }

      if (
        selectedConversation &&
        data.some(
          conversation =>
            conversation.id ===
            selectedConversation.id
        )
      ) {
        return
      }

      if (data.length > 0) {
        setSelectedConversation(
          data[0]
        )
      } else {
        setSelectedConversation(null)
        setMessages([])
      }
    } catch (err) {
      console.error(err)

      setError(
        'Unable to load conversations.'
      )
    } finally {
      setLoadingConversations(false)
    }
  }

  // ==================================================
  // LOAD MESSAGES
  // ==================================================

  const loadMessages = async conversationId => {
    if (!conversationId) {
      setMessages([])
      return
    }

    try {
      setLoadingMessages(true)

      const response = await fetch(
        `${API_BASE_URL}/conversations/${conversationId}/messages`
      )

      if (!response.ok) {
        throw new Error(
          'Failed to load messages'
        )
      }

      const data = await response.json()

      setMessages(data)

      setTimeout(() => {
        scrollToBottom('auto')
      }, 0)
    } catch (err) {
      console.error(err)

      setError(
        'Unable to load conversation messages.'
      )
    } finally {
      setLoadingMessages(false)
    }
  }

  // ==================================================
  // INITIAL LOAD
  // ==================================================

  useEffect(() => {
    loadProviders()
    loadAgents()
    loadKnowledgeBases()
  }, [])

  useEffect(() => {
    checkProviderStatus()

    const interval = setInterval(
      checkProviderStatus,
      10000
    )

    return () =>
      clearInterval(interval)
  }, [providers.length])

  useEffect(() => {
    if (!selectedKnowledgeBase) {
      setKnowledgeDocuments([])
      return
    }

    loadKnowledgeDocuments(
      selectedKnowledgeBase.id
    )
  }, [selectedKnowledgeBase?.id])

  // ==================================================
  // AGENT CHANGE
  // ==================================================

  useEffect(() => {
    if (!selectedAgent) {
      return
    }

    setError('')
    setSelectedConversation(null)
    setMessages([])
    setPrompt('')

    setShowCreateForm(false)
    setShowEditForm(false)

    loadConversations(
      selectedAgent.id
    )
  }, [selectedAgent?.id])

  // ==================================================
  // CONVERSATION CHANGE
  // ==================================================

  useEffect(() => {
    if (!selectedConversation) {
      setMessages([])
      return
    }

    setError('')

    loadMessages(
      selectedConversation.id
    )
  }, [selectedConversation?.id])

  // ==================================================
  // SELECT AGENT
  // ==================================================

  const handleSelectAgent = agent => {
    if (runningAgent) {
      return
    }

    setError('')
    setShowKnowledgePanel(false)
    setSelectedAgent(agent)
  }

  // ==================================================
  // SELECT CONVERSATION
  // ==================================================

  const handleSelectConversation = conversation => {
    if (runningAgent) {
      return
    }

    setError('')
    setPrompt('')

    setSelectedConversation(
      conversation
    )
  }

  // ==================================================
  // OPEN CREATE FORM
  // ==================================================

  const openCreateForm = async () => {
    if (runningAgent) {
      return
    }

    setError('')

    setShowCreateForm(true)
    setShowEditForm(false)
    setShowKnowledgePanel(false)

    setNewAgentName('')
    setNewAgentTemperature(0.7)
    setNewAgentSystemPrompt('')
    setNewAgentKnowledgeBaseId('')

    if (providers.length === 0) {
      setNewAgentProvider('')
      setNewAgentModel('')
      return
    }

    const defaultProvider =
      providers[0].id

    setNewAgentProvider(
      defaultProvider
    )

    const providerModels =
      await loadModels(
        defaultProvider
      )

    if (providerModels.length > 0) {
      setNewAgentModel(
        providerModels[0].id
      )
    } else {
      setNewAgentModel('')
    }
  }

  // ==================================================
  // CREATE PROVIDER CHANGE
  // ==================================================

  const handleNewProviderChange = async event => {
    const provider =
      event.target.value

    setError('')
    setNewAgentProvider(provider)
    setNewAgentModel('')

    if (
      !providerSupportsSystemPrompt(
        provider
      )
    ) {
      setNewAgentSystemPrompt('')
    }

    const providerModels =
      await loadModels(provider)

    if (providerModels.length > 0) {
      setNewAgentModel(
        providerModels[0].id
      )
    }
  }

  // ==================================================
  // CREATE AGENT
  // ==================================================

  const handleCreateAgent = async event => {
    event.preventDefault()

    if (!newAgentName.trim()) {
      setError(
        'Agent name is required.'
      )
      return
    }

    if (!newAgentProvider) {
      setError(
        'Provider is required.'
      )
      return
    }

    if (!newAgentModel) {
      setError(
        'Please select a model.'
      )
      return
    }

    try {
      setCreatingAgent(true)
      setError('')

      const response = await fetch(
        `${API_BASE_URL}/agents`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',
          },

          body: JSON.stringify({
            name:
              newAgentName.trim(),

            provider:
              newAgentProvider,

            model:
              newAgentModel,

            temperature:
              Number(
                newAgentTemperature
              ),

            system_prompt:
              providerSupportsSystemPrompt(
                newAgentProvider
              )
                ? newAgentSystemPrompt.trim()
                : '',

            knowledge_base_id:
              newAgentKnowledgeBaseId
                ? Number(
                    newAgentKnowledgeBaseId
                  )
                : null,
          }),
        }
      )

      if (!response.ok) {
        const data = await response
          .json()
          .catch(() => null)

        throw new Error(
          data?.detail ||
          'Failed to create agent'
        )
      }

      const createdAgent =
        await response.json()

      setAgents(prev => [
        ...prev,
        createdAgent,
      ])

      setSelectedAgent(
        createdAgent
      )

      setShowCreateForm(false)
    } catch (err) {
      console.error(err)

      setError(
        err.message ||
        'Unable to create agent.'
      )
    } finally {
      setCreatingAgent(false)
    }
  }

  // ==================================================
  // OPEN EDIT FORM
  // ==================================================

  const openEditForm = async () => {
    if (
      !selectedAgent ||
      runningAgent
    ) {
      return
    }

    setError('')

    const provider =
      selectedAgent.provider ||
      providers[0]?.id ||
      ''

    setEditAgentName(
      selectedAgent.name
    )

    setEditAgentProvider(
      provider
    )

    setEditAgentModel(
      selectedAgent.model
    )

    setEditAgentTemperature(
      selectedAgent.temperature
    )

    setEditAgentSystemPrompt(
      selectedAgent.system_prompt ||
      ''
    )

    setEditAgentKnowledgeBaseId(
      selectedAgent.knowledge_base_id
        ? String(
            selectedAgent.knowledge_base_id
          )
        : ''
    )

    await loadModels(provider)

    setShowEditForm(true)
    setShowCreateForm(false)
    setShowKnowledgePanel(false)
  }

  // ==================================================
  // EDIT PROVIDER CHANGE
  // ==================================================

  const handleEditProviderChange = async event => {
    const provider =
      event.target.value

    setError('')
    setEditAgentProvider(provider)
    setEditAgentModel('')

    if (
      !providerSupportsSystemPrompt(
        provider
      )
    ) {
      setEditAgentSystemPrompt('')
    }

    const providerModels =
      await loadModels(provider)

    if (providerModels.length > 0) {
      setEditAgentModel(
        providerModels[0].id
      )
    }
  }

  // ==================================================
  // UPDATE AGENT
  // ==================================================

  const handleUpdateAgent = async event => {
    event.preventDefault()

    if (!selectedAgent) {
      return
    }

    if (!editAgentName.trim()) {
      setError(
        'Agent name is required.'
      )
      return
    }

    if (!editAgentProvider) {
      setError(
        'Provider is required.'
      )
      return
    }

    if (!editAgentModel) {
      setError(
        'Model is required.'
      )
      return
    }

    try {
      setEditingAgent(true)
      setError('')

      const response = await fetch(
        `${API_BASE_URL}/agents/${selectedAgent.id}`,
        {
          method: 'PUT',

          headers: {
            'Content-Type':
              'application/json',
          },

          body: JSON.stringify({
            name:
              editAgentName.trim(),

            provider:
              editAgentProvider,

            model:
              editAgentModel,

            temperature:
              Number(
                editAgentTemperature
              ),

            system_prompt:
              providerSupportsSystemPrompt(
                editAgentProvider
              )
                ? editAgentSystemPrompt.trim()
                : '',

            knowledge_base_id:
              editAgentKnowledgeBaseId
                ? Number(
                    editAgentKnowledgeBaseId
                  )
                : null,
          }),
        }
      )

      if (!response.ok) {
        const data = await response
          .json()
          .catch(() => null)

        throw new Error(
          data?.detail ||
          'Failed to update agent'
        )
      }

      const updatedAgent =
        await response.json()

      setAgents(prev =>
        prev.map(agent =>
          agent.id ===
          updatedAgent.id
            ? updatedAgent
            : agent
        )
      )

      setSelectedAgent(
        updatedAgent
      )

      setShowEditForm(false)
    } catch (err) {
      console.error(err)

      setError(
        err.message ||
        'Unable to update agent.'
      )
    } finally {
      setEditingAgent(false)
    }
  }

  // ==================================================
  // DELETE AGENT
  // ==================================================

  const handleDeleteAgent = async () => {
    if (!selectedAgent) {
      return
    }

    const confirmed =
      window.confirm(
        `Delete "${selectedAgent.name}"? This will also delete its conversations.`
      )

    if (!confirmed) {
      return
    }

    try {
      setDeletingAgent(true)
      setError('')

      const response = await fetch(
        `${API_BASE_URL}/agents/${selectedAgent.id}`,
        {
          method: 'DELETE',
        }
      )

      if (!response.ok) {
        const data = await response
          .json()
          .catch(() => null)

        throw new Error(
          data?.detail ||
          'Failed to delete agent'
        )
      }

      const remaining =
        agents.filter(
          agent =>
            agent.id !==
            selectedAgent.id
        )

      setAgents(remaining)

      if (remaining.length > 0) {
        setSelectedAgent(
          remaining[0]
        )
      } else {
        setSelectedAgent(null)
        setConversations([])
        setSelectedConversation(null)
        setMessages([])
      }

      setShowEditForm(false)
    } catch (err) {
      console.error(err)

      setError(
        err.message ||
        'Unable to delete agent.'
      )
    } finally {
      setDeletingAgent(false)
    }
  }

  // ==================================================
  // CREATE CONVERSATION
  // ==================================================

  const createConversation = async (
    title = 'New Conversation'
  ) => {
    if (!selectedAgent) {
      return null
    }

    try {
      setCreatingConversation(true)
      setError('')

      const response = await fetch(
        `${API_BASE_URL}/conversations`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',
          },

          body: JSON.stringify({
            agent_id:
              selectedAgent.id,

            title,
          }),
        }
      )

      if (!response.ok) {
        const data = await response
          .json()
          .catch(() => null)

        throw new Error(
          data?.detail ||
          'Failed to create conversation'
        )
      }

      const conversation =
        await response.json()

      setConversations(prev => [
        conversation,
        ...prev,
      ])

      setSelectedConversation(
        conversation
      )

      setMessages([])

      return conversation
    } catch (err) {
      console.error(err)

      setError(
        err.message ||
        'Unable to create conversation.'
      )

      return null
    } finally {
      setCreatingConversation(false)
    }
  }

  // ==================================================
  // GENERATE AI TITLE
  // ==================================================

  const generateConversationTitle =
    async conversationId => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/conversations/${conversationId}/generate-title`,
          {
            method: 'POST',
          }
        )

        if (!response.ok) {
          return null
        }

        const updatedConversation =
          await response.json()

        setConversations(prev =>
          prev.map(conversation =>
            conversation.id ===
            updatedConversation.id
              ? updatedConversation
              : conversation
          )
        )

        setSelectedConversation(prev =>
          prev?.id ===
          updatedConversation.id
            ? updatedConversation
            : prev
        )

        return updatedConversation
      } catch (err) {
        console.error(
          'Unable to generate title:',
          err
        )

        return null
      }
    }

  // ==================================================
  // NEW CONVERSATION
  // ==================================================

  const handleNewConversation = async () => {
    if (runningAgent) {
      return
    }

    setError('')

    await createConversation(
      'New Conversation'
    )
  }

  // ==================================================
  // DELETE CONVERSATION
  // ==================================================

  const handleDeleteConversation = async (
    conversation,
    event
  ) => {
    event?.stopPropagation()

    if (
      !conversation ||
      runningAgent
    ) {
      return
    }

    const confirmed =
      window.confirm(
        `Delete "${conversation.title}"?`
      )

    if (!confirmed) {
      return
    }

    try {
      setDeletingConversation(true)
      setError('')

      const response = await fetch(
        `${API_BASE_URL}/conversations/${conversation.id}`,
        {
          method: 'DELETE',
        }
      )

      if (!response.ok) {
        const data = await response
          .json()
          .catch(() => null)

        throw new Error(
          data?.detail ||
          'Failed to delete conversation'
        )
      }

      const remaining =
        conversations.filter(
          item =>
            item.id !==
            conversation.id
        )

      setConversations(remaining)

      if (
        selectedConversation?.id ===
        conversation.id
      ) {
        if (remaining.length > 0) {
          setSelectedConversation(
            remaining[0]
          )
        } else {
          setSelectedConversation(null)
          setMessages([])
        }
      }
    } catch (err) {
      console.error(err)

      setError(
        err.message ||
        'Unable to delete conversation.'
      )
    } finally {
      setDeletingConversation(false)
    }
  }

  // ==================================================
  // SAVE MESSAGE
  // ==================================================

  const saveMessage = async (
    conversationId,
    role,
    content
  ) => {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}/messages`,
      {
        method: 'POST',

        headers: {
          'Content-Type':
            'application/json',
        },

        body: JSON.stringify({
          role,
          content,
        }),
      }
    )

    if (!response.ok) {
      const data = await response
        .json()
        .catch(() => null)

      throw new Error(
        data?.detail ||
        'Failed to save message'
      )
    }

    return response.json()
  }

  // ==================================================
  // SEND MESSAGE
  // ==================================================

  const handleSendMessage = async () => {
    const text =
      prompt.trim()

    if (
      !text ||
      !selectedAgent ||
      runningAgent
    ) {
      return
    }

    const provider =
      selectedAgent.provider

    const providerOnline =
      providerStatus[
        provider
      ] === true

    const streamingSupported =
      providerSupportsStreaming(
        provider
      )

    if (!providerOnline) {
      setError(
        `${provider} is currently unavailable.`
      )

      return
    }

    if (!streamingSupported) {
      setError(
        `${provider} does not support streaming.`
      )

      return
    }

    let conversation =
      selectedConversation

    const shouldGenerateTitle =
      !conversation ||
      conversation.title ===
        'New Conversation'

    const timestamp =
      Date.now()

    const tempUserId =
      `temp-user-${timestamp}`

    const tempAssistantId =
      `temp-assistant-${timestamp}`

    try {
      setRunningAgent(true)
      setError('')

      // ------------------------------------------
      // CREATE CONVERSATION IF NEEDED
      // ------------------------------------------

      if (!conversation) {
        conversation =
          await createConversation(
            'New Conversation'
          )

        if (!conversation) {
          return
        }
      }

      // ------------------------------------------
      // TEMP USER MESSAGE
      // ------------------------------------------

      const temporaryUserMessage = {
        id: tempUserId,
        conversation_id:
          conversation.id,
        role: 'user',
        content: text,
        temporary: true,
      }

      // ------------------------------------------
      // TEMP ASSISTANT MESSAGE
      // ------------------------------------------

      const temporaryAssistantMessage = {
        id: tempAssistantId,
        conversation_id:
          conversation.id,
        role: 'assistant',
        content: '',
        temporary: true,
      }

      setMessages(prev => [
        ...prev,
        temporaryUserMessage,
        temporaryAssistantMessage,
      ])

      setPrompt('')

      setTimeout(() => {
        scrollToBottom('smooth')
      }, 0)

      // ------------------------------------------
      // STREAM
      // ------------------------------------------

      const response = await fetch(
        `${API_BASE_URL}/agents/${selectedAgent.id}/stream`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',
          },

          body: JSON.stringify({
            prompt: text,
            conversation_id:
              conversation.id,
          }),
        }
      )

      if (!response.ok) {
        const data = await response
          .json()
          .catch(() => null)

        throw new Error(
          data?.detail ||
          `Provider request failed (${response.status})`
        )
      }

      if (!response.body) {
        throw new Error(
          'Streaming response is unavailable.'
        )
      }

      const reader =
        response.body.getReader()

      const decoder =
        new TextDecoder()

      let assistantText = ''

      while (true) {
        const {
          value,
          done,
        } = await reader.read()

        if (done) {
          break
        }

        const chunk =
          decoder.decode(
            value,
            {
              stream: true,
            }
          )

        assistantText += chunk

        setMessages(prev =>
          prev.map(message =>
            message.id ===
            tempAssistantId
              ? {
                  ...message,
                  content:
                    assistantText,
                }
              : message
          )
        )
      }

      assistantText +=
        decoder.decode()

      if (
        !assistantText.trim()
      ) {
        throw new Error(
          'The model returned an empty response.'
        )
      }

      // ------------------------------------------
      // SAVE MESSAGES
      // ------------------------------------------

      const savedUserMessage =
        await saveMessage(
          conversation.id,
          'user',
          text
        )

      const savedAssistantMessage =
        await saveMessage(
          conversation.id,
          'assistant',
          assistantText
        )

      setMessages(prev =>
        prev.map(message => {
          if (
            message.id ===
            tempUserId
          ) {
            return savedUserMessage
          }

          if (
            message.id ===
            tempAssistantId
          ) {
            return savedAssistantMessage
          }

          return message
        })
      )

      // ------------------------------------------
      // GENERATE TITLE
      // ------------------------------------------

      if (shouldGenerateTitle) {
        const updatedConversation =
          await generateConversationTitle(
            conversation.id
          )

        if (updatedConversation) {
          conversation =
            updatedConversation
        }
      }

      // ------------------------------------------
      // REFRESH SIDEBAR
      // ------------------------------------------

      await loadConversations(
        selectedAgent.id,
        conversation.id
      )

      setTimeout(() => {
        scrollToBottom('smooth')
      }, 0)
    } catch (err) {
      console.error(
        'Agent request failed:',
        err
      )

      setMessages(prev =>
        prev.filter(
          message =>
            message.id !==
              tempUserId &&
            message.id !==
              tempAssistantId
        )
      )

      setPrompt(text)

      setError(
        err.message ||
        'Unable to run agent.'
      )

      checkProviderStatus()
    } finally {
      setRunningAgent(false)
    }
  }

  // ==================================================
  // ENTER TO SEND
  // ==================================================

  const handlePromptKeyDown = event => {
    if (
      event.key === 'Enter' &&
      !event.shiftKey
    ) {
      event.preventDefault()

      handleSendMessage()
    }
  }

  // ==================================================
  // CLOSE FORMS
  // ==================================================

  const closeForms = () => {
    setShowCreateForm(false)
    setShowEditForm(false)
    setShowKnowledgePanel(false)
    setError('')
  }

  const getKnowledgeBaseName = knowledgeBaseId => {
    if (!knowledgeBaseId) {
      return 'None'
    }

    return (
      knowledgeBases.find(
        knowledgeBase =>
          knowledgeBase.id ===
          knowledgeBaseId
      )?.name ||
      `Knowledge Base #${knowledgeBaseId}`
    )
  }

  // ==================================================
  // SELECTED PROVIDER HELPERS
  // ==================================================

  const selectedProvider =
    selectedAgent?.provider

  const selectedProviderOnline =
    selectedProvider
      ? providerStatus[
          selectedProvider
        ] === true
      : false

  const selectedProviderSupportsStreaming =
    selectedProvider
      ? providerSupportsStreaming(
          selectedProvider
        )
      : false

  // ==================================================
  // RENDER
  // ==================================================

  return (
    <div className="app">

      {/* ============================================
          TOP BAR
      ============================================ */}

      <header className="topbar">

        <div>
          <h1>
            Enterprise AI Agent Platform
          </h1>

          <p>
            Manage and run your AI agents
          </p>
        </div>

        {/* PROVIDER STATUS */}

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '18px',
            flexWrap: 'wrap',
          }}
        >
          {providers.map(provider => {
            const online =
              providerStatus[
                provider.id
              ] === true

            return (
              <div
                key={provider.id}
                className={`status ${
                  checkingProviders
                    ? 'checking'
                    : online
                      ? 'online'
                      : 'offline'
                }`}
              >
                <span
                  className={`status-dot ${
                    checkingProviders
                      ? 'checking'
                      : online
                        ? 'online'
                        : 'offline'
                  }`}
                />

                <span>
                  {provider.name}
                  {' · '}

                  <small>
                    {provider.type}
                  </small>

                  {' · '}

                  {checkingProviders
                    ? 'Checking'
                    : online
                      ? 'Online'
                      : 'Offline'}
                </span>
              </div>
            )
          })}
        </div>

      </header>

      {/* ============================================
          DASHBOARD
      ============================================ */}

      <div className="dashboard">

        {/* ==========================================
            SIDEBAR
        ========================================== */}

        <aside className="sidebar">

          <div className="sidebar-header">

            <h2>
              Agents
            </h2>

            <button
              className="create-button"
              onClick={openCreateForm}
              disabled={runningAgent}
            >
              + Create
            </button>

          </div>

          {/* AGENT LIST */}

          <div className="agent-list">

            {loadingAgents ? (

              <div className="loading">
                Loading agents...
              </div>

            ) : agents.length === 0 ? (

              <div className="loading">
                No agents created yet.
              </div>

            ) : (

              agents.map(agent => (

                <button
                  key={agent.id}

                  className={`agent-item ${
                    selectedAgent?.id ===
                    agent.id
                      ? 'active'
                      : ''
                  }`}

                  onClick={() =>
                    handleSelectAgent(agent)
                  }

                  disabled={runningAgent}
                >
                  <strong>
                    {agent.name}
                  </strong>

                  <span>
                    {agent.provider}
                    {' · '}

                    {getProviderType(
                      agent.provider
                    )}

                    {' · '}

                    {agent.model}
                  </span>
                </button>

              ))

            )}

          </div>

          {/* KNOWLEDGE BASES */}

          <div className="conversations-section knowledge-sidebar-section">

            <div className="conversations-header">

              <h2>
                Knowledge
              </h2>

              <button
                className="new-conversation-button"
                onClick={() =>
                  openKnowledgePanel(
                    selectedKnowledgeBase
                  )
                }
                disabled={runningAgent}
                title="Manage knowledge bases"
              >
                ⚙
              </button>

            </div>

            <div className="conversation-list">

              {loadingKnowledgeBases ? (

                <div className="loading">
                  Loading knowledge bases...
                </div>

              ) : knowledgeBases.length === 0 ? (

                <button
                  className="conversation-item"
                  onClick={() =>
                    openKnowledgePanel(null)
                  }
                >
                  Create your first knowledge base
                </button>

              ) : (

                knowledgeBases.map(
                  knowledgeBase => (

                    <div
                      key={knowledgeBase.id}
                      className={`conversation-item ${
                        showKnowledgePanel &&
                        selectedKnowledgeBase?.id ===
                        knowledgeBase.id
                          ? 'active'
                          : ''
                      }`}
                      onClick={() =>
                        openKnowledgePanel(
                          knowledgeBase
                        )
                      }
                    >
                      <span className="conversation-title">
                        {knowledgeBase.name}
                      </span>
                    </div>

                  )
                )

              )}

            </div>

          </div>

          {/* CONVERSATIONS */}

          {selectedAgent && (

            <div className="conversations-section">

              <div className="conversations-header">

                <h2>
                  Conversations
                </h2>

                <button
                  className="new-conversation-button"
                  onClick={
                    handleNewConversation
                  }
                  disabled={
                    creatingConversation ||
                    runningAgent
                  }
                  title="New conversation"
                >
                  +
                </button>

              </div>

              <div className="conversation-list">

                {loadingConversations ? (

                  <div className="loading">
                    Loading conversations...
                  </div>

                ) : conversations.length === 0 ? (

                  <div className="loading">
                    No conversations yet.
                  </div>

                ) : (

                  conversations.map(
                    conversation => (

                      <div
                        key={
                          conversation.id
                        }

                        className={`conversation-item ${
                          selectedConversation?.id ===
                          conversation.id
                            ? 'active'
                            : ''
                        }`}

                        onClick={() =>
                          handleSelectConversation(
                            conversation
                          )
                        }
                      >
                        <span className="conversation-title">
                          {
                            conversation.title
                          }
                        </span>

                        <button
                          className="delete-conversation-button"

                          onClick={event =>
                            handleDeleteConversation(
                              conversation,
                              event
                            )
                          }

                          disabled={
                            deletingConversation ||
                            runningAgent
                          }

                          title="Delete conversation"
                        >
                          🗑
                        </button>
                      </div>

                    )
                  )

                )}

              </div>

            </div>

          )}

        </aside>

        {/* ==========================================
            WORKSPACE
        ========================================== */}

        <main className="workspace">

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* ========================================
              CREATE AGENT
          ======================================== */}

          {showKnowledgePanel ? (

            <section className="knowledge-panel">

              <div className="agent-header">

                <div>

                  <h2>
                    Knowledge Bases
                  </h2>

                  <p>
                    Upload company or project documents that RAG-enabled agents can search.
                  </p>

                </div>

                <button
                  className="cancel-button"
                  onClick={() =>
                    setShowKnowledgePanel(false)
                  }
                >
                  Close
                </button>

              </div>

              <div className="knowledge-layout">

                <div className="form-card knowledge-create-card">

                  <h3>
                    Create Knowledge Base
                  </h3>

                  <form
                    onSubmit={
                      handleCreateKnowledgeBase
                    }
                  >
                    <div className="form-group">

                      <label>
                        Name
                      </label>

                      <input
                        type="text"
                        value={
                          newKnowledgeBaseName
                        }
                        onChange={event =>
                          setNewKnowledgeBaseName(
                            event.target.value
                          )
                        }
                        placeholder="e.g. Company Policies"
                      />

                    </div>

                    <div className="form-group">

                      <label>
                        Description
                      </label>

                      <textarea
                        rows={3}
                        value={
                          newKnowledgeBaseDescription
                        }
                        onChange={event =>
                          setNewKnowledgeBaseDescription(
                            event.target.value
                          )
                        }
                        placeholder="What kind of documents will live here?"
                      />

                    </div>

                    <button
                      type="submit"
                      className="create-button"
                      disabled={
                        creatingKnowledgeBase ||
                        !newKnowledgeBaseName.trim()
                      }
                    >
                      {creatingKnowledgeBase
                        ? 'Creating...'
                        : 'Create Knowledge Base'}
                    </button>

                  </form>

                </div>

                <div className="form-card knowledge-detail-card">

                  {!selectedKnowledgeBase ? (

                    <div className="message-placeholder">
                      Create a knowledge base to start uploading documents.
                    </div>

                  ) : (

                    <>

                      <div className="knowledge-detail-header">

                        <div>

                          <h3>
                            {selectedKnowledgeBase.name}
                          </h3>

                          <p>
                            {selectedKnowledgeBase.description ||
                              'No description'}
                          </p>

                        </div>

                        <button
                          className="delete-button"
                          onClick={() =>
                            handleDeleteKnowledgeBase(
                              selectedKnowledgeBase
                            )
                          }
                          disabled={
                            deletingKnowledgeBase
                          }
                        >
                          {deletingKnowledgeBase
                            ? 'Deleting...'
                            : 'Delete'}
                        </button>

                      </div>

                      <div className="form-group">

                        <label>
                          Upload Document
                        </label>

                        <input
                          type="file"
                          accept=".pdf,.txt,.docx"
                          onChange={
                            handleUploadKnowledgeDocument
                          }
                          disabled={
                            uploadingDocument
                          }
                        />

                        <small>
                          PDF, TXT, or DOCX · maximum 10 MB
                        </small>

                        {uploadingDocument && (
                          <p>
                            Processing document and creating embeddings...
                          </p>
                        )}

                      </div>

                      <div className="knowledge-documents">

                        <h3>
                          Documents
                        </h3>

                        {loadingKnowledgeDocuments ? (

                          <div className="loading">
                            Loading documents...
                          </div>

                        ) : knowledgeDocuments.length === 0 ? (

                          <div className="loading">
                            No documents uploaded yet.
                          </div>

                        ) : (

                          knowledgeDocuments.map(
                            document => (

                              <div
                                className="knowledge-document-item"
                                key={document.id}
                              >

                                <div>

                                  <strong>
                                    {document.filename}
                                  </strong>

                                  <span>
                                    {document.content_type ||
                                      'unknown type'}
                                  </span>

                                </div>

                                <span
                                  className={`knowledge-status ${document.status}`}
                                >
                                  {document.status}
                                </span>

                              </div>

                            )
                          )

                        )}

                      </div>

                    </>

                  )}

                </div>

              </div>

            </section>

          ) : showCreateForm ? (

            <form
              className="form-card"
              onSubmit={
                handleCreateAgent
              }
            >
              <h2>
                Create Agent
              </h2>

              <p>
                Configure a new AI agent.
              </p>

              <div className="form-group">
                <label>
                  Agent Name
                </label>

                <input
                  type="text"

                  value={
                    newAgentName
                  }

                  onChange={event =>
                    setNewAgentName(
                      event.target.value
                    )
                  }

                  placeholder="e.g. Research Assistant"
                />
              </div>

              <div className="form-group">
                <label>
                  Provider
                </label>

                <select
                  value={
                    newAgentProvider
                  }

                  onChange={
                    handleNewProviderChange
                  }

                  disabled={
                    loadingProviders
                  }
                >
                  {providers.map(
                    provider => (
                      <option
                        key={
                          provider.id
                        }

                        value={
                          provider.id
                        }
                      >
                        {provider.name}
                        {' — '}
                        {provider.type}
                      </option>
                    )
                  )}
                </select>
              </div>

              <div className="form-group">
                <label>
                  Model
                </label>

                <select
                  value={
                    newAgentModel
                  }

                  onChange={event =>
                    setNewAgentModel(
                      event.target.value
                    )
                  }

                  disabled={
                    loadingModels
                  }
                >
                  {loadingModels ? (

                    <option value="">
                      Loading models...
                    </option>

                  ) : models.length > 0 ? (

                    models.map(model => (
                      <option
                        key={
                          model.id
                        }

                        value={
                          model.id
                        }
                      >
                        {model.id}
                      </option>
                    ))

                  ) : (

                    <option value="">
                      No models available
                    </option>

                  )}
                </select>
              </div>

              <div className="form-group">
                <label>
                  Temperature
                </label>

                <input
                  type="number"
                  min="0"
                  max="2"
                  step="0.1"

                  value={
                    newAgentTemperature
                  }

                  onChange={event =>
                    setNewAgentTemperature(
                      event.target.value
                    )
                  }
                />
              </div>

              <div className="form-group">
                <label>
                  System Prompt
                </label>

                <textarea
                  rows={6}

                  value={
                    newAgentSystemPrompt
                  }

                  onChange={event =>
                    setNewAgentSystemPrompt(
                      event.target.value
                    )
                  }

                  disabled={
                    !providerSupportsSystemPrompt(
                      newAgentProvider
                    )
                  }

                  placeholder={
                    providerSupportsSystemPrompt(
                      newAgentProvider
                    )
                      ? 'Describe how this agent should behave...'
                      : 'System prompts are not supported by this provider.'
                  }
                />
              </div>

              <div className="form-group">

                <label>
                  Knowledge Base
                </label>

                <select
                  value={
                    newAgentKnowledgeBaseId
                  }
                  onChange={event =>
                    setNewAgentKnowledgeBaseId(
                      event.target.value
                    )
                  }
                >
                  <option value="">
                    None — standard agent
                  </option>

                  {knowledgeBases.map(
                    knowledgeBase => (
                      <option
                        key={knowledgeBase.id}
                        value={knowledgeBase.id}
                      >
                        {knowledgeBase.name}
                      </option>
                    )
                  )}
                </select>

                <small>
                  Optional. Selecting one enables RAG for this agent.
                </small>

              </div>

              <div className="form-actions">

                <button
                  type="button"
                  className="cancel-button"
                  onClick={closeForms}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="create-button"

                  disabled={
                    creatingAgent ||
                    !newAgentModel
                  }
                >
                  {creatingAgent
                    ? 'Creating...'
                    : 'Create Agent'}
                </button>

              </div>
            </form>

          ) : showEditForm &&
            selectedAgent ? (

            /* ======================================
               EDIT AGENT
            ====================================== */

            <form
              className="form-card"
              onSubmit={
                handleUpdateAgent
              }
            >
              <h2>
                Edit Agent
              </h2>

              <p>
                Update agent configuration.
              </p>

              <div className="form-group">
                <label>
                  Agent Name
                </label>

                <input
                  type="text"

                  value={
                    editAgentName
                  }

                  onChange={event =>
                    setEditAgentName(
                      event.target.value
                    )
                  }
                />
              </div>

              <div className="form-group">
                <label>
                  Provider
                </label>

                <select
                  value={
                    editAgentProvider
                  }

                  onChange={
                    handleEditProviderChange
                  }
                >
                  {providers.map(
                    provider => (
                      <option
                        key={
                          provider.id
                        }

                        value={
                          provider.id
                        }
                      >
                        {provider.name}
                        {' — '}
                        {provider.type}
                      </option>
                    )
                  )}
                </select>
              </div>

              <div className="form-group">
                <label>
                  Model
                </label>

                <select
                  value={
                    editAgentModel
                  }

                  onChange={event =>
                    setEditAgentModel(
                      event.target.value
                    )
                  }

                  disabled={
                    loadingModels
                  }
                >
                  {loadingModels ? (

                    <option value="">
                      Loading models...
                    </option>

                  ) : models.length > 0 ? (

                    models.map(model => (
                      <option
                        key={
                          model.id
                        }

                        value={
                          model.id
                        }
                      >
                        {model.id}
                      </option>
                    ))

                  ) : (

                    <option
                      value={
                        editAgentModel
                      }
                    >
                      {
                        editAgentModel ||
                        'No model available'
                      }
                    </option>

                  )}
                </select>
              </div>

              <div className="form-group">
                <label>
                  Temperature
                </label>

                <input
                  type="number"
                  min="0"
                  max="2"
                  step="0.1"

                  value={
                    editAgentTemperature
                  }

                  onChange={event =>
                    setEditAgentTemperature(
                      event.target.value
                    )
                  }
                />
              </div>

              <div className="form-group">
                <label>
                  System Prompt
                </label>

                <textarea
                  rows={6}

                  value={
                    editAgentSystemPrompt
                  }

                  onChange={event =>
                    setEditAgentSystemPrompt(
                      event.target.value
                    )
                  }

                  disabled={
                    !providerSupportsSystemPrompt(
                      editAgentProvider
                    )
                  }

                  placeholder={
                    providerSupportsSystemPrompt(
                      editAgentProvider
                    )
                      ? 'Describe how this agent should behave...'
                      : 'System prompts are not supported by this provider.'
                  }
                />
              </div>

              <div className="form-group">

                <label>
                  Knowledge Base
                </label>

                <select
                  value={
                    editAgentKnowledgeBaseId
                  }
                  onChange={event =>
                    setEditAgentKnowledgeBaseId(
                      event.target.value
                    )
                  }
                >
                  <option value="">
                    None — standard agent
                  </option>

                  {knowledgeBases.map(
                    knowledgeBase => (
                      <option
                        key={knowledgeBase.id}
                        value={knowledgeBase.id}
                      >
                        {knowledgeBase.name}
                      </option>
                    )
                  )}
                </select>

                <small>
                  Optional. Selecting one enables RAG for this agent.
                </small>

              </div>

              <div className="form-actions">

                <button
                  type="button"
                  className="cancel-button"
                  onClick={closeForms}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="edit-button"
                  disabled={editingAgent}
                >
                  {editingAgent
                    ? 'Saving...'
                    : 'Save Changes'}
                </button>

              </div>
            </form>

          ) : !selectedAgent ? (

            /* ======================================
               EMPTY STATE
            ====================================== */

            <div className="empty-state">

              <h2>
                Welcome to Enterprise AI Agent Platform
              </h2>

              <p>
                Select an agent to start chatting.
              </p>

            </div>

          ) : (

            /* ======================================
               CHAT WORKSPACE
            ====================================== */

            <>

              {/* AGENT HEADER */}

              <section className="agent-header">

                <div>
                  <h2>
                    {selectedAgent.name}
                  </h2>

                  <p>
                    Provider:{' '}
                    {
                      selectedAgent.provider
                    }

                    {' ('}

                    {getProviderType(
                      selectedAgent.provider
                    )}

                    {')'}

                    {' · '}

                    Model:{' '}
                    {
                      selectedAgent.model
                    }

                    {' · '}

                    Temperature:{' '}
                    {
                      selectedAgent.temperature
                    }

                    {' · '}

                    Knowledge:{' '}
                    {getKnowledgeBaseName(
                      selectedAgent.knowledge_base_id
                    )}
                  </p>
                </div>

                <div className="agent-actions">

                  <button
                    className="edit-button"
                    onClick={openEditForm}
                    disabled={runningAgent}
                  >
                    Edit Agent
                  </button>

                  <button
                    className="delete-button"
                    onClick={
                      handleDeleteAgent
                    }

                    disabled={
                      deletingAgent ||
                      runningAgent
                    }
                  >
                    {deletingAgent
                      ? 'Deleting...'
                      : 'Delete Agent'}
                  </button>

                </div>
              </section>

              {/* ====================================
                  CHAT AREA
              ==================================== */}

              <section className="chat-area">

                {loadingMessages ? (

                  <div className="message-placeholder">
                    Loading conversation...
                  </div>

                ) : messages.length === 0 ? (

                  <div className="message-placeholder">

                    <div>
                      <strong>
                        Start a conversation
                      </strong>

                      <br />

                      <span>
                        Ask{' '}
                        {
                          selectedAgent.name
                        }{' '}
                        anything.
                      </span>
                    </div>

                  </div>

                ) : (

                  messages.map(
                    message => (

                      <div
                        key={
                          message.id
                        }

                        className={`chat-message ${
                          message.role ===
                          'user'
                            ? 'user'
                            : 'assistant'
                        }`}
                      >
                        <div className="message-label">

                          {message.role ===
                          'user'
                            ? 'You'
                            : selectedAgent.name}

                        </div>

                        <div
                          className={`message-content ${
                            runningAgent &&
                            message.temporary &&
                            message.role ===
                              'assistant' &&
                            !message.content
                              ? 'thinking'
                              : ''
                          }`}
                        >

                          {/* USER = PLAIN TEXT */}
                          {/* ASSISTANT = MARKDOWN */}

                          {message.role === 'assistant' ? (

                            message.content ? (

                              <MarkdownMessage
                                content={
                                  message.content
                                }
                              />

                            ) : (

                              message.temporary
                                ? 'Thinking...'
                                : ''

                            )

                          ) : (

                            message.content

                          )}

                        </div>
                      </div>

                    )
                  )

                )}

                <div
                  ref={chatEndRef}
                  aria-hidden="true"
                />

              </section>

              {/* ====================================
                  PROMPT
              ==================================== */}

              <section className="prompt-area">

                <textarea
                  value={prompt}

                  onChange={event =>
                    setPrompt(
                      event.target.value
                    )
                  }

                  onKeyDown={
                    handlePromptKeyDown
                  }

                  placeholder={
                    !selectedProviderOnline
                      ? `${selectedProvider} is unavailable...`
                      : !selectedProviderSupportsStreaming
                        ? 'Streaming is not supported by this provider...'
                        : `Message ${selectedAgent.name}...`
                  }

                  disabled={
                    runningAgent ||
                    !selectedProviderOnline ||
                    !selectedProviderSupportsStreaming
                  }
                />

                <button
                  className="run-button"
                  onClick={
                    handleSendMessage
                  }

                  disabled={
                    runningAgent ||
                    !prompt.trim() ||
                    !selectedProviderOnline ||
                    !selectedProviderSupportsStreaming
                  }
                >
                  {runningAgent
                    ? 'Streaming...'
                    : 'Send'}
                </button>

              </section>

            </>

          )}

        </main>

      </div>

    </div>
  )
}

export default App