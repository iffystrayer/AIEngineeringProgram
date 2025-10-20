import { LandingPage } from './components/LandingPage'

function App() {
  const handleStartNew = () => {
    console.log('Starting new questionnaire...')
    // TODO: Navigate to SessionForm
  }

  const handleResume = () => {
    console.log('Resuming session...')
    // TODO: Navigate to SessionList
  }

  return (
    <LandingPage onStartNew={handleStartNew} onResume={handleResume} />
  )
}

export default App
