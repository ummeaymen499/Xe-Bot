import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

interface Step {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

interface ProcessingStepsProps {
  steps: Step[];
}

export function ProcessingSteps({ steps }: ProcessingStepsProps) {
  return (
    <motion.div
      className="glass rounded-xl p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <h3 className="text-lg font-semibold text-white mb-6">Processing Pipeline</h3>
      
      <div className="space-y-4">
        {steps.map((step, index) => (
          <motion.div
            key={step.id}
            className="flex items-start gap-4"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            {/* Step indicator */}
            <div className="relative">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                step.status === 'completed' ? 'bg-green-500/20' :
                step.status === 'active' ? 'bg-primary-500/20' :
                step.status === 'error' ? 'bg-red-500/20' :
                'bg-dark-700'
              }`}>
                {step.status === 'completed' ? (
                  <CheckCircle2 className="w-5 h-5 text-green-400" />
                ) : step.status === 'active' ? (
                  <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
                ) : step.status === 'error' ? (
                  <span className="text-red-400">✕</span>
                ) : (
                  <Circle className="w-5 h-5 text-dark-500" />
                )}
              </div>
              
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className={`absolute top-10 left-1/2 w-0.5 h-8 -translate-x-1/2 ${
                  step.status === 'completed' ? 'bg-green-500/50' : 'bg-dark-700'
                }`} />
              )}
            </div>
            
            {/* Step content */}
            <div className="flex-1 pb-8">
              <h4 className={`font-medium ${
                step.status === 'completed' ? 'text-green-400' :
                step.status === 'active' ? 'text-primary-400' :
                step.status === 'error' ? 'text-red-400' :
                'text-dark-400'
              }`}>
                {step.title}
              </h4>
              <p className="text-sm text-dark-400 mt-1">{step.description}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
