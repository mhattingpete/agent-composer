export default function TeamBuilderPage() {
  return (
    <div className="flex h-full gap-6">
      {/* Agent Picker */}
      <div className="w-64 flex-shrink-0">
        <div className="card h-full">
          <h2 className="text-lg font-semibold mb-4">Available Agents</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Drag agents to build your team
          </p>
        </div>
      </div>

      {/* Team Canvas */}
      <div className="flex-1 flex flex-col gap-4">
        {/* Execution Mode Selector */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Execution Mode</h2>
          <div className="flex gap-4">
            <label className="flex items-center gap-2">
              <input type="radio" name="mode" value="sequential" defaultChecked />
              <span>Sequential</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="radio" name="mode" value="parallel" />
              <span>Parallel</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="radio" name="mode" value="router" />
              <span>Router</span>
            </label>
          </div>
        </div>

        {/* Team Canvas */}
        <div className="card flex-1">
          <h2 className="text-lg font-semibold mb-4">Team Members</h2>
          <div className="h-64 rounded-lg border-2 border-dashed border-gray-300 dark:border-dark-600 flex items-center justify-center text-gray-500">
            Drop agents here to build your team
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <button className="btn-secondary">Test Team</button>
          <button className="btn-primary">Save Team</button>
        </div>
      </div>
    </div>
  )
}
