import { useEffect, useRef, useState } from 'react'

function LogViewer({ logs, isRunning }) {
  const logEndRef = useRef(null)
  const [expandedLogs, setExpandedLogs] = useState(new Set())

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const toggleExpand = (logId) => {
    setExpandedLogs(prev => {
      const newSet = new Set(prev)
      if (newSet.has(logId)) {
        newSet.delete(logId)
      } else {
        newSet.add(logId)
      }
      return newSet
    })
  }

  const getLogIcon = (type) => {
    switch (type) {
      case 'success':
        return '✅'
      case 'failure':
        return '❌'
      case 'error':
        return '⚠️'
      case 'attempt_start':
        return '🔄'
      case 'decision':
        return '💡'
      case 'evaluation':
      case 'evaluation_result':
        return '📊'
      case 'prompt_updated':
        return '🧠'
      case 'countdown':
        return '⏱️'
      case 'price_update':
        return '💰'
      case 'complete':
        return '🏁'
      default:
        return 'ℹ️'
    }
  }

  const getLogColor = (type, data) => {
    switch (type) {
      case 'success':
        return 'border-green-500 bg-gradient-to-r from-green-500/20 to-green-600/10 shadow-lg shadow-green-500/20'
      case 'failure':
        return 'border-red-500 bg-gradient-to-r from-red-500/20 to-red-600/10 shadow-lg shadow-red-500/20'
      case 'error':
        return 'border-red-500 bg-gradient-to-r from-red-500/20 to-red-600/10 shadow-lg shadow-red-500/20'
      case 'attempt_start':
        return 'border-blue-500 bg-gradient-to-r from-blue-500/20 to-blue-600/10 shadow-lg shadow-blue-500/20'
      case 'decision':
        return data?.decision === 'BUY' 
          ? 'border-green-500 bg-gradient-to-r from-green-500/20 to-emerald-600/10 shadow-lg shadow-green-500/20'
          : 'border-red-500 bg-gradient-to-r from-red-500/20 to-red-600/10 shadow-lg shadow-red-500/20'
      case 'evaluation':
      case 'evaluation_result':
        return data?.success
          ? 'border-green-500 bg-gradient-to-r from-green-500/20 to-green-600/10 shadow-lg shadow-green-500/20'
          : 'border-yellow-500 bg-gradient-to-r from-yellow-500/20 to-orange-600/10 shadow-lg shadow-yellow-500/20'
      case 'prompt_updated':
        return 'border-pink-500 bg-gradient-to-r from-pink-500/20 to-purple-600/10 shadow-lg shadow-pink-500/20 animate-pulse'
      case 'countdown':
        return 'border-orange-500 bg-gradient-to-r from-orange-500/20 to-orange-600/10 shadow-lg shadow-orange-500/20'
      case 'price_update':
        return 'border-emerald-500 bg-gradient-to-r from-emerald-500/20 to-teal-600/10 shadow-lg shadow-emerald-500/20'
      case 'complete':
        return data?.success
          ? 'border-indigo-500 bg-gradient-to-r from-indigo-500/20 to-purple-600/10 shadow-lg shadow-indigo-500/20'
          : 'border-gray-500 bg-gradient-to-r from-gray-500/20 to-gray-600/10 shadow-lg shadow-gray-500/20'
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
      case 'evaluation_result':
        return `Evaluation: ${log.data.success ? '✅ SUCCESS' : '❌ FAILURE'} - Profit: $${log.data.profit?.toFixed(2)}`
      case 'price_update':
        return `${log.data.label}: $${log.data.price?.toFixed(2)}`
      case 'countdown':
        return `Waiting... ${log.data.seconds_remaining}s remaining`
      case 'prompt_updated':
        return `🧠 AI Learning: ${log.data.reason}`
      case 'success':
        return `✅ SUCCESS: ${log.data.message}`
      case 'failure':
        return `❌ FAILURE: ${log.data.message}`
      case 'complete':
        return `Complete: ${log.data.success ? '✅ SUCCESS' : '❌ FAILURE'} after ${log.data.attempts} attempts`
      case 'error':
        return `⚠️ ERROR: ${log.data.message}`
      default:
        return JSON.stringify(log.data, null, 2)
    }
  }

  const renderLogContent = (log) => {
    const isExpanded = expandedLogs.has(log.id)
    const canExpand = log.type === 'decision' || log.type === 'evaluation' || log.type === 'evaluation_result' || log.type === 'prompt_updated'
    const isLastLog = log.id === logs[logs.length - 1]?.id

    return (
      <div
        key={log.id}
        className={`p-4 rounded-xl border-l-4 ${getLogColor(log.type, log.data)} transition-all transform hover:scale-[1.01] ${
          isRunning && isLastLog ? 'ring-2 ring-blue-500/50' : ''
        }`}
      >
        <div className="flex items-start gap-4">
          <div className="text-2xl flex-shrink-0 mt-0.5">
            {getLogIcon(log.type)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-xs font-bold text-gray-300 uppercase tracking-wider px-2 py-1 bg-gray-700/50 rounded">
                {log.type.replace('_', ' ')}
              </span>
              <span className="text-xs text-gray-400 font-mono">
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div className="text-base text-gray-100 break-words font-medium">
              {formatLogData(log)}
            </div>
            
            {/* Decision Details */}
            {log.type === 'decision' && log.data.reason && (
              <div className={`mt-3 pt-3 border-t border-gray-600/50 transition-all ${isExpanded ? 'block' : 'hidden'}`}>
                <div className="text-sm text-gray-300 leading-relaxed">
                  <div className="font-semibold text-gray-400 mb-1">Analysis:</div>
                  <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-700">
                    {log.data.reason}
                  </div>
                </div>
              </div>
            )}

            {/* Evaluation Details */}
            {(log.type === 'evaluation' || log.type === 'evaluation_result') && log.data.price_before && (
              <div className={`mt-3 pt-3 border-t border-gray-600/50 transition-all ${isExpanded ? 'block' : 'hidden'}`}>
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-700">
                    <div className="text-xs text-gray-400 mb-1">Price Before</div>
                    <div className="text-lg font-mono font-bold text-white">${log.data.price_before.toFixed(2)}</div>
                  </div>
                  <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-700">
                    <div className="text-xs text-gray-400 mb-1">Price After</div>
                    <div className="text-lg font-mono font-bold text-white">${log.data.price_after.toFixed(2)}</div>
                  </div>
                  <div className={`p-3 rounded-lg border-2 ${
                    log.data.profit >= 0 
                      ? 'bg-green-900/30 border-green-500' 
                      : 'bg-red-900/30 border-red-500'
                  }`}>
                    <div className="text-xs text-gray-300 mb-1">Profit/Loss</div>
                    <div className={`text-xl font-mono font-bold ${
                      log.data.profit >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {log.data.profit >= 0 ? '+' : ''}${log.data.profit.toFixed(2)}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Prompt Update Details */}
            {log.type === 'prompt_updated' && log.data.reason && (
              <div className={`mt-3 pt-3 border-t border-gray-600/50 transition-all ${isExpanded ? 'block' : 'hidden'}`}>
                <div className="text-sm text-gray-300">
                  <div className="font-semibold text-pink-400 mb-2 flex items-center gap-2">
                    <span>🧠</span>
                    <span>AI Learning Update:</span>
                  </div>
                  <div className="bg-gradient-to-r from-pink-900/30 to-purple-900/30 p-3 rounded-lg border border-pink-500/30">
                    {log.data.reason}
                  </div>
                </div>
              </div>
            )}

            {/* Expand/Collapse Button */}
            {canExpand && (
              <button
                onClick={() => toggleExpand(log.id)}
                className="mt-2 text-xs text-gray-400 hover:text-gray-300 transition-colors flex items-center gap-1"
              >
                {isExpanded ? '▼ Hide Details' : '▶ Show Details'}
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-xl border border-gray-700/50 h-[calc(100vh-200px)] flex flex-col">
      <div className="p-5 border-b border-gray-700/50 flex items-center justify-between bg-gradient-to-r from-gray-800/50 to-gray-900/50">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <span className="text-2xl">📋</span>
          <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Execution Log
          </span>
        </h2>
        {isRunning && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/20 border border-green-500/30 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-400 font-medium">Running...</span>
          </div>
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto p-5 space-y-3 custom-scrollbar">
        {logs.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            <div className="text-6xl mb-4">🤖</div>
            <p className="text-lg">No logs yet.</p>
            <p className="text-sm mt-2">Click "Start AI Analysis" to begin.</p>
          </div>
        ) : (
          logs.map(renderLogContent)
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  )
}

export default LogViewer

