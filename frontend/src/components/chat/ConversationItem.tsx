import { clsx } from 'clsx'

export interface Conversation {
  id: string
  title: string
  agentId: string | null
  agentName?: string
  lastMessage?: string
  updatedAt: Date
  messageCount: number
}

interface ConversationItemProps {
  conversation: Conversation
  isSelected: boolean
  onSelect: () => void
  onDelete: () => void
}

export default function ConversationItem({
  conversation,
  isSelected,
  onSelect,
  onDelete,
}: ConversationItemProps) {
  const formattedDate = conversation.updatedAt.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  })

  return (
    <div
      className={clsx(
        'group flex items-center gap-2 p-3 rounded-lg cursor-pointer transition-colors',
        isSelected
          ? 'bg-primary-100 dark:bg-primary-900/20 border border-primary-500'
          : 'hover:bg-gray-100 dark:hover:bg-dark-700'
      )}
      onClick={onSelect}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium truncate text-gray-900 dark:text-gray-100">
            {conversation.title}
          </h3>
        </div>
        {conversation.lastMessage && (
          <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
            {conversation.lastMessage}
          </p>
        )}
        <div className="flex items-center gap-2 mt-1 text-xs text-gray-400 dark:text-gray-500">
          <span>{formattedDate}</span>
          <span className="w-1 h-1 rounded-full bg-gray-400" />
          <span>{conversation.messageCount} messages</span>
          {conversation.agentName && (
            <>
              <span className="w-1 h-1 rounded-full bg-gray-400" />
              <span className="truncate">{conversation.agentName}</span>
            </>
          )}
        </div>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation()
          onDelete()
        }}
        className="p-1.5 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all"
        title="Delete conversation"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  )
}
