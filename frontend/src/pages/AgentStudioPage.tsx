export default function AgentStudioPage() {
  return (
    <div className="flex h-full gap-6">
      {/* Agent Library Sidebar */}
      <div className="w-64 flex-shrink-0">
        <div className="card h-full">
          <h2 className="text-lg font-semibold mb-4">Agent Library</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Your agents will appear here
          </p>
        </div>
      </div>

      {/* Main Editor Area */}
      <div className="flex-1 flex flex-col gap-4">
        {/* Agent Description Input */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Create New Agent</h2>
          <textarea
            placeholder="Describe the agent you want to create... (e.g., 'An agent that helps me analyze CSV files and create charts')"
            className="input min-h-[100px] resize-none mb-4"
          />
          <button className="btn-primary">Generate Agent</button>
        </div>

        {/* Code Editor */}
        <div className="card flex-1">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Agent Code</h2>
            <div className="flex gap-2">
              <button className="btn-secondary" disabled>
                Accept
              </button>
              <button className="btn-secondary" disabled>
                Edit
              </button>
              <button className="btn-secondary" disabled>
                Regenerate
              </button>
              <button className="btn-danger" disabled>
                Delete
              </button>
            </div>
          </div>
          <div className="h-64 rounded-lg bg-gray-100 dark:bg-dark-700 flex items-center justify-center text-gray-500">
            Monaco Editor will be integrated here
          </div>
        </div>
      </div>
    </div>
  )
}
