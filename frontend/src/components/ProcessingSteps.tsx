import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Loader2, Sparkles, FileSearch, Scissors, Film, AlertCircle } from 'lucide-react';

interface Step {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

interface ProcessingStepsProps {
  steps: Step[];
}

const stepIcons: { [key: string]: React.ComponentType<{ className?: string }> } = {
  fetch: FileSearch,
  extract: Sparkles,
  segment: Scissors,
  animate: Film,
};

const stepLabels: { [key: string]: { active: string; completed: string } } = {
  fetch: { active: 'Fetching Paper', completed: 'Paper Fetched' },
  extract: { active: 'Extracting Content', completed: 'Content Extracted' },
  segment: { active: 'Segmenting Topics', completed: 'Topics Segmented' },
  animate: { active: 'Generating Animations', completed: 'Animations Complete' },
};

export function ProcessingSteps({ steps }: ProcessingStepsProps) {
  const completedCount = steps.filter(s => s.status === 'completed').length;
  const progress = (completedCount / steps.length) * 100;
  const activeStep = steps.find(s => s.status === 'active');
  const hasError = steps.some(s => s.status === 'error');

  return (
    <motion.div
      className="glass-card rounded-2xl p-6 overflow-hidden relative"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Progress bar at top */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-dark-800">
        <motion.div 
          className={`h-full ${hasError ? 'bg-red-500' : 'bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500'}`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>

      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary-400" />
          Processing Pipeline
        </h3>
        <span className={`text-sm ${hasError ? 'text-red-400' : 'text-dark-400'}`}>
          {hasError ? 'Error occurred' : `${completedCount}/${steps.length} complete`}
        </span>
      </div>

      {/* Current status banner */}
      {activeStep && (
        <motion.div
          className="mb-4 p-3 rounded-lg bg-primary-500/10 border border-primary-500/30"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 text-primary-400 animate-spin" />
            <span className="text-sm text-primary-300 font-medium">
              {stepLabels[activeStep.id]?.active || activeStep.title}
            </span>
          </div>
          <p className="text-xs text-dark-400 mt-1 ml-6">{activeStep.description}</p>
        </motion.div>
      )}
      
      <div className="space-y-4">
        {steps.map((step, index) => {
          const StepIcon = stepIcons[step.id] || Circle;
          
          return (
            <motion.div
              key={step.id}
              className={`flex items-start gap-4 p-3 rounded-xl transition-all duration-300 ${
                step.status === 'active' ? 'bg-primary-500/10 border border-primary-500/30' :
                step.status === 'completed' ? 'bg-emerald-500/5' :
                ''
              }`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              {/* Step indicator */}
              <div className="relative">
                <motion.div 
                  className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    step.status === 'completed' ? 'bg-gradient-to-br from-emerald-500/30 to-green-500/20' :
                    step.status === 'active' ? 'bg-gradient-to-br from-primary-500/30 to-secondary-500/20' :
                    step.status === 'error' ? 'bg-gradient-to-br from-red-500/30 to-red-600/20' :
                    'bg-dark-800'
                  }`}
                  animate={step.status === 'active' ? { 
                    boxShadow: ['0 0 0 0 rgba(6,182,212,0.4)', '0 0 0 10px rgba(6,182,212,0)', '0 0 0 0 rgba(6,182,212,0)']
                  } : {}}
                  transition={{ duration: 1.5, repeat: step.status === 'active' ? Infinity : 0 }}
                >
                  {step.status === 'completed' ? (
                    <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                  ) : step.status === 'active' ? (
                    <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />
                  ) : step.status === 'error' ? (
                    <AlertCircle className="w-6 h-6 text-red-400" />
                  ) : (
                    <StepIcon className="w-5 h-5 text-dark-500" />
                  )}
                </motion.div>
                
                {/* Connector line */}
                {index < steps.length - 1 && (
                  <div className={`absolute top-12 left-1/2 w-0.5 h-6 -translate-x-1/2 transition-colors duration-300 ${
                    step.status === 'completed' ? 'bg-gradient-to-b from-emerald-500/50 to-transparent' : 'bg-dark-700'
                  }`} />
                )}
              </div>
              
              {/* Step content */}
              <div className="flex-1 pt-1">
                <h4 className={`font-medium transition-colors duration-300 ${
                  step.status === 'completed' ? 'text-emerald-400' :
                  step.status === 'active' ? 'text-primary-300' :
                  step.status === 'error' ? 'text-red-400' :
                  'text-dark-400'
                }`}>
                  {step.title}
                </h4>
                <p className="text-sm text-dark-500 mt-0.5">{step.description}</p>
              </div>

              {/* Status badge */}
              {step.status === 'active' && (
                <span className="badge badge-primary animate-pulse">
                  In Progress
                </span>
              )}
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
