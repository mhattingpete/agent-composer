export default function MCPManagerPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">MCP Manager</h1>
        <button className="btn-primary">Add MCP Server</button>
      </div>

      {/* Connected Servers */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Connected Servers</h2>
        <div className="space-y-4">
          <p className="text-gray-500 dark:text-gray-400">
            No MCP servers connected. Click "Add MCP Server" to connect your first server.
          </p>
        </div>
      </div>

      {/* Server Catalog */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Popular MCP Servers</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {['Filesystem', 'GitHub', 'Slack', 'PostgreSQL', 'Memory'].map((server) => (
            <div
              key={server}
              className="rounded-lg border border-gray-200 p-4 dark:border-dark-700 hover:border-primary-500 cursor-pointer transition-colors"
            >
              <h3 className="font-medium">{server}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                MCP server for {server.toLowerCase()} integration
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
