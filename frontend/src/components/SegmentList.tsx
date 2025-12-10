import { motion } from 'framer-motion';
import { Tag } from 'lucide-react';
import type { Segment } from '../services/api';

interface SegmentListProps {
  segments: Segment[];
}

const categoryColors: Record<string, string> = {
  background: 'from-blue-500 to-cyan-500',
  problem_statement: 'from-red-500 to-orange-500',
  motivation: 'from-yellow-500 to-amber-500',
  approach: 'from-green-500 to-emerald-500',
  contributions: 'from-purple-500 to-violet-500',
  outline: 'from-pink-500 to-rose-500',
  general: 'from-gray-500 to-slate-500',
};

export function SegmentList({ segments }: SegmentListProps) {
  return (
    <motion.div
      className="glass rounded-xl p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <h3 className="text-lg font-semibold text-white mb-4">Content Segments</h3>
      
      <div className="space-y-3">
        {segments.map((segment, index) => (
          <motion.div
            key={index}
            className="p-4 bg-dark-800/50 rounded-lg hover:bg-dark-800 transition-colors"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-dark-400">#{index + 1}</span>
                  <h4 className="font-medium text-white truncate">{segment.topic}</h4>
                </div>
                
                <div className="mt-2 flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full bg-gradient-to-r ${categoryColors[segment.topic_category] || categoryColors.general} text-white`}>
                    {segment.topic_category.replace('_', ' ')}
                  </span>
                </div>
                
                {segment.key_concepts && segment.key_concepts.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {segment.key_concepts.slice(0, 4).map((concept, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-dark-700 rounded-md text-dark-300"
                      >
                        <Tag className="w-3 h-3" />
                        {concept}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
