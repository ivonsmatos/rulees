import {
  Activity,
  Archive,
  BadgeCheck,
  Bot,
  Check,
  CircleAlert,
  CircleHelp,
  Download,
  FileText,
  FolderKanban,
  History,
  LogIn,
  MessageSquare,
  Mic,
  Pause,
  Play,
  Plus,
  Radio,
  RefreshCw,
  Search,
  ShieldCheck,
  Square,
  UserPlus,
  X,
} from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

type AuthUser = {
  id: string
  name: string
  email: string
}

type Tenant = {
  id: string
  name: string
  slug: string
  role: string
}

type AuthSession = {
  access_token: string
  user: AuthUser
  tenant: Tenant
}

type TenantAccess = {
  id: string
  user_id: string
  role: string
  created_at: string
  tenant: Tenant
}

type TenantMember = {
  id: string
  tenant_id: string
  user_id: string
  role: string
  created_at: string
  user?: AuthUser | null
}

type TenantInvite = {
  id: string
  tenant_id: string
  email: string
  role: string
  status: string
  invited_by: string
  accepted_by?: string | null
  accepted_at?: string | null
  created_at: string
  tenant?: Tenant | null
}

type Project = {
  id: string
  name: string
  description: string
  status: string
  archived_at?: string | null
}

type ProjectMember = {
  id: string
  tenant_id: string
  project_id: string
  user_id: string
  role: string
  created_by: string
  created_at: string
}

type ProjectGlossaryTerm = {
  id: string
  tenant_id: string
  project_id: string
  term: string
  definition: string
  aliases: string[]
  created_by: string
  created_at: string
}

type ProjectTemplate = {
  id: string
  tenant_id: string
  name: string
  description: string
  default_objective: string
  default_glossary_terms: Array<{
    term: string
    definition: string
    aliases: string[]
  }>
  created_by: string
  created_at: string
}

type Meeting = {
  id: string
  project_id: string
  title: string
  objective: string
  status: string
}

type MeetingTemplate = {
  key: string
  title: string
  objective: string
  agenda: string[]
}

type MeetingSummary = {
  meeting_id: string
  title: string
  status: string
  transcript_chunks: number
  rules_total: number
  rules_approved: number
  open_questions: number
  decisions_total: number
  summary: string
  next_steps: string[]
}

type MeetingConsent = {
  id: string
  meeting_id: string
  user_id: string
  text_version: string
  accepted_at: string
  revoked_at?: string | null
  revoke_reason?: string | null
}

type MeetingParticipant = {
  id: string
  meeting_id: string
  user_id: string
  role: string
  consent_required: boolean
  created_at: string
}

type MeetingLifecycleEvent = {
  id: string
  event_type: string
  from_status?: string | null
  to_status?: string | null
  user_id: string
  created_at: string
}

type Rule = {
  id: string
  code: string
  rule_text: string
  status: string
  version_number: number
  confidence_score: number
  quality_score: number
  quality_details?: {
    score?: number
    missing?: string[]
    evidence_count?: number
  }
  source_chunk_ids?: string[]
  replaced_by_rule_id?: string | null
  rag_result_type?: string
  requires_human_resolution?: boolean
}

type Transcript = {
  id?: string
  chunk_id?: string
  normalized_text: string
  raw_text?: string
  source?: string
  is_final?: boolean
  start_time?: number | null
  end_time?: number | null
  speaker_label?: string | null
  language?: string | null
  confidence_score?: number | null
  sequence?: number | null
}

type DocumentResult = {
  id: string
  project_id: string
  meeting_id: string
  title: string
  status: string
  content: string
  created_at?: string
}

type DocumentSection = {
  id: string
  section_key: string
  title: string
  body: string
  sort_order: number
}

type DocumentVersion = {
  id: string
  version_number: number
  title: string
  status: string
  change_reason: string
  created_at: string
}

type DocumentExportJob = {
  id: string
  document_id: string
  format: string
  status: string
  payload: Record<string, unknown>
  result_url?: string | null
  created_at: string
}

type VersionDiff = {
  resource_type: string
  resource_id: string
  from_version: number
  to_version: number
  lines: Array<{ kind: string; text: string }>
}

type ProjectGapSummary = {
  project_id: string
  meetings_total: number
  meetings_without_transcript: number
  rules_pending_review: number
  rules_conflicted: number
  open_questions: number
  documents_total: number
  readiness_score: number
  gaps: string[]
}

type BetaFeedback = {
  id: string
  rating: number
  category: string
  comment: string
  created_at: string
}

type CommentItem = {
  id: string
  resource_type: string
  resource_id: string
  author_id: string
  body: string
  status: string
  created_at: string
}

type NotificationItem = {
  id: string
  title: string
  body: string
  resource_type?: string | null
  resource_id?: string | null
  read_at?: string | null
  created_at: string
}

type AnalyticsSummary = {
  projects_total: number
  meetings_total: number
  rules_total: number
  approved_rules: number
  documents_total: number
  open_questions: number
  comments_total: number
  notifications_unread: number
  readiness_score: number
}

type GlobalSearchResult = {
  source_type: string
  source_id: string
  project_id?: string | null
  title: string
  snippet: string
  created_at: string
}

type AuditLog = {
  id: string
  action: string
  resource_type: string
  resource_id: string | null
  created_at: string
}

type UsageSummaryItem = {
  event_type: string
  unit: string
  quantity: number
}

type BillingLimitItem = {
  event_type: string
  used: number
  limit: number
  remaining: number
}

type BillingCostItem = {
  event_type: string
  quantity: number
  unit_cost_usd: number
  estimated_cost_usd: number
}

type BillingStatus = {
  plan_name: string
  status: string
  limits: BillingLimitItem[]
  estimated_costs: BillingCostItem[]
}

type QuestionInsight = {
  id: string
  question_text: string
  reason: string
  gap_type: string
  priority: string
  status: string
  confidence_score: number
  source_chunk_ids?: string[]
}

type DecisionInsight = {
  id: string
  decision_text: string
  decision_type: string
  status: string
  responsible_area: string | null
  confidence_score: number
  source_chunk_ids?: string[]
}

type AgentRun = {
  run_id: string
  agent_name: string
  agent_role: string
  status: string
  confidence_score: number | null
  created_at: string
}

type RagSearchResult = {
  source_type: string
  source_id: string
  meeting_id: string | null
  content: string
  similarity_score: number
  created_at: string
}

type WsEvent = {
  event_id?: string
  event_type: string
  payload: Record<string, unknown>
}

type MicState = 'idle' | 'requesting' | 'recording' | 'error'

type WorkspaceView = 'projects' | 'meetings' | 'rules' | 'documents' | 'audit'

const apiBase = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8001'
const wsBase = apiBase.replace('http://', 'ws://').replace('https://', 'wss://')
const tenantRoleOptions = ['admin', 'manager', 'member', 'viewer'] as const
const projectRoleOptions = ['manager', 'member', 'viewer'] as const

