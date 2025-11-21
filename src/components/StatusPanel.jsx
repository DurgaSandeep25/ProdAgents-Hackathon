function StatusPanel({ status }) {
  const getStatusColor = (type) => {
    switch (type) {
      case 'success':
        return 'bg-green-500/20 border-green-500'
      case 'failure':
        return 'bg-red-500/20 border-red-500'
      case 'error':
        return 'bg-red-500/20 border-red-500'
      case 'attempt_start':
        return 'bg-blue-500/20 border-blue-500'
      case 'decision':
        return 'bg-purple-500/20 border-purple-500'
      case 'evaluation':
        return status.data.success
          ? 'bg-green-500/20 border-green-500'
          : 'bg-yellow-500/20 border-yellow-500'
      default:
        return 'bg-gray-700 border-gray-600'
    }
  }

  const renderContent = () => {
    switch (status.type) {
      case 'attempt_start':
        return (
          <div>
            <div className="text-lg font-semibold mb-2">
              Attempt {status.data.attempt} / {status.data.max_retries}
            </div>
          </div>
        )

      case 'decision':
        return (
          <div>
            <div className="text-lg font-semibold mb-2">
              Decision: <span className={`${status.data.decision === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                {status.data.decision}
              </span>
            </div>
            {status.data.reason && (
              <div className="text-sm text-gray-300 mt-2">
                {status.data.reason}
              </div>
            )}
          </div>
        )

      case 'evaluation':
        return (
          <div>
            <div className="text-lg font-semibold mb-2">
              {status.data.success ? '✓ Success' : '✗ Failure'}
            </div>
            <div className="space-y-1 text-sm">
              <div>Price Before: <span className="font-mono">${status.data.price_before?.toFixed(2)}</span></div>
              <div>Price After: <span className="font-mono">${status.data.price_after?.toFixed(2)}</span></div>
              <div className={`font-semibold ${status.data.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                Profit: <span className="font-mono">${status.data.profit?.toFixed(2)}</span>
              </div>
            </div>
          </div>
        )

      case 'countdown':
        return (
          <div className="text-center">
            <div className="text-2xl font-bold">
              {status.data.seconds_remaining}s
            </div>
            <div className="text-sm text-gray-400">Waiting for price update...</div>
          </div>
        )

      case 'price_update':
        return (
          <div>
            <div className="text-sm text-gray-400">{status.data.label}</div>
            <div className="text-xl font-bold font-mono">
              ${status.data.price?.toFixed(2)}
            </div>
          </div>
        )

      case 'complete':
        return (
          <div>
            <div className={`text-lg font-semibold mb-2 ${status.data.success ? 'text-green-400' : 'text-red-400'}`}>
              {status.data.success ? '✓ Completed Successfully' : '✗ Completed with Failures'}
            </div>
            <div className="text-sm text-gray-300">
              Total Attempts: {status.data.attempts}
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
    <div className={`bg-gray-800 rounded-lg p-4 border-2 ${getStatusColor(status.type)} transition-all`}>
      <div className="text-xs uppercase tracking-wider text-gray-400 mb-2">
        {status.type.replace('_', ' ')}
      </div>
      {renderContent()}
    </div>
  )
}

export default StatusPanel

