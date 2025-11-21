import { useState, useEffect } from 'react'
import CoinSelector from './components/CoinSelector'
import RunButton from './components/RunButton'
import StatusPanel from './components/StatusPanel'
import LogViewer from './components/LogViewer'

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
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Crypto Agent Runner
          </h1>
          <p className="text-gray-400">
            AI-powered cryptocurrency trading decision maker with real-time feedback loop
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Controls */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-gray-800 rounded-lg p-6 shadow-xl border border-gray-700">
              <h2 className="text-xl font-semibold mb-4">Configuration</h2>
              
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

