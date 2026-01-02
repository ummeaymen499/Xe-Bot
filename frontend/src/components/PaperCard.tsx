import { motion } from 'framer-motion';
import { FileText, Users, Calendar, ArrowRight, Loader2, Sparkles, ExternalLink } from 'lucide-react';
import type { ArxivSearchResult } from '../services/api';

interface PaperCardProps {
  paper: ArxivSearchResult;
  onSelect: (arxivId: string) => void;
  isProcessing?: boolean;
  index?: number;
}

export function PaperCard({ paper, onSelect, isProcessing = false, index = 0 }: PaperCardProps) {
  return (
    <motion.div
      className="relative group rounded-2xl overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      whileHover={{ scale: 1.01, y: -4 }}
      whileTap={{ scale: 0.99 }}
    >
      {/* Glow effect on hover */}
      <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500/30 via-teal-500/30 to-purple-500/30 rounded-2xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      
      <div 
        className="relative bg-gradient-to-br from-slate-900/95 to-slate-950/95 border border-slate-700/50 group-hover:border-cyan-500/30 p-6 rounded-2xl transition-all cursor-pointer"
        onClick={() => !isProcessing && onSelect(paper.arxiv_id)}
      >
        <div className="flex items-start gap-5">
          {/* Icon */}
          <motion.div 
            className="w-14 h-14 rounded-xl bg-gradient-to-br from-cyan-500/20 to-teal-500/20 border border-cyan-500/30 flex items-center justify-center flex-shrink-0"
            whileHover={{ rotate: [0, -10, 10, 0] }}
            transition={{ duration: 0.5 }}
          >
            <FileText className="w-7 h-7 text-cyan-400" />
          </motion.div>
          
          <div className="flex-1 min-w-0">
            {/* Title and arXiv ID */}
            <div className="flex items-start justify-between gap-4">
              <h3 className="font-semibold text-white group-hover:text-cyan-300 transition-colors line-clamp-2 text-lg leading-tight">
                {paper.title}
              </h3>
              <a 
                href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-xs text-slate-400 bg-slate-800/80 hover:bg-cyan-500/20 hover:text-cyan-300 px-3 py-1.5 rounded-lg flex-shrink-0 flex items-center gap-1.5 transition-all border border-slate-700/50 hover:border-cyan-500/30"
              >
                {paper.arxiv_id}
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            
            {/* Metadata */}
            <div className="mt-3 flex items-center gap-5 text-sm text-slate-400">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-500/70" />
                <span className="truncate max-w-[200px]">
                  {paper.authors.slice(0, 2).join(', ')}
                  {paper.authors.length > 2 && (
                    <span className="text-slate-500"> +{paper.authors.length - 2} more</span>
                  )}
                </span>
              </div>
              {paper.published && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-teal-500/70" />
                  <span>{new Date(paper.published).toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric' 
                  })}</span>
                </div>
              )}
            </div>
            
            {/* Summary */}
            <p className="mt-4 text-sm text-slate-400 line-clamp-2 leading-relaxed">
              {paper.summary}
            </p>
            
            {/* Action button */}
            <div className="mt-5 flex items-center justify-end">
              <motion.button
                disabled={isProcessing}
                className={`flex items-center gap-2.5 px-5 py-2.5 rounded-xl font-medium text-sm transition-all disabled:opacity-50 ${
                  isProcessing 
                    ? 'bg-slate-800 text-slate-400'
                    : 'bg-gradient-to-r from-cyan-500/10 to-teal-500/10 text-cyan-400 hover:from-cyan-500 hover:to-teal-500 hover:text-white border border-cyan-500/30 hover:border-transparent shadow-lg shadow-cyan-500/0 hover:shadow-cyan-500/25'
                }`}
                whileHover={!isProcessing ? { scale: 1.05 } : {}}
                whileTap={!isProcessing ? { scale: 0.95 } : {}}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Generate Animation</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
