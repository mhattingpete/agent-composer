export default function ConversationPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-auto p-4">
        {/* Chat messages will go here */}
        <div className="flex h-full items-center justify-center text-gray-500 dark:text-gray-400">
          <div className="text-center">
            <h2 className="text-xl font-semibold mb-2">Welcome to Agent Composer</h2>
            <p>Select an agent and start chatting</p>
          </div>
        </div>
      </div>

      {/* Chat input */}
      <div className="border-t border-gray-200 p-4 dark:border-dark-700">
        <div className="flex gap-4">
          <textarea
            placeholder="Type your message..."
            className="input min-h-[80px] resize-none"
            disabled
          />
          <button className="btn-primary h-fit" disabled>
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
