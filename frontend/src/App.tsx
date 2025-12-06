import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import ConversationPage from './pages/ConversationPage'
import AgentStudioPage from './pages/AgentStudioPage'
import TeamBuilderPage from './pages/TeamBuilderPage'
import MCPManagerPage from './pages/MCPManagerPage'
import SettingsPage from './pages/SettingsPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ConversationPage />} />
        <Route path="/studio" element={<AgentStudioPage />} />
        <Route path="/teams" element={<TeamBuilderPage />} />
        <Route path="/mcp" element={<MCPManagerPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </Layout>
  )
}

export default App
