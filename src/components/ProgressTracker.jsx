import { useState, useEffect } from 'react'

const STAGES = [
  { id: 'starting', label: 'Starting', icon: '🚀', color: 'blue' },
  { id: 'analyzing', label: 'AI Analyzing', icon: '🤖', color: 'purple' },
  { id: 'decision', label: 'Decision Made', icon: '💡', color: 'yellow' },
  { id: 'evaluating', label: 'Evaluating', icon: '📊', color: 'cyan' },
  { id: 'learning', label: 'AI Learning', icon: '🧠', color: 'pink' },
  { id: 'complete', label: 'Complete', icon: '✅', color: 'green' }
]

function ProgressTracker({ currentStage, logs, isRunning }) {
  const [activeStage, setActiveStage] = useState(null)
  const [completedStages, setCompletedStages] = useState(new Set())

  useEffect(() => {
    // Determine current stage based on logs
    if (!isRunning && logs.length > 0) {
      const lastLog = logs[logs.length - 1]
      if (lastLog.type === 'complete') {
        setActiveStage('complete')
        setCompletedStages(new Set(STAGES.map(s => s.id)))
        return
      }
    }

    if (logs.length === 0) {
      setActiveStage('starting')
      return
    }

    // Check for different stages based on log types
    const hasAttemptStart = logs.some(l => l.type === 'attempt_start')
    const hasDecision = logs.some(l => l.type === 'decision')
    const hasEvaluation = logs.some(l => l.type === 'evaluation' || l.type === 'evaluation_result')
    const hasPromptUpdate = logs.some(l => l.type === 'prompt_updated')

    if (hasEvaluation) {
      setActiveStage('evaluating')
      setCompletedStages(new Set(['starting', 'analyzing', 'decision', 'evaluating']))
    } else if (hasDecision) {
      setActiveStage('decision')
      setCompletedStages(new Set(['starting', 'analyzing', 'decision']))
    } else if (hasAttemptStart) {
      setActiveStage('analyzing')
      setCompletedStages(new Set(['starting', 'analyzing']))
    } else {
      setActiveStage('starting')
      setCompletedStages(new Set(['starting']))
    }

    if (hasPromptUpdate) {
      setActiveStage('learning')
    }
  }, [logs, isRunning])

  const getStageIndex = (stageId) => {
    return STAGES.findIndex(s => s.id === stageId)
  }

  const isStageActive = (stageId) => {
    return activeStage === stageId
  }

  const isStageCompleted = (stageId) => {
    return completedStages.has(stageId)
  }

  const getStageColor = (stage) => {
    if (isStageCompleted(stage.id)) {
      return `bg-${stage.color}-500`
    }
    if (isStageActive(stage.id)) {
      return `bg-${stage.color}-500 animate-pulse`
    }
    return 'bg-gray-600'
  }

  return (
    <div className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50 mb-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <span className="text-xl">📈</span>
        <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          Execution Progress
        </span>
      </h3>
      
      <div className="relative">
        {/* Progress Line */}
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-700">
          <div 
            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-500"
            style={{ 
              width: `${(completedStages.size / STAGES.length) * 100}%` 
            }}
          />
        </div>

        {/* Stages */}
        <div className="relative flex justify-between">
          {STAGES.map((stage, index) => {
            const isActive = isStageActive(stage.id)
            const isCompleted = isStageCompleted(stage.id)
            
            return (
              <div key={stage.id} className="flex flex-col items-center flex-1">
                <div className={`relative z-10 w-10 h-10 rounded-full ${getStageColor(stage)} flex items-center justify-center text-white text-lg shadow-lg transition-all transform ${isActive ? 'scale-110' : ''}`}>
                  {isCompleted ? '✓' : stage.icon}
                </div>
                <div className={`mt-2 text-xs text-center font-medium transition-colors ${
                  isActive ? `text-${stage.color}-400` : isCompleted ? 'text-gray-400' : 'text-gray-600'
                }`}>
                  {stage.label}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default ProgressTracker

