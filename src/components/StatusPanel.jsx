function StatusPanel({ status }) {
  const getStatusColor = (type) => {
    switch (type) {
      case 'success':
        return 'bg-gradient-to-r from-green-500/30 to-emerald-500/20 border-green-500 shadow-lg shadow-green-500/20'
      case 'failure':
        return 'bg-gradient-to-r from-red-500/30 to-red-600/20 border-red-500 shadow-lg shadow-red-500/20'
      case 'error':
        return 'bg-gradient-to-r from-red-500/30 to-red-600/20 border-red-500 shadow-lg shadow-red-500/20'
      case 'attempt_start':
        return 'bg-gradient-to-r from-blue-500/30 to-cyan-500/20 border-blue-500 shadow-lg shadow-blue-500/20'
      case 'decision':
        return status.data.decision === 'BUY'
          ? 'bg-gradient-to-r from-green-500/30 to-emerald-500/20 border-green-500 shadow-lg shadow-green-500/20'
          : 'bg-gradient-to-r from-red-500/30 to-red-600/20 border-red-500 shadow-lg shadow-red-500/20'
      case 'evaluation':
      case 'evaluation_result':
        return status.data.success
          ? 'bg-gradient-to-r from-green-500/30 to-emerald-500/20 border-green-500 shadow-lg shadow-green-500/20'
          : 'bg-gradient-to-r from-yellow-500/30 to-orange-500/20 border-yellow-500 shadow-lg shadow-yellow-500/20'
      case 'prompt_updated':
        return 'bg-gradient-to-r from-pink-500/30 to-purple-500/20 border-pink-500 shadow-lg shadow-pink-500/20 animate-pulse'
      case 'countdown':
        return 'bg-gradient-to-r from-orange-500/30 to-orange-600/20 border-orange-500 shadow-lg shadow-orange-500/20'
      case 'price_update':
        return 'bg-gradient-to-r from-emerald-500/30 to-teal-500/20 border-emerald-500 shadow-lg shadow-emerald-500/20'
      case 'complete':
        return status.data.success
          ? 'bg-gradient-to-r from-indigo-500/30 to-purple-500/20 border-indigo-500 shadow-lg shadow-indigo-500/20'
          : 'bg-gradient-to-r from-gray-500/30 to-gray-600/20 border-gray-500 shadow-lg shadow-gray-500/20'
      default:
        return 'bg-gray-700/50 border-gray-600'
    }
  }

  const renderContent = () => {
    switch (status.type) {
      case 'attempt_start':
        return (
          <div className="flex items-center gap-3">
            <div className="text-3xl animate-spin">🔄</div>
            <div>
              <div className="text-xl font-bold mb-1">
                Attempt {status.data.attempt} / {status.data.max_retries}
              </div>
              <div className="text-sm text-gray-300">AI is analyzing the market...</div>
            </div>
          </div>
        )

      case 'decision':
        return (
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="text-3xl">{status.data.decision === 'BUY' ? '📈' : '📉'}</div>
              <div>
                <div className="text-sm text-gray-400 mb-1">AI Decision</div>
                <div className="text-2xl font-bold">
                  <span className={`${status.data.decision === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                    {status.data.decision}
                  </span>
                </div>
              </div>
            </div>
            {status.data.reason && (
              <div className="text-sm text-gray-300 mt-3 p-3 bg-gray-900/50 rounded-lg border border-gray-700">
                {status.data.reason}
              </div>
            )}
          </div>
        )

      case 'evaluation':
      case 'evaluation_result':
        return (
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="text-3xl">{status.data.success ? '✅' : '❌'}</div>
              <div>
                <div className="text-xl font-bold">
                  {status.data.success ? 'Success!' : 'Failure'}
                </div>
                <div className={`text-2xl font-bold font-mono ${status.data.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {status.data.profit >= 0 ? '+' : ''}${status.data.profit?.toFixed(2)}
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-700">
                <div className="text-xs text-gray-400 mb-1">Price Before</div>
                <div className="text-lg font-mono font-bold">${status.data.price_before?.toFixed(2)}</div>
              </div>
              <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-700">
                <div className="text-xs text-gray-400 mb-1">Price After</div>
                <div className="text-lg font-mono font-bold">${status.data.price_after?.toFixed(2)}</div>
              </div>
            </div>
          </div>
        )

      case 'countdown':
        return (
          <div className="text-center">
            <div className="text-5xl font-bold mb-2 animate-pulse text-orange-400">
              {status.data.seconds_remaining}s
            </div>
            <div className="text-sm text-gray-400 flex items-center justify-center gap-2">
              <span className="animate-spin">⏱️</span>
              <span>Waiting for price update...</span>
            </div>
          </div>
        )

      case 'price_update':
        return (
          <div>
            <div className="text-sm text-gray-400 mb-2">{status.data.label}</div>
            <div className="text-3xl font-bold font-mono text-emerald-400 animate-pulse">
              ${status.data.price?.toFixed(2)}
            </div>
          </div>
        )

      case 'prompt_updated':
        return (
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="text-3xl animate-bounce">🧠</div>
              <div>
                <div className="text-xl font-bold text-pink-400">AI Learning</div>
                <div className="text-sm text-gray-300">Prompt updated based on results</div>
              </div>
            </div>
            {status.data.reason && (
              <div className="text-sm text-gray-300 mt-3 p-3 bg-pink-900/20 rounded-lg border border-pink-500/30">
                {status.data.reason}
              </div>
            )}
          </div>
        )

      case 'complete':
        return (
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="text-3xl">{status.data.success ? '🎉' : '😔'}</div>
              <div>
                <div className={`text-xl font-bold ${status.data.success ? 'text-green-400' : 'text-red-400'}`}>
                  {status.data.success ? 'Completed Successfully!' : 'Completed with Failures'}
                </div>
                <div className="text-sm text-gray-300">
                  Total Attempts: {status.data.attempts}
                </div>
              </div>
            </div>
          </div>
        )

      default:
        return (
          <div>
            <div className="text-sm text-gray-300">
              {status.data.message || JSON.stringify(status.data)}
            </div>
          </div>
        )
    }
  }

  if (!status) return null

  return (
    <div className={`bg-gray-800/80 backdrop-blur-sm rounded-xl p-5 border-2 ${getStatusColor(status.type)} transition-all transform hover:scale-[1.02]`}>
      <div className="text-xs uppercase tracking-wider text-gray-300 mb-3 font-bold flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-current animate-pulse"></span>
        {status.type.replace('_', ' ')}
      </div>
      {renderContent()}
    </div>
  )
}

export default StatusPanel

