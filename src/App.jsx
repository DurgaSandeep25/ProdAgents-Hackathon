import { useState, useEffect } from 'react'
import CoinSelector from './components/CoinSelector'
import RunButton from './components/RunButton'
import StatusPanel from './components/StatusPanel'
import LogViewer from './components/LogViewer'
import ProgressTracker from './components/ProgressTracker'

function App() {
  const [selectedCoin, setSelectedCoin] = useState('BTC')
  const [isRunning, setIsRunning] = useState(false)
  const [logs, setLogs] = useState([])
  const [currentStatus, setCurrentStatus] = useState(null)

  const handleRun = async () => {
    if (isRunning) return

    setIsRunning(true)
    setLogs([])
    setCurrentStatus(null)

    try {
      // Use fetch for POST with SSE streaming
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          coin_name: selectedCoin,
          max_retries: 3
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      const readStream = async () => {
        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() || '' // Keep incomplete line in buffer

            for (const line of lines) {
              if (line.trim() === '' || line.startsWith(':')) continue
              
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6))
                  handleUpdate(data)
                  
                  // Stop if complete or error
                  if (data.type === 'complete' || data.type === 'error') {
                    setIsRunning(false)
                    return
                  }
                } catch (e) {
                  console.error('Failed to parse SSE data:', e)
                }
              }
            }
          }
        } catch (error) {
          console.error('Stream error:', error)
          handleUpdate({
            type: 'error',
            data: { message: `Stream connection error: ${error.message}` }
          })
        } finally {
          setIsRunning(false)
        }
      }

      readStream()
    } catch (error) {
      console.error('Request error:', error)
      handleUpdate({
        type: 'error',
        data: { message: `Failed to start: ${error.message}` }
      })
      setIsRunning(false)
    }
  }

  const handleUpdate = (update) => {
    const logEntry = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
      type: update.type,
      data: update.data
    }

    setLogs(prev => [...prev, logEntry])
    setCurrentStatus(update)

    if (update.type === 'complete' || update.type === 'error') {
      setIsRunning(false)
      if (eventSource) {
        eventSource.close()
        setEventSource(null)
      }
    }
  }


  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-10 text-center">
          <div className="inline-block mb-4">
            <span className="px-4 py-2 bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-full text-sm font-semibold text-blue-300 animate-pulse">
              🤖 AI POWERED
            </span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Market Pulse
          </h1>
          <p className="text-2xl md:text-3xl font-semibold mb-3 bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">
            AI Learn while Trading
          </p>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Real-time cryptocurrency analysis with adaptive learning. Watch the AI make smarter decisions with every trade.
          </p>
        </header>

        {/* Progress Tracker */}
        {isRunning && logs.length > 0 && (
          <ProgressTracker currentStage={null} logs={logs} isRunning={isRunning} />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Controls */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50 hover:border-gray-600 transition-all">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <span className="text-2xl">⚙️</span>
                <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Configuration</span>
              </h2>
              
              <CoinSelector
                selectedCoin={selectedCoin}
                onCoinChange={setSelectedCoin}
                disabled={isRunning}
              />

              <div className="mt-6">
                <RunButton
                  onClick={handleRun}
                  disabled={isRunning}
                  coin={selectedCoin}
                />
              </div>
            </div>

            {/* Status Panel */}
            {currentStatus && (
              <StatusPanel status={currentStatus} />
            )}
          </div>

          {/* Right Column - Logs */}
          <div className="lg:col-span-2">
            <LogViewer logs={logs} isRunning={isRunning} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

