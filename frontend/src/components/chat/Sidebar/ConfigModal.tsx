'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription
} from '@/components/ui/dialog'
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem
} from '@/components/ui/select'
import Icon from '@/components/ui/icon'
import { useStore } from '@/store'
import {
  getModelsAPI,
  createAgentAPI,
  createTeamAPI,
  type ModelInfo,
  type AgentConfigCreate,
  type TeamConfigCreate,
  type TeamMember
} from '@/api/os'
import useChatActions from '@/hooks/useChatActions'

interface ConfigModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  mode: 'agent' | 'team'
}

const DEFAULT_AGENT_INSTRUCTIONS = `You are a helpful AI assistant.

You have access to a Python interpreter with many useful tools. To accomplish tasks:

1. Write Python code using run_python_code
2. Install packages with uv_add if needed
3. Save and run files with save_and_run_python_file

Inside run_python_code, you have access to:
- web_search(query) - Search the web
- fetch_url(url) - Fetch and parse web pages
- shell(command) - Run shell commands
- read_file/write_file - File operations

Be helpful, accurate, and thorough.`

export function ConfigModal({ open, onOpenChange, mode }: ConfigModalProps) {
  const { selectedEndpoint, authToken } = useStore()
  const { initialize } = useChatActions()

  // Models state
  const [models, setModels] = useState<ModelInfo[]>([])
  const [isLoadingModels, setIsLoadingModels] = useState(false)

  // Agent form state
  const [agentName, setAgentName] = useState('')
  const [agentDescription, setAgentDescription] = useState('')
  const [agentModelId, setAgentModelId] = useState('')
  const [agentInstructions, setAgentInstructions] = useState(
    DEFAULT_AGENT_INSTRUCTIONS
  )

  // Team form state
  const [teamName, setTeamName] = useState('')
  const [teamDescription, setTeamDescription] = useState('')
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([
    { name: '', role: '', has_tools: false }
  ])

  // Submission state
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Load models when modal opens
  useEffect(() => {
    if (open && models.length === 0) {
      loadModels()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  const loadModels = async () => {
    setIsLoadingModels(true)
    const fetchedModels = await getModelsAPI(selectedEndpoint, authToken)
    setModels(fetchedModels)
    if (fetchedModels.length > 0 && !agentModelId) {
      setAgentModelId(fetchedModels[0].id)
    }
    setIsLoadingModels(false)
  }

  const resetForm = () => {
    setAgentName('')
    setAgentDescription('')
    setAgentModelId(models.length > 0 ? models[0].id : '')
    setAgentInstructions(DEFAULT_AGENT_INSTRUCTIONS)
    setTeamName('')
    setTeamDescription('')
    setTeamMembers([{ name: '', role: '', has_tools: false }])
  }

  const handleSubmitAgent = async () => {
    if (!agentName.trim() || !agentModelId) return

    setIsSubmitting(true)
    const agent: AgentConfigCreate = {
      name: agentName.trim(),
      description: agentDescription.trim(),
      model_id: agentModelId,
      instructions: agentInstructions.trim()
    }

    const result = await createAgentAPI(selectedEndpoint, agent, authToken)
    setIsSubmitting(false)

    if (result) {
      resetForm()
      onOpenChange(false)
      // Refresh the agent list
      await initialize()
    }
  }

  const handleSubmitTeam = async () => {
    if (!teamName.trim() || teamMembers.length === 0) return

    // Filter out empty members
    const validMembers = teamMembers.filter(
      (m) => m.name.trim() && m.role.trim()
    )
    if (validMembers.length === 0) return

    setIsSubmitting(true)
    const team: TeamConfigCreate = {
      name: teamName.trim(),
      description: teamDescription.trim(),
      members: validMembers.map((m) => ({
        name: m.name.trim(),
        role: m.role.trim(),
        has_tools: m.has_tools
      }))
    }

    const result = await createTeamAPI(selectedEndpoint, team, authToken)
    setIsSubmitting(false)

    if (result) {
      resetForm()
      onOpenChange(false)
      // Refresh the team list
      await initialize()
    }
  }

  const addTeamMember = () => {
    setTeamMembers([...teamMembers, { name: '', role: '', has_tools: false }])
  }

  const removeTeamMember = (index: number) => {
    if (teamMembers.length > 1) {
      setTeamMembers(teamMembers.filter((_, i) => i !== index))
    }
  }

  const updateTeamMember = (
    index: number,
    field: keyof TeamMember,
    value: string | boolean
  ) => {
    const updated = [...teamMembers]
    updated[index] = { ...updated[index], [field]: value }
    setTeamMembers(updated)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[80vh] max-w-lg overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="font-dmmono text-sm font-medium uppercase">
            {mode === 'agent' ? 'Create New Agent' : 'Create New Team'}
          </DialogTitle>
          <DialogDescription className="font-dmmono text-xs text-muted">
            {mode === 'agent'
              ? 'Configure a custom AI agent with specific instructions and model.'
              : 'Create a team of agents that work together.'}
          </DialogDescription>
        </DialogHeader>

        <div className="mt-4 space-y-4">
          {mode === 'agent' ? (
            // Agent Form
            <>
              <div className="space-y-2">
                <label className="font-dmmono text-xs font-medium uppercase text-primary">
                  Name
                </label>
                <input
                  type="text"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  placeholder="My Custom Agent"
                  className="flex h-9 w-full items-center rounded-xl border border-primary/15 bg-accent p-3 font-dmmono text-xs text-primary placeholder:text-muted"
                />
              </div>

              <div className="space-y-2">
                <label className="font-dmmono text-xs font-medium uppercase text-primary">
                  Description
                </label>
                <input
                  type="text"
                  value={agentDescription}
                  onChange={(e) => setAgentDescription(e.target.value)}
                  placeholder="A brief description of what this agent does"
                  className="flex h-9 w-full items-center rounded-xl border border-primary/15 bg-accent p-3 font-dmmono text-xs text-primary placeholder:text-muted"
                />
              </div>

              <div className="space-y-2">
                <label className="font-dmmono text-xs font-medium uppercase text-primary">
                  Model
                </label>
                <Select
                  value={agentModelId}
                  onValueChange={setAgentModelId}
                  disabled={isLoadingModels}
                >
                  <SelectTrigger className="h-9 w-full rounded-xl border border-primary/15 bg-accent font-dmmono text-xs">
                    <SelectValue
                      placeholder={
                        isLoadingModels ? 'Loading...' : 'Select a model'
                      }
                    />
                  </SelectTrigger>
                  <SelectContent className="border-none bg-accent font-dmmono shadow-lg">
                    {models.map((model) => (
                      <SelectItem
                        key={model.id}
                        value={model.id}
                        className="cursor-pointer"
                      >
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-muted">{model.provider}</span>
                          <span>{model.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="font-dmmono text-xs font-medium uppercase text-primary">
                  Instructions
                </label>
                <textarea
                  value={agentInstructions}
                  onChange={(e) => setAgentInstructions(e.target.value)}
                  placeholder="System instructions for the agent..."
                  rows={8}
                  className="flex w-full resize-none rounded-xl border border-primary/15 bg-accent p-3 font-dmmono text-xs text-primary placeholder:text-muted"
                />
              </div>
            </>
          ) : (
            // Team Form
            <>
              <div className="space-y-2">
                <label className="font-dmmono text-xs font-medium uppercase text-primary">
                  Team Name
                </label>
                <input
                  type="text"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  placeholder="My Research Team"
                  className="flex h-9 w-full items-center rounded-xl border border-primary/15 bg-accent p-3 font-dmmono text-xs text-primary placeholder:text-muted"
                />
              </div>

              <div className="space-y-2">
                <label className="font-dmmono text-xs font-medium uppercase text-primary">
                  Description
                </label>
                <input
                  type="text"
                  value={teamDescription}
                  onChange={(e) => setTeamDescription(e.target.value)}
                  placeholder="A team that researches and analyzes topics"
                  className="flex h-9 w-full items-center rounded-xl border border-primary/15 bg-accent p-3 font-dmmono text-xs text-primary placeholder:text-muted"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="font-dmmono text-xs font-medium uppercase text-primary">
                    Team Members
                  </label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={addTeamMember}
                    className="h-6 px-2 font-dmmono text-xs"
                  >
                    <Icon type="plus-icon" size="xxs" className="mr-1" />
                    Add Member
                  </Button>
                </div>

                <div className="space-y-3">
                  {teamMembers.map((member, index) => (
                    <div
                      key={index}
                      className="space-y-2 rounded-lg border border-primary/10 p-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-dmmono text-xs text-muted">
                          Member {index + 1}
                        </span>
                        {teamMembers.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeTeamMember(index)}
                            className="h-5 w-5 p-0 text-destructive hover:text-destructive"
                          >
                            <Icon type="x" size="xxs" />
                          </Button>
                        )}
                      </div>
                      <input
                        type="text"
                        value={member.name}
                        onChange={(e) =>
                          updateTeamMember(index, 'name', e.target.value)
                        }
                        placeholder="Name (e.g., Researcher)"
                        className="flex h-8 w-full items-center rounded-lg border border-primary/15 bg-accent p-2 font-dmmono text-xs text-primary placeholder:text-muted"
                      />
                      <input
                        type="text"
                        value={member.role}
                        onChange={(e) =>
                          updateTeamMember(index, 'role', e.target.value)
                        }
                        placeholder="Role (e.g., Find and gather information)"
                        className="flex h-8 w-full items-center rounded-lg border border-primary/15 bg-accent p-2 font-dmmono text-xs text-primary placeholder:text-muted"
                      />
                      <label className="flex cursor-pointer items-center gap-2">
                        <input
                          type="checkbox"
                          checked={member.has_tools}
                          onChange={(e) =>
                            updateTeamMember(index, 'has_tools', e.target.checked)
                          }
                          className="h-4 w-4 rounded border-primary/15"
                        />
                        <span className="font-dmmono text-xs text-muted">
                          Has access to tools
                        </span>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          <div className="flex justify-end gap-2 pt-4">
            <Button
              variant="ghost"
              onClick={() => onOpenChange(false)}
              className="font-dmmono text-xs uppercase"
            >
              Cancel
            </Button>
            <Button
              onClick={mode === 'agent' ? handleSubmitAgent : handleSubmitTeam}
              disabled={
                isSubmitting ||
                (mode === 'agent'
                  ? !agentName.trim() || !agentModelId
                  : !teamName.trim() ||
                    !teamMembers.some((m) => m.name.trim() && m.role.trim()))
              }
              className="font-dmmono text-xs uppercase"
            >
              {isSubmitting ? 'Creating...' : 'Create'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
