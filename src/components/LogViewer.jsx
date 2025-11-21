import { useEffect, useRef } from 'react'

function LogViewer({ logs, isRunning }) {
  const logEndRef = useRef(null)

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const getLogIcon = (type) => {
    switch (type) {
      case 'success':
        return '✓'
      case 'failure':
        return '✗'
      case 'error':
        return '⚠'
      case 'attempt_start':
        return '🔄'
      case 'decision':
        return '💡'
      case 'evaluation':
        return '📊'
      case 'prompt_updated':
        return '🔄'
      case 'countdown':
        return '⏱'
      case 'price_update':
        return '💰'
      case 'complete':
        return '🏁'
      default:
        return 'ℹ'
    }
  }

  const getLogColor = (type) => {
    switch (type) {
      case 'success':
        return 'border-green-500 bg-green-500/10'
      case 'failure':
        return 'border-red-500 bg-red-500/10'
      case 'error':
        return 'border-red-500 bg-red-500/10'
      case 'attempt_start':
        return 'border-blue-500 bg-blue-500/10'
      case 'decision':
        return 'border-purple-500 bg-purple-500/10'
      case 'evaluation':
        return 'border-yellow-500 bg-yellow-500/10'
      case 'prompt_updated':
        return 'border-cyan-500 bg-cyan-500/10'
      case 'countdown':
        return 'border-orange-500 bg-orange-500/10'
      case 'price_update':
        return 'border-emerald-500 bg-emerald-500/10'
      case 'complete':
        return 'border-indigo-500 bg-indigo-500/10'
      default:
        return 'border-gray-600 bg-gray-700/50'
    }
  }

  const formatLogData = (log) => {
    switch (log.type) {
      case 'status':
        return log.data.message
      case 'attempt_start':
        return `Starting attempt ${log.data.attempt}/${log.data.max_retries}`
      case 'decision':
        return `Decision: ${log.data.decision}${log.data.reason ? ` - ${log.data.reason}` : ''}`
      case 'evaluation':
        return `Evaluation: ${log.data.success ? 'SUCCESS' : 'FAILURE'} - Profit: $${log.data.profit?.toFixed(2)}`
      case 'price_update':
        return `${log.data.label}: $${log.data.price?.toFixed(2)}`
      case 'countdown':
        return `Waiting... ${log.data.seconds_remaining}s remaining`
      case 'prompt_updated':
        return `Prompt updated: ${log.data.reason}`
      case 'success':
        return `SUCCESS: ${log.data.message}`
      case 'failure':
        return `FAILURE: ${log.data.message}`
      case 'complete':
        return `Complete: ${log.data.success ? 'SUCCESS' : 'FAILURE'} after ${log.data.attempts} attempts`
      case 'error':
        return `ERROR: ${log.data.message}`
      default:
        return JSON.stringify(log.data, null, 2)
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl border border-gray-700 h-[calc(100vh-200px)] flex flex-col">
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        <h2 className="text-xl font-semibold">Execution Log</h2>
        {isRunning && (
          <div className="flex items-center text-sm text-gray-400">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
            Running...
          </div>
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {logs.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>No logs yet. Click "Run Agent" to start.</p>
          </div>
        ) : (
          logs.map((log) => (
            <div
              key={log.id}
              className={`p-3 rounded-lg border-l-4 ${getLogColor(log.type)} transition-all`}
            >
              <div className="flex items-start gap-3">
                <div className="text-xl flex-shrink-0 mt-0.5">
                  {getLogIcon(log.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                      {log.type.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="text-sm text-gray-200 break-words">
                    {formatLogData(log)}
                  </div>
                  {log.type === 'evaluation' && log.data.price_before && (
                    <div className="mt-2 pt-2 border-t border-gray-600 space-y-1 text-xs">
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <span className="text-gray-400">Price Before:</span>
                          <span className="ml-2 font-mono text-white">${log.data.price_before.toFixed(2)}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Price After:</span>
                          <span className="ml-2 font-mono text-white">${log.data.price_after.toFixed(2)}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-400">Profit:</span>
                        <span className={`ml-2 font-mono font-semibold ${log.data.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          ${log.data.profit.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  )
}

export default LogViewer

