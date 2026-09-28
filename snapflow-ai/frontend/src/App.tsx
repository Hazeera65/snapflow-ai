import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import Assistant from './pages/Assistant'
import Images from './pages/Images'
import Voice from './pages/Voice'
import Tasks from './pages/Tasks'
import Benchmarks from './pages/Benchmarks'
import Hardware from './pages/Hardware'
import Privacy from './pages/Privacy'
import Settings from './pages/Settings'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/assistant" element={<Assistant />} />
          <Route path="/images" element={<Images />} />
          <Route path="/voice" element={<Voice />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/benchmarks" element={<Benchmarks />} />
          <Route path="/hardware" element={<Hardware />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
