import { motion } from 'framer-motion';
import { Tag, Hash, Layers, BookOpen, Target, Lightbulb, Compass, ListTree, MoreHorizontal } from 'lucide-react';
import type { Segment } from '../services/api';

interface SegmentListProps {
  segments: Segment[];
}

const categoryConfig: Record<string, { gradient: string; icon: React.ElementType; label: string }> = {
  background: { 
    gradient: 'from-blue-500 to-cyan-500', 
    icon: BookOpen,
    label: 'Background'
  },
  problem_statement: { 
    gradient: 'from-red-500 to-orange-500', 
    icon: Target,
    label: 'Problem'
  },
  motivation: { 
    gradient: 'from-amber-500 to-yellow-500', 
    icon: Lightbulb,
    label: 'Motivation'
  },
  approach: { 
    gradient: 'from-green-500 to-emerald-500', 
    icon: Compass,
    label: 'Approach'
  },
  contributions: { 
    gradient: 'from-purple-500 to-violet-500', 
    icon: Layers,
    label: 'Contributions'
  },
  outline: { 
    gradient: 'from-pink-500 to-rose-500', 
    icon: ListTree,
    label: 'Outline'
  },
  general: { 
    gradient: 'from-slate-500 to-gray-500', 
    icon: MoreHorizontal,
    label: 'General'
  },
};

export function SegmentList({ segments }: SegmentListProps) {
  return (
    <motion.div
      className="rounded-2xl bg-gradient-to-br from-slate-900/90 to-slate-950/90 border border-slate-700/50 p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500/20 to-teal-500/20 border border-cyan-500/30">
          <Layers className="w-5 h-5 text-cyan-400" />
        </div>
        <h3 className="text-xl font-semibold bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent">
          Content Segments
        </h3>
        <span className="ml-auto text-sm text-slate-500 bg-slate-800/50 px-3 py-1 rounded-full">
          {segments.length} segments
        </span>
      </div>
      
      <div className="space-y-3">
        {segments.map((segment, index) => {
          const config = categoryConfig[segment.topic_category] || categoryConfig.general;
          const IconComponent = config.icon;
          
          return (
            <motion.div
              key={index}
              className="relative group rounded-xl overflow-hidden"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              {/* Hover glow */}
              <div className={`absolute -inset-0.5 bg-gradient-to-r ${config.gradient} rounded-xl blur opacity-0 group-hover:opacity-20 transition-opacity`} />
              
              <div className="relative p-4 bg-slate-800/50 hover:bg-slate-800/80 border border-slate-700/50 group-hover:border-slate-600/50 rounded-xl transition-all">
                <div className="flex items-start gap-4">
                  {/* Segment number */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br ${config.gradient} bg-opacity-20 flex items-center justify-center shadow-lg`}>
                    <Hash className="w-4 h-4 text-white/90" />
                    <span className="text-sm font-bold text-white">{index + 1}</span>
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    {/* Topic title */}
                    <h4 className="font-medium text-white group-hover:text-cyan-300 transition-colors">
                      {segment.topic}
                    </h4>
                    
                    {/* Category badge */}
                    <div className="mt-2 flex items-center gap-2">
                      <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-gradient-to-r ${config.gradient} text-white font-medium shadow-sm`}>
                        <IconComponent className="w-3 h-3" />
                        {config.label}
                      </span>
                    </div>
                    
                    {/* Key concepts */}
                    {segment.key_concepts && segment.key_concepts.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {segment.key_concepts.slice(0, 4).map((concept, i) => (
                          <motion.span
                            key={i}
                            className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 bg-slate-700/50 hover:bg-cyan-500/20 border border-slate-600/50 hover:border-cyan-500/30 rounded-lg text-slate-300 hover:text-cyan-300 transition-all cursor-default"
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.05 + i * 0.02 }}
                          >
                            <Tag className="w-3 h-3" />
                            {concept}
                          </motion.span>
                        ))}
                        {segment.key_concepts.length > 4 && (
                          <span className="text-xs text-slate-500 px-2 py-1">
                            +{segment.key_concepts.length - 4} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