function App() {
  const [session, setSession] = useState<AuthSession | null>(() => {
    const stored = localStorage.getItem('rulees.session')
    return stored ? JSON.parse(stored) : null
  })
  const [mode, setMode] = useState<'login' | 'register'>('register')
  const [message, setMessage] = useState('')
  const [activeView, setActiveView] = useState<WorkspaceView>('projects')
  const [tenantAccess, setTenantAccess] = useState<TenantAccess[]>([])
  const [tenantMembers, setTenantMembers] = useState<TenantMember[]>([])
  const [tenantInvites, setTenantInvites] = useState<TenantInvite[]>([])
  const [pendingInvites, setPendingInvites] = useState<TenantInvite[]>([])
  const [projectMembers, setProjectMembers] = useState<ProjectMember[]>([])
  const [projectGlossary, setProjectGlossary] = useState<ProjectGlossaryTerm[]>([])
  const [projectTemplates, setProjectTemplates] = useState<ProjectTemplate[]>([])
  const [projectTab, setProjectTab] = useState<'overview' | 'glossary' | 'templates' | 'members'>('overview')
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [projectGapSummary, setProjectGapSummary] = useState<ProjectGapSummary | null>(null)
  const [meetings, setMeetings] = useState<Meeting[]>([])
  const [meetingTemplates, setMeetingTemplates] = useState<MeetingTemplate[]>([])
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null)
  const [meetingSummary, setMeetingSummary] = useState<MeetingSummary | null>(null)
  const [hasConsent, setHasConsent] = useState(false)
  const [meetingConsent, setMeetingConsent] = useState<MeetingConsent | null>(null)
  const [meetingParticipants, setMeetingParticipants] = useState<MeetingParticipant[]>([])
  const [meetingLifecycle, setMeetingLifecycle] = useState<MeetingLifecycleEvent[]>([])
  const [transcript, setTranscript] = useState<Transcript[]>([])
  const [rules, setRules] = useState<Rule[]>([])
  const [questions, setQuestions] = useState<QuestionInsight[]>([])
  const [decisions, setDecisions] = useState<DecisionInsight[]>([])
  const [agentRuns, setAgentRuns] = useState<AgentRun[]>([])
  const [ragQuery, setRagQuery] = useState('cashback cliente premium')
  const [ragResults, setRagResults] = useState<RagSearchResult[]>([])
  const [editingRuleId, setEditingRuleId] = useState<string | null>(null)
  const [revisionDraft, setRevisionDraft] = useState('')
  const [ruleEvidence, setRuleEvidence] = useState<Record<string, Transcript[]>>({})
  const [documents, setDocuments] = useState<DocumentResult[]>([])
  const [documentSections, setDocumentSections] = useState<DocumentSection[]>([])
  const [documentVersions, setDocumentVersions] = useState<DocumentVersion[]>([])
  const [documentExportJobs, setDocumentExportJobs] = useState<DocumentExportJob[]>([])
  const [documentComments, setDocumentComments] = useState<CommentItem[]>([])
  const [documentDiff, setDocumentDiff] = useState<VersionDiff | null>(null)
  const [auditActionFilter, setAuditActionFilter] = useState('')
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [betaFeedback, setBetaFeedback] = useState<BetaFeedback[]>([])
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [analyticsSummary, setAnalyticsSummary] = useState<AnalyticsSummary | null>(null)
  const [globalSearchQuery, setGlobalSearchQuery] = useState('')
  const [globalSearchResults, setGlobalSearchResults] = useState<GlobalSearchResult[]>([])
  const [usageSummary, setUsageSummary] = useState<UsageSummaryItem[]>([])
  const [billingStatus, setBillingStatus] = useState<BillingStatus | null>(null)
  const [documentResult, setDocumentResult] = useState<DocumentResult | null>(null)
  const [documentRevisionDraft, setDocumentRevisionDraft] = useState('')
  const [connectionState, setConnectionState] = useState<'offline' | 'connecting' | 'online'>('offline')
  const [browserOnline, setBrowserOnline] = useState(navigator.onLine)
  const [lastPongAt, setLastPongAt] = useState<string | null>(null)
  const [micState, setMicState] = useState<MicState>('idle')
  const [audioChunksSent, setAudioChunksSent] = useState(0)
  const [audioMimeType, setAudioMimeType] = useState('')
  const [demoText, setDemoText] = useState(
    'Quando o cliente tiver investimento acima de R$ 15000, deve receber 1% de cashback.',
  )
  const socketRef = useRef<WebSocket | null>(null)
  const heartbeatRef = useRef<number | null>(null)
  const shouldReconnectRef = useRef(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioSequenceRef = useRef(0)
  const wsEventCounterRef = useRef(0)

  const authHeaders = useMemo<Record<string, string>>(() => {
    const headers: Record<string, string> = {}
    if (session) {
      headers.Authorization = `Bearer ${session.access_token}`
      headers['X-Tenant-Id'] = session.tenant.id
    }
    return headers
  }, [session])

  const canStreamAudio = selectedMeeting?.status === 'active' && connectionState === 'online'
  const canManageTenantAccess = session ? ['admin', 'manager'].includes(session.tenant.role) : false
  const canManageProjects = canManageTenantAccess
  const canAssignTenantAdmin = session?.tenant.role === 'admin'
  const tenantMemberByUserId = useMemo(() => {
    return new Map(tenantMembers.map((member) => [member.user_id, member]))
  }, [tenantMembers])
  const tenantRoleChoices = canAssignTenantAdmin
    ? tenantRoleOptions
    : tenantRoleOptions.filter((role) => role !== 'admin')
  const onboardingItems = [
    { label: 'Projeto', done: projects.length > 0 },
    { label: 'Reuniao', done: meetings.length > 0 },
    { label: 'Consentimento', done: hasConsent },
    { label: 'Transcricao', done: transcript.some((chunk) => chunk.is_final !== false) },
    { label: 'Regra aprovada', done: rules.some((rule) => rule.status === 'approved') },
    { label: 'Documento', done: documents.length > 0 || Boolean(documentResult) },
  ]

  function parseAliases(value: FormDataEntryValue | null) {
    return String(value ?? '')
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
  }

  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers)
    headers.set('Content-Type', 'application/json')
    Object.entries(authHeaders).forEach(([key, value]) => headers.set(key, value))
    const response = await fetch(`${apiBase}${path}`, {
      ...options,
      headers,
    })
    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      throw new Error(body.detail ?? 'Erro inesperado')
    }
    return response.json()
  }

  async function handleAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const payload =
      mode === 'register'
        ? {
            name: String(form.get('name')),
            email: String(form.get('email')),
            password: String(form.get('password')),
            organization_name: String(form.get('organization')),
          }
        : {
            email: String(form.get('email')),
            password: String(form.get('password')),
          }
    try {
      const result = await request<AuthSession>(`/api/auth/${mode}`, {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      localStorage.setItem('rulees.session', JSON.stringify(result))
      setSession(result)
      setMessage('Sessao iniciada')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha no acesso')
    }
  }

  async function loadTenantAccess() {
    if (!session) return
    const result = await request<TenantAccess[]>('/api/auth/tenants')
    setTenantAccess(result)
  }

  async function loadTenantMembers() {
    if (!session) return
    try {
      const result = await request<TenantMember[]>('/api/auth/tenant/members')
      setTenantMembers(result)
    } catch {
      setTenantMembers([])
    }
  }

  async function loadTenantInvites() {
    if (!session) return
    try {
      const result = await request<TenantInvite[]>('/api/auth/tenant/invites')
      setTenantInvites(result)
    } catch {
      setTenantInvites([])
    }
  }

  async function loadPendingInvites() {
    if (!session) return
    try {
      const result = await request<TenantInvite[]>('/api/auth/invites/pending')
      setPendingInvites(result)
    } catch {
      setPendingInvites([])
    }
  }

  async function loadProjectMembers(project: Project | null = selectedProject) {
    if (!session || !project) {
      setProjectMembers([])
      return
    }
    try {
      const result = await request<ProjectMember[]>(`/api/projects/${project.id}/members`)
      setProjectMembers(result)
    } catch {
      setProjectMembers([])
    }
  }

  async function loadProjectGlossary(project: Project | null = selectedProject) {
    if (!session || !project) {
      setProjectGlossary([])
      return
    }
    try {
      const result = await request<ProjectGlossaryTerm[]>(`/api/projects/${project.id}/glossary`)
      setProjectGlossary(result)
    } catch {
      setProjectGlossary([])
    }
  }

  async function loadProjectTemplates() {
    if (!session) return
    try {
      const result = await request<ProjectTemplate[]>('/api/projects/templates')
      setProjectTemplates(result)
    } catch {
      setProjectTemplates([])
    }
  }

  async function loadProjects() {
    if (!session) return
    const result = await request<Project[]>('/api/projects')
    setProjects(result)
    if (!selectedProject && result.length > 0) {
      setSelectedProject(result[0])
    }
    if (result.length === 0) {
      setSelectedProject(null)
    }
  }

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const project = await request<Project>('/api/projects', {
      method: 'POST',
      body: JSON.stringify({
        name: String(form.get('name')),
        description: String(form.get('description')),
      }),
    })
    event.currentTarget.reset()
    setProjects((current) => [project, ...current])
    setSelectedProject(project)
    await refreshOperationalPanels()
  }

  async function updateProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedProject) return
    const form = new FormData(event.currentTarget)
    try {
      const project = await request<Project>(`/api/projects/${selectedProject.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          name: String(form.get('project_name')),
          description: String(form.get('project_description')),
        }),
      })
      setSelectedProject(project)
      setProjects((current) => current.map((item) => (item.id === project.id ? project : item)))
      setMessage('Projeto atualizado')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao atualizar projeto')
    }
  }

  async function archiveProject() {
    if (!selectedProject) return
    try {
      const project = await request<Project>(`/api/projects/${selectedProject.id}/archive`, {
        method: 'POST',
      })
      setSelectedProject(project)
      setProjects((current) => current.map((item) => (item.id === project.id ? project : item)))
      setMessage('Projeto arquivado')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao arquivar projeto')
    }
  }

  async function createGlossaryTerm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedProject) return
    const form = new FormData(event.currentTarget)
    try {
      const term = await request<ProjectGlossaryTerm>(`/api/projects/${selectedProject.id}/glossary`, {
        method: 'POST',
        body: JSON.stringify({
          term: String(form.get('term')),
          definition: String(form.get('definition')),
          aliases: parseAliases(form.get('aliases')),
        }),
      })
      event.currentTarget.reset()
      setProjectGlossary((current) => [...current.filter((item) => item.id !== term.id), term])
      setMessage('Termo adicionado')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao salvar termo')
    }
  }

  async function createProjectTemplate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const defaultTerm = String(form.get('template_term')).trim()
    try {
      const template = await request<ProjectTemplate>('/api/projects/templates', {
        method: 'POST',
        body: JSON.stringify({
          name: String(form.get('template_name')),
          description: String(form.get('template_description')),
          default_objective: String(form.get('template_objective')),
          default_glossary_terms: defaultTerm
            ? [
                {
                  term: defaultTerm,
                  definition: String(form.get('template_definition')),
                  aliases: parseAliases(form.get('template_aliases')),
                },
              ]
            : [],
        }),
      })
      event.currentTarget.reset()
      setProjectTemplates((current) => [template, ...current.filter((item) => item.id !== template.id)])
      setMessage('Template criado')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao criar template')
    }
  }

  async function createProjectFromTemplate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const templateId = String(form.get('template_id'))
    if (!templateId) return
    try {
      const project = await request<Project>(`/api/projects/templates/${templateId}/projects`, {
        method: 'POST',
        body: JSON.stringify({
          name: String(form.get('project_name')),
        }),
      })
      event.currentTarget.reset()
      setProjects((current) => [project, ...current])
      setSelectedProject(project)
      setProjectTab('overview')
      await Promise.all([loadProjectGlossary(project), loadProjectMembers(project), loadProjectTemplates()])
      setMessage('Projeto criado pelo template')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao usar template')
    }
  }

  async function createTenantInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    try {
      const invite = await request<TenantInvite>('/api/auth/tenant/invites', {
        method: 'POST',
        body: JSON.stringify({
          email: String(form.get('email')),
          role: String(form.get('role')),
        }),
      })
      event.currentTarget.reset()
      setTenantInvites((current) => [invite, ...current.filter((item) => item.id !== invite.id)])
      setMessage('Convite criado')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao criar convite')
    }
  }

  async function acceptTenantInvite(invite: TenantInvite) {
    try {
      await request<TenantMember>(`/api/auth/tenant/invites/${invite.id}/accept`, {
        method: 'POST',
      })
      await Promise.all([loadPendingInvites(), loadTenantAccess()])
      setMessage('Convite aceito')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao aceitar convite')
    }
  }

  async function updateTenantMemberRole(member: TenantMember, role: string) {
    try {
      const updated = await request<TenantMember>(`/api/auth/tenant/members/${member.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ role }),
      })
      setTenantMembers((current) => current.map((item) => (item.id === updated.id ? updated : item)))
      setMessage('Papel atualizado')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao atualizar papel')
    }
  }

  async function addProjectMember(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedProject) return
    const form = new FormData(event.currentTarget)
    try {
      const member = await request<ProjectMember>(`/api/projects/${selectedProject.id}/members`, {
        method: 'POST',
        body: JSON.stringify({
          user_id: String(form.get('user_id')),
          role: String(form.get('role')),
        }),
      })
      event.currentTarget.reset()
      setProjectMembers((current) => [member, ...current.filter((item) => item.id !== member.id)])
      setMessage('Membro do projeto atualizado')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao atualizar projeto')
    }
  }

  async function loadMeetings(project: Project) {
    const result = await request<Meeting[]>(`/api/projects/${project.id}/meetings`)
    setMeetings(result)
    if (result.length > 0) {
      setSelectedMeeting(result[0])
    } else {
      setSelectedMeeting(null)
      setHasConsent(false)
      setTranscript([])
      setRules([])
      setQuestions([])
      setDecisions([])
      setAgentRuns([])
      setMeetingSummary(null)
    }
  }

  async function loadMeetingTemplates() {
    if (!session) return
    const result = await request<MeetingTemplate[]>('/api/meetings/templates')
    setMeetingTemplates(result)
  }

  async function loadProjectGapSummary(project: Project | null = selectedProject) {
    if (!project) {
      setProjectGapSummary(null)
      return
    }
    const result = await request<ProjectGapSummary>(`/api/projects/${project.id}/gaps/summary`)
    setProjectGapSummary(result)
  }

  async function loadMeetingSummary(meeting: Meeting | null = selectedMeeting) {
    if (!meeting) {
      setMeetingSummary(null)
      return
    }
    const result = await request<MeetingSummary>(`/api/meetings/${meeting.id}/summary`)
    setMeetingSummary(result)
  }

  async function loadDocuments() {
    if (!session) return
    const result = await request<DocumentResult[]>('/api/documents')
    setDocuments(result)
  }

  async function loadDocumentDetails(document: DocumentResult) {
    const [sections, versions, exportJobs, comments] = await Promise.all([
      request<DocumentSection[]>(`/api/documents/${document.id}/sections`),
      request<DocumentVersion[]>(`/api/documents/${document.id}/versions`),
      request<DocumentExportJob[]>(`/api/documents/${document.id}/export-jobs`),
      request<CommentItem[]>(`/api/comments?resource_type=document&resource_id=${document.id}`),
    ])
    setDocumentSections(sections)
    setDocumentVersions(versions)
    setDocumentExportJobs(exportJobs)
    setDocumentComments(comments)
    setDocumentDiff(null)
    setDocumentRevisionDraft(document.content)
  }

  async function loadAuditLogs() {
    if (!session) return
    try {
      const params = new URLSearchParams({ limit: '12' })
      if (auditActionFilter.trim()) {
        params.set('action', auditActionFilter.trim())
      }
      const result = await request<AuditLog[]>(`/api/audit/logs?${params.toString()}`)
      setAuditLogs(result)
    } catch {
      setAuditLogs([])
    }
  }

  async function loadUsageSummary() {
    if (!session) return
    try {
      const result = await request<UsageSummaryItem[]>('/api/usage/summary')
      setUsageSummary(result)
    } catch {
      setUsageSummary([])
    }
  }

  async function loadBillingStatus() {
    if (!session) return
    try {
      const result = await request<BillingStatus>('/api/billing/status')
      setBillingStatus(result)
    } catch {
      setBillingStatus(null)
    }
  }

  async function loadBetaFeedback() {
    if (!session || !canManageTenantAccess) {
      setBetaFeedback([])
      return
    }
    try {
      const result = await request<BetaFeedback[]>('/api/feedback/beta?limit=8')
      setBetaFeedback(result)
    } catch {
      setBetaFeedback([])
    }
  }

  async function loadNotifications() {
    if (!session) return
    try {
      const result = await request<NotificationItem[]>('/api/notifications?limit=8')
      setNotifications(result)
    } catch {
      setNotifications([])
    }
  }

  async function loadAnalyticsSummary() {
    if (!session) return
    try {
      const result = await request<AnalyticsSummary>('/api/analytics/summary')
      setAnalyticsSummary(result)
    } catch {
      setAnalyticsSummary(null)
    }
  }

  async function loadAgentRuns(meeting: Meeting | null = selectedMeeting) {
    if (!session || !meeting) {
      setAgentRuns([])
      return
    }
    const result = await request<AgentRun[]>(`/api/meetings/${meeting.id}/agent-runs`)
    setAgentRuns(result)
  }

  async function searchRagMemory(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault()
    if (!selectedProject || ragQuery.trim().length < 2) {
      setRagResults([])
      return
    }
    const params = new URLSearchParams({ query: ragQuery.trim(), limit: '6' })
    const result = await request<RagSearchResult[]>(
      `/api/projects/${selectedProject.id}/rag/search?${params.toString()}`,
    )
    setRagResults(result)
  }

  async function searchGlobal(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault()
    if (globalSearchQuery.trim().length < 2) {
      setGlobalSearchResults([])
      return
    }
    const params = new URLSearchParams({ query: globalSearchQuery.trim(), limit: '10' })
    const result = await request<GlobalSearchResult[]>(`/api/search/global?${params.toString()}`)
    setGlobalSearchResults(result)
  }

  async function refreshOperationalPanels() {
    await Promise.all([
      loadDocuments(),
      loadAuditLogs(),
      loadUsageSummary(),
      loadBillingStatus(),
      loadTenantAccess(),
      loadTenantMembers(),
      loadTenantInvites(),
      loadPendingInvites(),
      loadProjectMembers(),
      loadProjectTemplates(),
      loadMeetingTemplates(),
      loadProjectGapSummary(),
      loadMeetingSummary(),
      loadBetaFeedback(),
      loadNotifications(),
      loadAnalyticsSummary(),
    ])
  }

  async function createMeeting(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedProject) return
    const form = new FormData(event.currentTarget)
    const meeting = await request<Meeting>(`/api/projects/${selectedProject.id}/meetings`, {
      method: 'POST',
      body: JSON.stringify({
        title: String(form.get('title')),
        objective: String(form.get('objective')),
      }),
    })
    event.currentTarget.reset()
    setMeetings((current) => [meeting, ...current])
    setSelectedMeeting(meeting)
    setHasConsent(false)
    setMeetingConsent(null)
    setMeetingParticipants([])
    setMeetingLifecycle([])
    setTranscript([])
    setRules([])
    setQuestions([])
    setDecisions([])
    setAgentRuns([])
    setDocumentResult(null)
    setDocumentSections([])
    setDocumentVersions([])
    await refreshOperationalPanels()
  }

  async function loadMeetingState(meeting: Meeting) {
    const state = await request<{
      meeting: Meeting
      has_consent: boolean
      consent: MeetingConsent | null
      participants: MeetingParticipant[]
      lifecycle_events: MeetingLifecycleEvent[]
      transcript: Transcript[]
      rules: Rule[]
      questions: QuestionInsight[]
      decisions: DecisionInsight[]
    }>(`/api/meetings/${meeting.id}/state`)
    setSelectedMeeting(state.meeting)
    setHasConsent(state.has_consent)
    setMeetingConsent(state.consent)
    setMeetingParticipants(state.participants)
    setMeetingLifecycle(state.lifecycle_events)
    setTranscript(state.transcript)
    setRules(state.rules)
    setQuestions(state.questions)
    setDecisions(state.decisions)
    await Promise.all([loadAgentRuns(state.meeting), loadMeetingSummary(state.meeting)])
  }

  async function acceptConsent() {
    if (!selectedMeeting) return
    await request(`/api/meetings/${selectedMeeting.id}/consent`, {
      method: 'POST',
      body: JSON.stringify({
        text_version: 'v1',
        accepted_scope: { audio: true, transcription: true, ai_analysis: true },
      }),
    })
    setHasConsent(true)
    await loadMeetingState(selectedMeeting)
    await refreshOperationalPanels()
  }

  async function revokeConsent() {
    if (!selectedMeeting) return
    try {
      await request(`/api/meetings/${selectedMeeting.id}/consent/revoke`, {
        method: 'POST',
        body: JSON.stringify({ reason: 'Revogado pela interface' }),
      })
      setHasConsent(false)
      setMeetingConsent(null)
      await loadMeetingState(selectedMeeting)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao revogar consentimento')
    }
  }

  async function addMeetingParticipant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedMeeting) return
    const form = new FormData(event.currentTarget)
    try {
      await request<MeetingParticipant>(`/api/meetings/${selectedMeeting.id}/participants`, {
        method: 'POST',
        body: JSON.stringify({
          user_id: String(form.get('user_id')),
          role: String(form.get('role')),
          consent_required: form.get('consent_required') === 'on',
        }),
      })
      event.currentTarget.reset()
      await loadMeetingState(selectedMeeting)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Falha ao adicionar participante')
    }
  }

  async function startMeeting() {
    if (!selectedMeeting) return
    const meeting = await request<Meeting>(`/api/meetings/${selectedMeeting.id}/start`, {
      method: 'POST',
    })
    setSelectedMeeting(meeting)
    shouldReconnectRef.current = true
    connectSocket(meeting)
    await refreshOperationalPanels()
  }

  async function pauseMeeting() {
    if (!selectedMeeting) return
    stopMicrophone()
    shouldReconnectRef.current = false
    socketRef.current?.close()
    setConnectionState('offline')
    const meeting = await request<Meeting>(`/api/meetings/${selectedMeeting.id}/pause`, {
      method: 'POST',
    })
    setSelectedMeeting(meeting)
    await refreshOperationalPanels()
  }

  async function createMeetingFromTemplate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedProject) return
    const form = new FormData(event.currentTarget)
    const templateKey = String(form.get('template_key'))
    if (!templateKey) return
    const meeting = await request<Meeting>(`/api/projects/${selectedProject.id}/meetings/from-template`, {
      method: 'POST',
      body: JSON.stringify({
        template_key: templateKey,
        title: String(form.get('title') || '').trim() || undefined,
      }),
    })
    event.currentTarget.reset()
    setMeetings((current) => [meeting, ...current])
    setSelectedMeeting(meeting)
    await refreshOperationalPanels()
  }

  async function submitBetaFeedback(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const feedback = await request<BetaFeedback>('/api/feedback/beta', {
      method: 'POST',
      body: JSON.stringify({
        project_id: selectedProject?.id ?? null,
        rating: Number(form.get('rating') || 5),
        category: String(form.get('category') || 'general'),
        comment: String(form.get('comment') || ''),
      }),
    })
    event.currentTarget.reset()
    setBetaFeedback((current) => [feedback, ...current])
    setMessage('Feedback registrado')
  }

  async function resumeMeeting() {
    if (!selectedMeeting) return
    const meeting = await request<Meeting>(`/api/meetings/${selectedMeeting.id}/resume`, {
      method: 'POST',
    })
    setSelectedMeeting(meeting)
    shouldReconnectRef.current = true
    connectSocket(meeting)
    await refreshOperationalPanels()
  }

  async function finishMeeting() {
    if (!selectedMeeting) return
    stopMicrophone()
    shouldReconnectRef.current = false
    socketRef.current?.close()
    setConnectionState('offline')
    const meeting = await request<Meeting>(`/api/meetings/${selectedMeeting.id}/finish`, {
      method: 'POST',
    })
    setSelectedMeeting(meeting)
    await refreshOperationalPanels()
  }

  function nextWsEventId() {
    wsEventCounterRef.current += 1
    return `web-${Date.now()}-${wsEventCounterRef.current}`
  }

  function stopHeartbeat() {
    if (heartbeatRef.current !== null) {
      window.clearInterval(heartbeatRef.current)
      heartbeatRef.current = null
    }
  }

  function sendSocketEvent(eventType: string, payload: Record<string, unknown>) {
    const socket = socketRef.current
    if (!socket || socket.readyState !== WebSocket.OPEN) return false
    socket.send(
      JSON.stringify({
        event_id: nextWsEventId(),
        event_type: eventType,
        payload,
      }),
    )
    return true
  }

  function connectSocket(meeting: Meeting) {
    if (!session) return
    socketRef.current?.close()
    stopHeartbeat()
    setConnectionState('connecting')
    const socket = new WebSocket(`${wsBase}/ws/meetings/${meeting.id}?token=${session.access_token}`)
    socketRef.current = socket
    socket.onopen = () => {
      setConnectionState('online')
      sendSocketEvent(lastPongAt ? 'client.resume_connection' : 'client.join_meeting', {})
      heartbeatRef.current = window.setInterval(() => {
        sendSocketEvent('system.ping', {})
      }, 15000)
    }
    socket.onclose = () => {
      setConnectionState('offline')
      stopHeartbeat()
      stopMicrophone()
      if (shouldReconnectRef.current && meeting.status === 'active') {
        window.setTimeout(() => connectSocket(meeting), 2500)
      }
    }
    socket.onerror = () => {
      setConnectionState('offline')
      stopHeartbeat()
      stopMicrophone()
    }
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data) as WsEvent
      if (data.event_type === 'system.pong') {
        setLastPongAt(String(data.payload.server_time ?? new Date().toISOString()))
      }
      if (data.event_type === 'transcript.partial') {
        const partial = data.payload as Transcript
        setTranscript((current) => {
          const id = partial.id ?? partial.chunk_id
          return [partial, ...current.filter((item) => (item.id ?? item.chunk_id) !== id)]
        })
      }
      if (data.event_type === 'transcript.final') {
        setTranscript((current) => [data.payload as Transcript, ...current])
      }
      if (data.event_type === 'ai.rule.detected') {
        setRules((current) => [data.payload as Rule, ...current])
      }
      if (data.event_type === 'ai.question.suggested') {
        setQuestions((current) => [data.payload as QuestionInsight, ...current])
      }
      if (data.event_type === 'ai.decision.detected') {
        setDecisions((current) => [data.payload as DecisionInsight, ...current])
      }
      if (data.event_type.startsWith('error.')) {
        setMessage(String((data.payload.message as string) ?? 'Evento recusado'))
      }
      if (data.event_type === 'system.ack') {
        Promise.all([
          loadUsageSummary(),
          loadAgentRuns(meeting),
          selectedProject ? searchRagMemory() : Promise.resolve(),
        ]).catch((error) => setMessage(error.message))
      }
    }
  }

  function getSupportedAudioMimeType() {
    const mimeTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4']
    return mimeTypes.find((mimeType) => MediaRecorder.isTypeSupported(mimeType)) ?? ''
  }

  function blobToBase64(blob: Blob) {
    return new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onerror = () => reject(reader.error)
      reader.onloadend = () => {
        const result = String(reader.result ?? '')
        resolve(result.includes(',') ? result.split(',')[1] : result)
      }
      reader.readAsDataURL(blob)
    })
  }

  async function startMicrophone() {
    if (!canStreamAudio) return
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      setMicState('error')
      setMessage('Microfone indisponivel neste navegador')
      return
    }

    setMicState('requesting')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })
      const mimeType = getSupportedAudioMimeType()
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)

      mediaStreamRef.current = stream
      mediaRecorderRef.current = recorder
      audioSequenceRef.current = 0
      setAudioChunksSent(0)
      setAudioMimeType(recorder.mimeType || mimeType || 'audio')

      recorder.ondataavailable = async (event) => {
        if (event.data.size === 0) return
        if (socketRef.current?.readyState !== WebSocket.OPEN) return

        try {
          const audioBase64 = await blobToBase64(event.data)
          const sequence = audioSequenceRef.current + 1
          audioSequenceRef.current = sequence
          sendSocketEvent('audio.chunk', {
            audio_base64: audioBase64,
            mime_type: event.data.type || recorder.mimeType || mimeType || 'audio/webm',
            sequence,
            size_bytes: event.data.size,
            captured_at: new Date().toISOString(),
          })
          setAudioChunksSent(sequence)
        } catch {
          setMicState('error')
          setMessage('Falha ao preparar chunk de audio')
        }
      }

      recorder.onerror = () => {
        setMicState('error')
        setMessage('Falha na captura do microfone')
      }

      recorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop())
        setMicState((current) => (current === 'error' ? current : 'idle'))
      }

      recorder.start(2500)
      setMicState('recording')
    } catch (error) {
      setMicState('error')
      setMessage(error instanceof Error ? error.message : 'Falha ao acessar microfone')
    }
  }

  function stopMicrophone() {
    const recorder = mediaRecorderRef.current
    if (recorder && recorder.state !== 'inactive') {
      recorder.stop()
    }
    mediaRecorderRef.current = null
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop())
    mediaStreamRef.current = null
    setMicState('idle')
  }

  function sendDemoChunk() {
    sendSocketEvent('audio.chunk', { text: demoText, source: 'manual_text' })
  }

  async function changeRuleStatus(ruleId: string, action: 'approve' | 'reject') {
    const rule = await request<Rule>(`/api/rules/${ruleId}/${action}`, { method: 'POST' })
    setRules((current) => current.map((item) => (item.id === rule.id ? rule : item)))
    await refreshOperationalPanels()
  }

  async function changeRuleLifecycle(ruleId: string, action: 'archive' | 'revoke') {
    const rule = await request<Rule>(`/api/rules/${ruleId}/${action}`, {
      method: 'POST',
      body: JSON.stringify({ reason: 'Atualizado pela interface' }),
    })
    setRules((current) => current.map((item) => (item.id === rule.id ? rule : item)))
    await refreshOperationalPanels()
  }

  async function loadRuleEvidence(ruleId: string) {
    if (ruleEvidence[ruleId]) {
      setRuleEvidence((current) => {
        const next = { ...current }
        delete next[ruleId]
        return next
      })
      return
    }
    const evidence = await request<Transcript[]>(`/api/rules/${ruleId}/evidence`)
    setRuleEvidence((current) => ({ ...current, [ruleId]: evidence }))
  }

  function startRuleRevision(rule: Rule) {
    setEditingRuleId(rule.id)
    setRevisionDraft(rule.rule_text)
  }

  async function saveRuleRevision(ruleId: string) {
    const rule = await request<Rule>(`/api/rules/${ruleId}/versions`, {
      method: 'POST',
      body: JSON.stringify({
        rule_text: revisionDraft,
        change_reason: 'Revisao manual pela interface',
      }),
    })
    setRules((current) => current.map((item) => (item.id === rule.id ? rule : item)))
    setEditingRuleId(null)
    setRevisionDraft('')
    await Promise.all([refreshOperationalPanels(), selectedProject ? searchRagMemory() : Promise.resolve()])
  }

  async function replaceRule(ruleId: string) {
    const rule = await request<Rule>(`/api/rules/${ruleId}/replace`, {
      method: 'POST',
      body: JSON.stringify({
        rule_text: revisionDraft,
        change_reason: 'Substituicao manual pela interface',
      }),
    })
    setRules((current) => [rule, ...current.map((item) => (item.id === ruleId ? { ...item, status: 'replaced', replaced_by_rule_id: rule.id } : item))])
    setEditingRuleId(null)
    setRevisionDraft('')
    await Promise.all([refreshOperationalPanels(), selectedProject ? searchRagMemory() : Promise.resolve()])
  }

  async function generateDocument() {
    if (!selectedMeeting) return
    const result = await request<DocumentResult>(`/api/meetings/${selectedMeeting.id}/documents/generate`, {
      method: 'POST',
    })
    setDocumentResult(result)
    await loadDocumentDetails(result)
    setDocuments((current) => [result, ...current.filter((document) => document.id !== result.id)])
    await refreshOperationalPanels()
  }

  async function selectDocument(document: DocumentResult) {
    setDocumentResult(document)
    await loadDocumentDetails(document)
  }

  async function saveDocumentRevision() {
    if (!documentResult) return
    const result = await request<DocumentResult>(`/api/documents/${documentResult.id}/versions`, {
      method: 'POST',
      body: JSON.stringify({
        content: documentRevisionDraft,
        change_reason: 'Revisao manual pela interface',
      }),
    })
    setDocumentResult(result)
    setDocuments((current) => current.map((document) => (document.id === result.id ? result : document)))
    await Promise.all([loadDocumentDetails(result), refreshOperationalPanels()])
  }

  async function exportDocumentPdf() {
    if (!documentResult || !session) return
    const response = await fetch(`${apiBase}/api/documents/${documentResult.id}/export/pdf`, {
      headers: {
        Authorization: `Bearer ${session.access_token}`,
        'X-Tenant-Id': session.tenant.id,
      },
    })
    if (!response.ok) {
      setMessage('Falha ao exportar PDF')
      return
    }
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${documentResult.id}.pdf`
    link.click()
    URL.revokeObjectURL(url)
    await refreshOperationalPanels()
  }

  async function exportDocumentMarkdown() {
    if (!documentResult || !session) return
    const response = await fetch(`${apiBase}/api/documents/${documentResult.id}/export/markdown`, {
      headers: {
        Authorization: `Bearer ${session.access_token}`,
        'X-Tenant-Id': session.tenant.id,
      },
    })
    if (!response.ok) {
      setMessage('Falha ao exportar Markdown')
      return
    }
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${documentResult.id}.md`
    link.click()
    URL.revokeObjectURL(url)
    await refreshOperationalPanels()
  }

  async function exportDocumentExcel() {
    if (!documentResult || !session) return
    const response = await fetch(`${apiBase}/api/documents/${documentResult.id}/export/excel`, {
      headers: {
        Authorization: `Bearer ${session.access_token}`,
        'X-Tenant-Id': session.tenant.id,
      },
    })
    if (!response.ok) {
      setMessage('Falha ao exportar Excel')
      return
    }
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${documentResult.id}.xlsx`
    link.click()
    URL.revokeObjectURL(url)
    await refreshOperationalPanels()
  }

  async function createSignedExportUrl(format: 'pdf' | 'markdown' | 'excel') {
    if (!documentResult) return
    const result = await request<{ url: string; expires_in_seconds: number }>(
      `/api/documents/${documentResult.id}/export/${format}/signed-url`,
    )
    window.open(`${apiBase}${result.url}`, '_blank', 'noopener,noreferrer')
    setMessage(`URL assinada criada por ${result.expires_in_seconds}s`)
  }

  async function loadDocumentDiff() {
    if (!documentResult || documentVersions.length < 2) return
    const sorted = [...documentVersions].sort((a, b) => b.version_number - a.version_number)
    const result = await request<VersionDiff>(
      `/api/documents/${documentResult.id}/versions/diff?from_version=${sorted[1].version_number}&to_version=${sorted[0].version_number}`,
    )
    setDocumentDiff(result)
  }

  async function submitDocumentComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!documentResult) return
    const form = new FormData(event.currentTarget)
    const comment = await request<CommentItem>('/api/comments', {
      method: 'POST',
      body: JSON.stringify({
        project_id: documentResult.project_id,
        resource_type: 'document',
        resource_id: documentResult.id,
        body: String(form.get('body') || ''),
      }),
    })
    event.currentTarget.reset()
    setDocumentComments((current) => [comment, ...current])
    await Promise.all([loadNotifications(), loadAnalyticsSummary()])
  }

  async function createDocumentExportJob(format: 'pdf' | 'markdown' | 'excel' | 'jira' | 'confluence') {
    if (!documentResult) return
    const job = await request<DocumentExportJob>(`/api/documents/${documentResult.id}/export-jobs`, {
      method: 'POST',
      body: JSON.stringify({ format }),
    })
    setDocumentExportJobs((current) => [job, ...current])
    setDocumentResult((current) => (current ? { ...current, status: 'exported' } : current))
    await refreshOperationalPanels()
  }

  function clearWorkspaceState() {
    stopMicrophone()
    stopHeartbeat()
    socketRef.current?.close()
    setProjects([])
    setMeetings([])
    setSelectedProject(null)
    setProjectGapSummary(null)
    setSelectedMeeting(null)
    setMeetingSummary(null)
    setHasConsent(false)
    setMeetingConsent(null)
    setMeetingParticipants([])
    setMeetingLifecycle([])
    setTranscript([])
    setRules([])
    setQuestions([])
    setDecisions([])
    setAgentRuns([])
    setRagResults([])
    setRuleEvidence({})
    setDocuments([])
    setDocumentResult(null)
    setDocumentSections([])
    setDocumentVersions([])
    setDocumentExportJobs([])
    setDocumentComments([])
    setDocumentDiff(null)
    setAuditLogs([])
    setUsageSummary([])
    setBillingStatus(null)
    setTenantMembers([])
    setTenantInvites([])
    setProjectMembers([])
    setProjectGlossary([])
    setProjectTemplates([])
    setMeetingTemplates([])
    setBetaFeedback([])
    setNotifications([])
    setAnalyticsSummary(null)
    setGlobalSearchResults([])
    setProjectTab('overview')
    setConnectionState('offline')
    setLastPongAt(null)
  }

  function switchTenant(tenantId: string) {
    if (!session) return
    const access = tenantAccess.find((item) => item.tenant.id === tenantId)
    if (!access) return
    const nextSession = {
      ...session,
      tenant: { ...access.tenant, role: access.role },
    }
    localStorage.setItem('rulees.session', JSON.stringify(nextSession))
    clearWorkspaceState()
    setSession(nextSession)
  }

  function logout() {
    clearWorkspaceState()
    localStorage.removeItem('rulees.session')
    setSession(null)
    setTenantAccess([])
    setPendingInvites([])
  }

  useEffect(() => {
    loadProjects().catch((error) => setMessage(error.message))
    refreshOperationalPanels().catch((error) => setMessage(error.message))
  }, [session])

  useEffect(() => {
    if (selectedProject) {
      loadMeetings(selectedProject).catch((error) => setMessage(error.message))
      loadProjectMembers(selectedProject).catch((error) => setMessage(error.message))
      loadProjectGlossary(selectedProject).catch((error) => setMessage(error.message))
      loadProjectGapSummary(selectedProject).catch((error) => setMessage(error.message))
      searchRagMemory().catch((error) => setMessage(error.message))
    }
  }, [selectedProject?.id])

  useEffect(() => {
    if (selectedMeeting) {
      loadMeetingState(selectedMeeting).catch((error) => setMessage(error.message))
      loadMeetingSummary(selectedMeeting).catch((error) => setMessage(error.message))
    }
  }, [selectedMeeting?.id])

  useEffect(() => {
    const updateOnline = () => setBrowserOnline(navigator.onLine)
    window.addEventListener('online', updateOnline)
    window.addEventListener('offline', updateOnline)
    return () => {
      window.removeEventListener('online', updateOnline)
      window.removeEventListener('offline', updateOnline)
    }
  }, [])

  useEffect(() => {
    return () => {
      stopMicrophone()
      stopHeartbeat()
      socketRef.current?.close()
    }
  }, [])

  if (!session) {
    return (
      <main className="auth-shell">
        <section className="auth-panel">
          <img className="auth-logo" src="/brand/logo.svg" alt="Rulees" />
          <h1>Rulees</h1>
          <p>Plataforma de inteligencia de requisitos e regras de negocio com IA.</p>
          <div className="auth-tabs" role="tablist">
            <button className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')} type="button">
              <UserPlus size={16} /> Cadastro
            </button>
            <button className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')} type="button">
              <LogIn size={16} /> Login
            </button>
          </div>
          <form className="form-stack" onSubmit={handleAuth}>
            {mode === 'register' && (
              <>
                <label>
                  Nome
                  <input name="name" defaultValue="Founder Rulees" required />
                </label>
                <label>
                  Organizacao
                  <input name="organization" defaultValue="Rulees Beta" required />
                </label>
              </>
            )}
            <label>
              Email
              <input name="email" defaultValue="founder@rulees.dev" type="email" required />
            </label>
            <label>
              Senha
              <input name="password" defaultValue="rulees123" type="password" required minLength={8} />
            </label>
            <button className="primary-action" type="submit">
              {mode === 'register' ? <UserPlus size={18} /> : <LogIn size={18} />}
              Entrar
            </button>
          </form>
          {message && <p className="inline-message">{message}</p>}
        </section>
      </main>
    )
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-row">
          <img className="sidebar-logo" src="/brand/logo-reta.svg" alt="Rulees" />
          <span>{session.tenant.name}</span>
          {tenantAccess.length > 1 && (
            <select
              aria-label="Tenant ativo"
              className="tenant-switcher"
              value={session.tenant.id}
              onChange={(event) => switchTenant(event.target.value)}
            >
              {tenantAccess.map((access) => (
                <option key={access.id} value={access.tenant.id}>
                  {access.tenant.name} · {access.role}
                </option>
              ))}
            </select>
          )}
        </div>
        <nav>
          <button
            className={activeView === 'projects' ? 'nav-link active' : 'nav-link'}
            onClick={() => setActiveView('projects')}
            type="button"
          >
            <FolderKanban size={18} /> Projetos
          </button>
          <button
            className={activeView === 'meetings' ? 'nav-link active' : 'nav-link'}
            onClick={() => setActiveView('meetings')}
            type="button"
          >
            <Radio size={18} /> Reunioes
          </button>
          <button
            className={activeView === 'rules' ? 'nav-link active' : 'nav-link'}
            onClick={() => setActiveView('rules')}
            type="button"
          >
            <Bot size={18} /> Rules Ledger
          </button>
          <button
            className={activeView === 'documents' ? 'nav-link active' : 'nav-link'}
            onClick={() => setActiveView('documents')}
            type="button"
          >
            <FileText size={18} /> Documentos
          </button>
          <button
            className={activeView === 'audit' ? 'nav-link active' : 'nav-link'}
            onClick={() => setActiveView('audit')}
            type="button"
          >
            <ShieldCheck size={18} /> Auditoria
          </button>
        </nav>
        <button className="ghost-action" onClick={logout} type="button">
          Sair
        </button>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h1>Fluxo MVP</h1>
            <span>{session.user.name} · {session.tenant.role}</span>
          </div>
          <div className={`connection ${connectionState}`}>
            <Radio size={16} /> {browserOnline ? connectionState : 'offline navegador'}
          </div>
        </header>

        {message && (
          <div className="notice">
            <CircleAlert size={18} /> {message}
          </div>
        )}

        {activeView === 'projects' && (
          <>
            <section className="p1-grid">
              <div className="panel p1-panel">
                <div className="panel-title">
                  <BadgeCheck size={18} />
                  <h2>Onboarding</h2>
                </div>
                <div className="checklist">
                  {onboardingItems.map((item) => (
                    <span className={item.done ? 'check-item done' : 'check-item'} key={item.label}>
                      {item.done ? <Check size={14} /> : <CircleAlert size={14} />}
                      {item.label}
                    </span>
                  ))}
                </div>
              </div>

              <div className="panel p1-panel">
                <div className="panel-title">
                  <CircleHelp size={18} />
                  <h2>Lacunas</h2>
                  {projectGapSummary && <span className="status-pill ready">{projectGapSummary.readiness_score}</span>}
                </div>
                <div className="compact-list">
                  {projectGapSummary?.gaps.map((gap) => (
                    <div className="compact-row" key={gap}>
                      <span>{gap}</span>
                    </div>
                  ))}
                  {projectGapSummary && projectGapSummary.gaps.length === 0 && (
                    <p className="empty-state">Sem lacunas críticas.</p>
                  )}
                  {!projectGapSummary && <p className="empty-state">Selecione um projeto.</p>}
                </div>
              </div>

              <div className="panel p1-panel">
                <div className="panel-title">
                  <FileText size={18} />
                  <h2>Resumo</h2>
                </div>
                {meetingSummary ? (
                  <div className="summary-box">
                    <p>{meetingSummary.summary}</p>
                    {meetingSummary.next_steps.map((step) => (
                      <span key={step}>{step}</span>
                    ))}
                  </div>
                ) : (
                  <p className="empty-state">Selecione uma reuniao.</p>
                )}
              </div>
            </section>

            <section className="grid two-columns">
          <div className="panel">
            <div className="panel-title">
              <FolderKanban size={18} />
              <h2>Projetos</h2>
            </div>
            {canManageProjects && (
              <form className="inline-form" onSubmit={createProject}>
                <input name="name" placeholder="Nome do projeto" required />
                <input name="description" placeholder="Descricao curta" />
                <button type="submit" title="Criar projeto">
                  <Plus size={18} />
                </button>
              </form>
            )}
            <div className="list">
              {projects.map((project) => (
                <button
                  className={selectedProject?.id === project.id ? 'list-item selected' : 'list-item'}
                  key={project.id}
                  onClick={() => setSelectedProject(project)}
                  type="button"
                >
                  <strong>{project.name}</strong>
                  <span>{project.description || project.status}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-title">
              <Mic size={18} />
              <h2>Reunioes</h2>
            </div>
            <form className="inline-form" onSubmit={createMeeting}>
              <input name="title" placeholder="Titulo da reuniao" required />
              <input name="objective" placeholder="Objetivo" />
              <button disabled={!selectedProject} type="submit" title="Criar reuniao">
                <Plus size={18} />
              </button>
            </form>
            <form className="template-meeting-form" onSubmit={createMeetingFromTemplate}>
              <select name="template_key" defaultValue="" aria-label="Template de reuniao" required>
                <option value="" disabled>
                  Template
                </option>
                {meetingTemplates.map((template) => (
                  <option key={template.key} value={template.key}>
                    {template.title}
                  </option>
                ))}
              </select>
              <input name="title" placeholder="Titulo opcional" />
              <button disabled={!selectedProject || meetingTemplates.length === 0} type="submit" title="Criar pelo template">
                <Plus size={18} />
              </button>
            </form>
            <div className="list">
              {meetings.map((meeting) => (
                <button
                  className={selectedMeeting?.id === meeting.id ? 'list-item selected' : 'list-item'}
                  key={meeting.id}
                  onClick={() => setSelectedMeeting(meeting)}
                  type="button"
                >
                  <strong>{meeting.title}</strong>
                  <span>{meeting.status}</span>
                </button>
              ))}
            </div>
          </div>
        </section>

        {selectedProject && (
          <section className="panel project-detail">
            <div className="panel-title">
              <FolderKanban size={18} />
              <h2>{selectedProject.name}</h2>
              <span className={`status-pill ${selectedProject.status}`}>{selectedProject.status}</span>
            </div>

            <div className="detail-tabs" role="tablist">
              <button
                className={projectTab === 'overview' ? 'active' : ''}
                onClick={() => setProjectTab('overview')}
                type="button"
              >
                Resumo
              </button>
              <button
                className={projectTab === 'glossary' ? 'active' : ''}
                onClick={() => setProjectTab('glossary')}
                type="button"
              >
                Glossario
              </button>
              <button
                className={projectTab === 'templates' ? 'active' : ''}
                onClick={() => setProjectTab('templates')}
                type="button"
              >
                Templates
              </button>
              <button
                className={projectTab === 'members' ? 'active' : ''}
                onClick={() => setProjectTab('members')}
                type="button"
              >
                Membros
              </button>
            </div>

            {projectTab === 'overview' && (
              <div className="project-detail-body">
                {canManageProjects && selectedProject.status !== 'archived' ? (
                  <form className="project-edit-form" key={selectedProject.id} onSubmit={updateProject}>
                    <input name="project_name" defaultValue={selectedProject.name} required />
                    <input name="project_description" defaultValue={selectedProject.description} placeholder="Descricao" />
                    <button title="Salvar projeto" type="submit">
                      <Check size={18} />
                    </button>
                    <button className="danger-action" onClick={archiveProject} title="Arquivar projeto" type="button">
                      <Square size={18} />
                    </button>
                  </form>
                ) : (
                  <div className="detail-summary">
                    <strong>{selectedProject.name}</strong>
                    <span>{selectedProject.description || 'Sem descricao'}</span>
                  </div>
                )}
                <div className="detail-metrics">
                  <div>
                    <span>Reunioes</span>
                    <strong>{meetings.length}</strong>
                  </div>
                  <div>
                    <span>Termos</span>
                    <strong>{projectGlossary.length}</strong>
                  </div>
                  <div>
                    <span>Membros</span>
                    <strong>{projectMembers.length}</strong>
                  </div>
                </div>
              </div>
            )}

            {projectTab === 'glossary' && (
              <div className="project-detail-body">
                {canManageProjects && selectedProject.status !== 'archived' && (
                  <form className="glossary-form" onSubmit={createGlossaryTerm}>
                    <input name="term" placeholder="Termo" required />
                    <input name="definition" placeholder="Definicao" />
                    <input name="aliases" placeholder="Alias separados por virgula" />
                    <button title="Adicionar termo" type="submit">
                      <Plus size={18} />
                    </button>
                  </form>
                )}
                <div className="glossary-list">
                  {projectGlossary.map((term) => (
                    <article className="glossary-row" key={term.id}>
                      <strong>{term.term}</strong>
                      <p>{term.definition || 'Sem definicao'}</p>
                      {term.aliases.length > 0 && <span>{term.aliases.join(', ')}</span>}
                    </article>
                  ))}
                  {projectGlossary.length === 0 && <p className="empty-state">Sem termos no glossario.</p>}
                </div>
              </div>
            )}

            {projectTab === 'templates' && (
              <div className="project-detail-body">
                {canManageProjects && (
                  <>
                    <form className="template-form" onSubmit={createProjectTemplate}>
                      <input name="template_name" placeholder="Nome do template" required />
                      <input name="template_description" placeholder="Descricao" />
                      <input name="template_objective" placeholder="Objetivo padrao" />
                      <input name="template_term" placeholder="Termo inicial opcional" />
                      <input name="template_definition" placeholder="Definicao do termo" />
                      <input name="template_aliases" placeholder="Alias do termo" />
                      <button title="Criar template" type="submit">
                        <Plus size={18} />
                      </button>
                    </form>
                    <form className="template-use-form" onSubmit={createProjectFromTemplate}>
                      <select name="template_id" defaultValue="" aria-label="Template" required>
                        <option value="" disabled>
                          Template
                        </option>
                        {projectTemplates.map((template) => (
                          <option key={template.id} value={template.id}>
                            {template.name}
                          </option>
                        ))}
                      </select>
                      <input name="project_name" placeholder="Novo projeto" required />
                      <button disabled={projectTemplates.length === 0} title="Criar projeto pelo template" type="submit">
                        <Plus size={18} />
                      </button>
                    </form>
                  </>
                )}
                <div className="template-list">
                  {projectTemplates.map((template) => (
                    <article className="template-row" key={template.id}>
                      <strong>{template.name}</strong>
                      <p>{template.description || template.default_objective || 'Template sem descricao'}</p>
                      <span>{template.default_glossary_terms.length} termos iniciais</span>
                    </article>
                  ))}
                  {projectTemplates.length === 0 && <p className="empty-state">Sem templates cadastrados.</p>}
                </div>
              </div>
            )}

            {projectTab === 'members' && (
              <div className="project-detail-body">
                {canManageProjects && tenantMembers.length > 0 && (
                  <form className="access-form" onSubmit={addProjectMember}>
                    <select name="user_id" defaultValue="" aria-label="Usuario do projeto" required>
                      <option value="" disabled>
                        Membro
                      </option>
                      {tenantMembers.map((member) => (
                        <option key={member.id} value={member.user_id}>
                          {member.user?.name ?? member.user_id}
                        </option>
                      ))}
                    </select>
                    <select name="role" defaultValue="member" aria-label="Papel no projeto">
                      {projectRoleOptions.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                    <button title="Adicionar ao projeto" type="submit">
                      <Plus size={18} />
                    </button>
                  </form>
                )}
                <div className="project-member-list">
                  {projectMembers.map((member) => {
                    const tenantMember = tenantMemberByUserId.get(member.user_id)
                    return (
                      <div className="project-member-row" key={member.id}>
                        <div>
                          <strong>{tenantMember?.user?.name ?? member.user_id}</strong>
                          <span>{tenantMember?.user?.email ?? member.user_id}</span>
                        </div>
                        <span className="status-pill ready">{member.role}</span>
                      </div>
                    )
                  })}
                  {projectMembers.length === 0 && <p className="empty-state">Sem membros neste projeto.</p>}
                </div>
              </div>
            )}
          </section>
        )}
          </>
        )}

        {activeView === 'meetings' && (
          <section className="meeting-console solo">
          <div className="panel live-panel">
            <div className="panel-title">
              <Radio size={18} />
              <h2>Sala ao vivo</h2>
              {selectedMeeting && <span className={`status-pill ${selectedMeeting.status}`}>{selectedMeeting.status}</span>}
            </div>
            <div className="action-row">
              <button className="secondary-action" disabled={!selectedMeeting || hasConsent} onClick={acceptConsent} type="button">
                <ShieldCheck size={18} /> Consentimento
              </button>
              <button
                className="secondary-action"
                disabled={!selectedMeeting || !hasConsent || selectedMeeting?.status === 'active'}
                onClick={revokeConsent}
                type="button"
              >
                <X size={18} /> Revogar
              </button>
              <button className="primary-action" disabled={!selectedMeeting || !hasConsent} onClick={startMeeting} type="button">
                <Play size={18} /> Iniciar
              </button>
              <button className="secondary-action" disabled={selectedMeeting?.status !== 'active'} onClick={pauseMeeting} type="button">
                <Pause size={18} /> Pausar
              </button>
              <button className="secondary-action" disabled={selectedMeeting?.status !== 'paused'} onClick={resumeMeeting} type="button">
                <RefreshCw size={18} /> Retomar
              </button>
              <button className="danger-action" disabled={!selectedMeeting} onClick={finishMeeting} type="button">
                <Square size={18} /> Finalizar
              </button>
            </div>
            {meetingConsent && (
              <p className="consent-meta">
                Consentimento ativo desde {new Date(meetingConsent.accepted_at).toLocaleString('pt-BR')}
              </p>
            )}
            <div className="demo-sender">
              <div className="audio-controls">
                <button
                  aria-label="Iniciar captura do microfone"
                  disabled={!canStreamAudio || micState === 'recording'}
                  onClick={startMicrophone}
                  type="button"
                >
                  <Mic size={18} /> Microfone
                </button>
                <button
                  aria-label="Parar captura do microfone"
                  disabled={micState !== 'recording'}
                  onClick={stopMicrophone}
                  type="button"
                >
                  <Square size={18} /> Parar
                </button>
                <span className={`status-pill ${micState}`}>{micState}</span>
                <span className="audio-meta">
                  {audioChunksSent} chunks{audioMimeType ? ` · ${audioMimeType}` : ''}
                </span>
                <span className="audio-meta">
                  heartbeat {lastPongAt ? new Date(lastPongAt).toLocaleTimeString('pt-BR') : 'aguardando'}
                </span>
              </div>
              <textarea value={demoText} onChange={(event) => setDemoText(event.target.value)} />
              <button disabled={connectionState !== 'online'} onClick={sendDemoChunk} type="button">
                <Mic size={18} /> Enviar fala
              </button>
            </div>
            <div className="meeting-meta-grid">
              <div className="meeting-meta-panel">
                <strong>Participantes</strong>
                {canManageProjects && selectedMeeting && tenantMembers.length > 0 && (
                  <form className="participant-form" onSubmit={addMeetingParticipant}>
                    <select name="user_id" defaultValue="" aria-label="Participante" required>
                      <option value="" disabled>
                        Usuario
                      </option>
                      {tenantMembers.map((member) => (
                        <option key={member.id} value={member.user_id}>
                          {member.user?.name ?? member.user_id}
                        </option>
                      ))}
                    </select>
                    <select name="role" defaultValue="participant" aria-label="Papel na reuniao">
                      <option value="facilitator">facilitator</option>
                      <option value="participant">participant</option>
                      <option value="observer">observer</option>
                    </select>
                    <label className="checkbox-line">
                      <input name="consent_required" defaultChecked type="checkbox" />
                      Consentimento
                    </label>
                    <button title="Adicionar participante" type="submit">
                      <Plus size={16} />
                    </button>
                  </form>
                )}
                <div className="compact-list">
                  {meetingParticipants.map((participant) => {
                    const tenantMember = tenantMemberByUserId.get(participant.user_id)
                    return (
                      <div className="compact-row" key={participant.id}>
                        <span>{tenantMember?.user?.name ?? participant.user_id}</span>
                        <strong>{participant.role}</strong>
                      </div>
                    )
                  })}
                  {meetingParticipants.length === 0 && <p className="empty-state">Sem participantes.</p>}
                </div>
              </div>
              <div className="meeting-meta-panel">
                <strong>Lifecycle</strong>
                <div className="compact-list">
                  {meetingLifecycle.slice(-5).map((event) => (
                    <div className="compact-row" key={event.id}>
                      <span>{event.event_type}</span>
                      <strong>{event.to_status ?? event.from_status ?? '-'}</strong>
                    </div>
                  ))}
                  {meetingLifecycle.length === 0 && <p className="empty-state">Sem eventos.</p>}
                </div>
              </div>
            </div>
            <div className="transcript-feed">
              {transcript.map((chunk, index) => (
                <article className={chunk.is_final === false ? 'transcript-row partial' : 'transcript-row'} key={chunk.id ?? chunk.chunk_id ?? index}>
                  <div>
                    <strong>{chunk.speaker_label ?? 'speaker'}</strong>
                    <span>
                      {typeof chunk.start_time === 'number' ? `${chunk.start_time.toFixed(1)}s` : 'tempo pendente'}
                      {typeof chunk.end_time === 'number' ? ` - ${chunk.end_time.toFixed(1)}s` : ''}
                      {typeof chunk.confidence_score === 'number'
                        ? ` · ${Math.round(chunk.confidence_score * 100)}%`
                        : ''}
                    </span>
                    <span className={`status-pill ${chunk.is_final === false ? 'partial' : 'ready'}`}>
                      {chunk.is_final === false ? 'partial' : 'final'}
                    </span>
                  </div>
                  <p>{chunk.normalized_text}</p>
                </article>
              ))}
            </div>
          </div>
          </section>
        )}

        {activeView === 'rules' && (
          <section className="meeting-console solo">
          <div className="panel">
            <div className="panel-title">
              <Bot size={18} />
              <h2>Rules Ledger</h2>
            </div>
            <div className="rule-list">
              {rules.map((rule) => (
                <article className="rule-card" key={rule.id}>
                  <div>
                    <strong>{rule.code} · v{rule.version_number}</strong>
                    <span className={`status-pill ${rule.status}`}>{rule.status}</span>
                  </div>
                  <p>{rule.rule_text}</p>
                  {rule.rag_result_type && (
                    <small>
                      RAG {rule.rag_result_type}
                      {rule.requires_human_resolution ? ' · exige revisão humana' : ''}
                    </small>
                  )}
                  <small>
                    Qualidade {rule.quality_score} · Confianca {Math.round(rule.confidence_score * 100)}%
                    {typeof rule.quality_details?.evidence_count === 'number'
                      ? ` · ${rule.quality_details.evidence_count} evidencias`
                      : ''}
                  </small>
                  {rule.quality_details?.missing && rule.quality_details.missing.length > 0 && (
                    <small>Falta: {rule.quality_details.missing.join(', ')}</small>
                  )}
                  {rule.replaced_by_rule_id && <small>Substituida por {rule.replaced_by_rule_id}</small>}
                  <div className="rule-actions">
                    <button onClick={() => changeRuleStatus(rule.id, 'approve')} type="button" title="Aprovar regra">
                      <Check size={16} />
                    </button>
                    <button onClick={() => changeRuleStatus(rule.id, 'reject')} type="button" title="Rejeitar regra">
                      <X size={16} />
                    </button>
                    <button onClick={() => changeRuleLifecycle(rule.id, 'archive')} type="button" title="Arquivar regra">
                      <Archive size={16} />
                    </button>
                    <button onClick={() => changeRuleLifecycle(rule.id, 'revoke')} type="button" title="Revogar regra">
                      <CircleAlert size={16} />
                    </button>
                    <button onClick={() => startRuleRevision(rule)} type="button" title="Criar revisão">
                      <RefreshCw size={16} />
                    </button>
                    <button onClick={() => loadRuleEvidence(rule.id)} type="button" title="Ver evidências">
                      <FileText size={16} />
                    </button>
                  </div>
                  {ruleEvidence[rule.id] && (
                    <div className="evidence-list">
                      {ruleEvidence[rule.id].map((chunk) => (
                        <div className="evidence-row" key={chunk.id ?? chunk.chunk_id}>
                          <strong>{chunk.speaker_label ?? 'speaker'}</strong>
                          <span>
                            {typeof chunk.start_time === 'number' ? `${chunk.start_time.toFixed(1)}s` : 'sem tempo'}
                          </span>
                          <p>{chunk.normalized_text}</p>
                        </div>
                      ))}
                      {ruleEvidence[rule.id].length === 0 && <p className="empty-state">Sem evidência vinculada.</p>}
                    </div>
                  )}
                  {editingRuleId === rule.id && (
                    <div className="revision-box">
                      <textarea
                        aria-label="Texto revisado da regra"
                        value={revisionDraft}
                        onChange={(event) => setRevisionDraft(event.target.value)}
                      />
                      <button
                        disabled={revisionDraft.trim().length < 5}
                        onClick={() => saveRuleRevision(rule.id)}
                        type="button"
                      >
                        <Check size={16} /> Salvar revisão
                      </button>
                      <button
                        disabled={revisionDraft.trim().length < 5}
                        onClick={() => replaceRule(rule.id)}
                        type="button"
                      >
                        <RefreshCw size={16} /> Substituir regra
                      </button>
                    </div>
                  )}
                </article>
              ))}
            </div>
            <button className="primary-action full-width" disabled={!selectedMeeting} onClick={generateDocument} type="button">
              <FileText size={18} /> Gerar documento
            </button>
          </div>
          </section>
        )}

        {activeView === 'rules' && (
          <section className="insights-grid">
          <div className="panel">
            <div className="panel-title">
              <CircleHelp size={18} />
              <h2>Perguntas abertas</h2>
            </div>
            <div className="insight-list">
              {questions.map((question) => (
                <article className="insight-row" key={question.id}>
                  <div>
                    <strong>{question.question_text}</strong>
                    <span className={`status-pill ${question.priority}`}>{question.priority}</span>
                  </div>
                  <p>{question.reason}</p>
                  <small>{question.gap_type} · {Math.round(question.confidence_score * 100)}%</small>
                </article>
              ))}
              {questions.length === 0 && <p className="empty-state">Nenhuma pergunta sugerida.</p>}
            </div>
          </div>

          <div className="panel">
            <div className="panel-title">
              <BadgeCheck size={18} />
              <h2>Decisões detectadas</h2>
            </div>
            <div className="insight-list">
              {decisions.map((decision) => (
                <article className="insight-row" key={decision.id}>
                  <div>
                    <strong>{decision.decision_text}</strong>
                    <span className={`status-pill ${decision.status}`}>{decision.status}</span>
                  </div>
                  <small>{decision.decision_type} · {Math.round(decision.confidence_score * 100)}%</small>
                </article>
              ))}
              {decisions.length === 0 && <p className="empty-state">Nenhuma decisão detectada.</p>}
            </div>
          </div>
          </section>
        )}

        {activeView === 'audit' && (
          <section className="operational-grid">
          <div className="panel operational-panel access-panel">
            <div className="panel-title">
              <UserPlus size={18} />
              <h2>Acessos</h2>
            </div>

            {pendingInvites.length > 0 && (
              <div className="invite-list">
                {pendingInvites.map((invite) => (
                  <div className="invite-row" key={invite.id}>
                    <div>
                      <strong>{invite.tenant?.name ?? invite.tenant_id}</strong>
                      <span>{invite.role}</span>
                    </div>
                    <button
                      className="compact-icon-button"
                      onClick={() => acceptTenantInvite(invite)}
                      title="Aceitar convite"
                      type="button"
                    >
                      <Check size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {canManageTenantAccess && (
              <form className="access-form" onSubmit={createTenantInvite}>
                <input name="email" placeholder="email@empresa.com" type="email" required />
                <select name="role" defaultValue="member" aria-label="Papel do convite">
                  {tenantRoleChoices.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
                <button title="Convidar" type="submit">
                  <UserPlus size={18} />
                </button>
              </form>
            )}

            <div className="member-list">
              {tenantMembers.map((member) => (
                <div className="member-row" key={member.id}>
                  <div>
                    <strong>{member.user?.name ?? member.user_id}</strong>
                    <span>{member.user?.email ?? member.user_id}</span>
                  </div>
                  {canManageTenantAccess && member.user_id !== session.user.id ? (
                    <select
                      aria-label="Papel do membro"
                      value={member.role}
                      onChange={(event) => updateTenantMemberRole(member, event.target.value)}
                    >
                      {tenantRoleChoices.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <span className="status-pill ready">{member.role}</span>
                  )}
                </div>
              ))}
              {tenantMembers.length === 0 && <p className="empty-state">Sem membros visiveis.</p>}
            </div>

            {tenantInvites.length > 0 && (
              <div className="invite-list">
                {tenantInvites.slice(0, 5).map((invite) => (
                  <div className="invite-row" key={invite.id}>
                    <div>
                      <strong>{invite.email}</strong>
                      <span>{invite.role} · {invite.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="panel operational-panel usage-panel">
            <div className="panel-title">
              <Activity size={18} />
              <h2>Uso</h2>
            </div>
            <div className="metric-list">
              {usageSummary.map((item) => (
                <div className="metric-row" key={`${item.event_type}-${item.unit}`}>
                  <span>{item.event_type}</span>
                  <strong>{item.quantity} {item.unit}</strong>
                </div>
              ))}
              {usageSummary.length === 0 && <p className="empty-state">Sem uso registrado.</p>}
            </div>
          </div>

          <div className="panel operational-panel plan-panel">
            <div className="panel-title">
              <ShieldCheck size={18} />
              <h2>Plano</h2>
            </div>
            {billingStatus ? (
              <div className="billing-list">
                <div className="metric-row">
                  <span>{billingStatus.plan_name}</span>
                  <strong>{billingStatus.status}</strong>
                </div>
                {billingStatus.limits.slice(0, 5).map((item) => (
                  <div className="billing-row" key={item.event_type}>
                    <span>{item.event_type}</span>
                    <strong>{item.used}/{item.limit}</strong>
                  </div>
                ))}
                {billingStatus.estimated_costs.slice(0, 4).map((item) => (
                  <div className="billing-row cost-row" key={`cost-${item.event_type}`}>
                    <span>{item.event_type}</span>
                    <strong>US$ {item.estimated_cost_usd.toFixed(4)}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-state">Plano indisponivel para este papel.</p>
            )}
          </div>

          <div className="panel operational-panel audit-panel">
            <div className="panel-title">
              <History size={18} />
              <h2>Auditoria</h2>
            </div>
            <form
              className="audit-filter"
              onSubmit={(event) => {
                event.preventDefault()
                loadAuditLogs()
              }}
            >
              <input
                aria-label="Filtrar auditoria por ação"
                value={auditActionFilter}
                onChange={(event) => setAuditActionFilter(event.target.value)}
                placeholder="acao ex: rule.approve"
              />
              <button title="Filtrar auditoria" type="submit">
                <Search size={16} />
              </button>
            </form>
            <div className="audit-list">
              {auditLogs.map((log) => (
                <div className="audit-row" key={log.id}>
                  <strong>{log.action}</strong>
                  <span>{log.resource_type} · {new Date(log.created_at).toLocaleString('pt-BR')}</span>
                </div>
              ))}
              {auditLogs.length === 0 && <p className="empty-state">Sem eventos de auditoria.</p>}
            </div>
          </div>

          <div className="panel operational-panel feedback-panel">
            <div className="panel-title">
              <BadgeCheck size={18} />
              <h2>Feedback beta</h2>
            </div>
            <form className="feedback-form" onSubmit={submitBetaFeedback}>
              <select name="rating" defaultValue="5" aria-label="Nota do feedback">
                <option value="5">5</option>
                <option value="4">4</option>
                <option value="3">3</option>
                <option value="2">2</option>
                <option value="1">1</option>
              </select>
              <select name="category" defaultValue="ux" aria-label="Categoria do feedback">
                <option value="ux">ux</option>
                <option value="ai">ai</option>
                <option value="exports">exports</option>
                <option value="performance">performance</option>
              </select>
              <textarea name="comment" placeholder="Comentario" />
              <button className="secondary-action" type="submit">
                <Check size={16} /> Enviar
              </button>
            </form>
            {canManageTenantAccess && (
              <div className="compact-list">
                {betaFeedback.map((item) => (
                  <div className="compact-row" key={item.id}>
                    <span>{item.category} · {item.comment || 'sem comentario'}</span>
                    <strong>{item.rating}/5</strong>
                  </div>
                ))}
                {betaFeedback.length === 0 && <p className="empty-state">Sem feedback registrado.</p>}
              </div>
            )}
          </div>

          <div className="panel operational-panel global-search-panel">
            <div className="panel-title">
              <Search size={18} />
              <h2>Busca global</h2>
            </div>
            <form className="rag-form" onSubmit={searchGlobal}>
              <input
                aria-label="Busca global"
                value={globalSearchQuery}
                onChange={(event) => setGlobalSearchQuery(event.target.value)}
                placeholder="Buscar no tenant"
              />
              <button title="Buscar" type="submit">
                <Search size={18} />
              </button>
            </form>
            <div className="compact-list">
              {globalSearchResults.map((result) => (
                <div className="compact-row" key={`${result.source_type}-${result.source_id}`}>
                  <span>{result.source_type} · {result.title}</span>
                  <strong>{result.snippet}</strong>
                </div>
              ))}
              {globalSearchResults.length === 0 && <p className="empty-state">Sem resultados.</p>}
            </div>
          </div>

          <div className="panel operational-panel analytics-panel">
            <div className="panel-title">
              <Activity size={18} />
              <h2>Analytics</h2>
              {analyticsSummary && <span className="status-pill ready">{analyticsSummary.readiness_score}</span>}
            </div>
            {analyticsSummary ? (
              <div className="metric-list">
                <div className="metric-row"><span>Projetos</span><strong>{analyticsSummary.projects_total}</strong></div>
                <div className="metric-row"><span>Reunioes</span><strong>{analyticsSummary.meetings_total}</strong></div>
                <div className="metric-row"><span>Regras aprovadas</span><strong>{analyticsSummary.approved_rules}/{analyticsSummary.rules_total}</strong></div>
                <div className="metric-row"><span>Documentos</span><strong>{analyticsSummary.documents_total}</strong></div>
                <div className="metric-row"><span>Comentarios</span><strong>{analyticsSummary.comments_total}</strong></div>
              </div>
            ) : (
              <p className="empty-state">Analytics indisponivel para este papel.</p>
            )}
          </div>

          <div className="panel operational-panel notifications-panel">
            <div className="panel-title">
              <MessageSquare size={18} />
              <h2>Notificações</h2>
            </div>
            <div className="compact-list">
              {notifications.map((notification) => (
                <div className="compact-row" key={notification.id}>
                  <span>{notification.title}</span>
                  <strong>{notification.read_at ? 'lida' : 'nova'}</strong>
                </div>
              ))}
              {notifications.length === 0 && <p className="empty-state">Sem notificações.</p>}
            </div>
          </div>
          </section>
        )}

        {activeView === 'rules' && (
          <section className="rules-extra-grid">
            <div className="panel operational-panel agents-panel">
              <div className="panel-title">
                <Bot size={18} />
                <h2>Execuções IA</h2>
              </div>
              <div className="agent-list">
                {agentRuns.slice(0, 8).map((run) => (
                  <div className="agent-row" key={run.run_id}>
                    <strong>{run.agent_name}</strong>
                    <span>{run.agent_role}</span>
                    <small>
                      {run.status}
                      {typeof run.confidence_score === 'number'
                        ? ` · ${Math.round(run.confidence_score * 100)}%`
                        : ''}
                    </small>
                  </div>
                ))}
                {agentRuns.length === 0 && <p className="empty-state">Sem execuções registradas.</p>}
              </div>
            </div>

            <div className="panel operational-panel rag-panel">
              <div className="panel-title">
                <Search size={18} />
                <h2>Memória RAG</h2>
              </div>
              <form className="rag-form" onSubmit={searchRagMemory}>
                <input
                  aria-label="Buscar memória do projeto"
                  value={ragQuery}
                  onChange={(event) => setRagQuery(event.target.value)}
                  placeholder="Buscar regra ou contexto"
                />
                <button disabled={!selectedProject} title="Buscar memória" type="submit">
                  <Search size={18} />
                </button>
              </form>
              <div className="rag-list">
                {ragResults.map((result) => (
                  <div className="rag-row" key={result.source_id}>
                    <strong>{result.source_type}</strong>
                    <p>{result.content}</p>
                    <span>{Math.round(result.similarity_score * 100)}% similar</span>
                  </div>
                ))}
                {ragResults.length === 0 && <p className="empty-state">Sem memória compatível.</p>}
              </div>
            </div>
          </section>
        )}

        {activeView === 'documents' && (
          <section className="documents-grid">
            <div className="panel operational-panel documents-panel">
              <div className="panel-title">
                <FileText size={18} />
                <h2>Documentos</h2>
              </div>
              <div className="document-list">
                {documents.slice(0, 6).map((document) => (
                  <button
                    className="document-row"
                    key={document.id}
                    onClick={() => selectDocument(document).catch((error) => setMessage(error.message))}
                    type="button"
                  >
                    <strong>{document.title}</strong>
                    <span>{document.status}</span>
                  </button>
                ))}
                {documents.length === 0 && <p className="empty-state">Nenhum documento gerado.</p>}
              </div>
            </div>
          </section>
        )}

        {activeView === 'documents' && documentResult && (
          <section className="panel document-panel">
            <div className="panel-title">
              <FileText size={18} />
              <h2>{documentResult.title}</h2>
              <span className={`status-pill ${documentResult.status}`}>{documentResult.status}</span>
            </div>
            <pre>{documentResult.content}</pre>
            <div className="document-sections">
              {documentSections.map((section) => (
                <article className="document-section" key={section.id}>
                  <strong>{section.title}</strong>
                  <p>{section.body}</p>
                </article>
              ))}
            </div>
            <div className="document-versions">
              {documentVersions.map((version) => (
                <span className="status-pill ready" key={version.id}>
                  v{version.version_number} · {version.status}
                </span>
              ))}
            </div>
            <div className="document-revision">
              <textarea
                aria-label="Conteudo revisado do documento"
                value={documentRevisionDraft}
                onChange={(event) => setDocumentRevisionDraft(event.target.value)}
              />
              <button
                className="secondary-action"
                disabled={documentRevisionDraft.trim().length < 10}
                onClick={saveDocumentRevision}
                type="button"
              >
                <Check size={16} /> Salvar versão
              </button>
            </div>
            <div className="document-actions">
              <button className="secondary-action download-link" onClick={exportDocumentPdf} type="button">
                <Download size={16} /> PDF
              </button>
              <button className="secondary-action download-link" onClick={exportDocumentMarkdown} type="button">
                <Download size={16} /> Markdown
              </button>
              <button className="secondary-action download-link" onClick={exportDocumentExcel} type="button">
                <Download size={16} /> Excel
              </button>
              <button className="secondary-action download-link" onClick={() => createSignedExportUrl('pdf')} type="button">
                URL PDF
              </button>
              <button className="secondary-action download-link" onClick={() => createSignedExportUrl('excel')} type="button">
                URL Excel
              </button>
              <button
                className="secondary-action download-link"
                disabled={documentVersions.length < 2}
                onClick={loadDocumentDiff}
                type="button"
              >
                Comparar
              </button>
              <button className="secondary-action download-link" onClick={() => createDocumentExportJob('jira')} type="button">
                Jira
              </button>
              <button className="secondary-action download-link" onClick={() => createDocumentExportJob('confluence')} type="button">
                Confluence
              </button>
            </div>
            <div className="document-export-jobs">
              {documentExportJobs.map((job) => (
                <article className="export-job-row" key={job.id}>
                  <div>
                    <strong>{job.format}</strong>
                    <span className={`status-pill ${job.status}`}>{job.status}</span>
                  </div>
                  <small>{new Date(job.created_at).toLocaleString('pt-BR')}</small>
                  {['jira', 'confluence'].includes(job.format) && (
                    <pre>{JSON.stringify(job.payload, null, 2)}</pre>
                  )}
                </article>
              ))}
              {documentExportJobs.length === 0 && <p className="empty-state">Sem jobs de exportação.</p>}
            </div>
            {documentDiff && (
              <div className="diff-view">
                {documentDiff.lines.map((line, index) => (
                  <span className={`diff-line ${line.kind}`} key={`${line.kind}-${index}`}>
                    {line.kind === 'added' ? '+ ' : line.kind === 'removed' ? '- ' : '  '}
                    {line.text}
                  </span>
                ))}
              </div>
            )}
            <form className="comment-form" onSubmit={submitDocumentComment}>
              <textarea name="body" placeholder="Comentario do documento" required />
              <button className="secondary-action" type="submit">
                <MessageSquare size={16} /> Comentar
              </button>
            </form>
            <div className="comment-list">
              {documentComments.map((comment) => (
                <article className="comment-row" key={comment.id}>
                  <strong>{comment.author_id}</strong>
                  <p>{comment.body}</p>
                  <span>{new Date(comment.created_at).toLocaleString('pt-BR')}</span>
                </article>
              ))}
              {documentComments.length === 0 && <p className="empty-state">Sem comentarios.</p>}
            </div>
          </section>
        )}
      </section>
    </main>
  )
}

export default App
