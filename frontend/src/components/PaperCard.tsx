import { motion } from 'framer-motion';
import { FileText, Users, Calendar, ArrowRight, Loader2 } from 'lucide-react';
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
      className="glass rounded-xl p-6 hover:bg-white/10 transition-all cursor-pointer group"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      onClick={() => !isProcessing && onSelect(paper.arxiv_id)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-purple-500/20 flex items-center justify-center flex-shrink-0">
          <FileText className="w-6 h-6 text-primary-400" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4">
            <h3 className="font-semibold text-white group-hover:text-primary-300 transition-colors line-clamp-2">
              {paper.title}
            </h3>
            <span className="text-xs text-dark-400 bg-dark-800 px-2 py-1 rounded-md flex-shrink-0">
              {paper.arxiv_id}
            </span>
          </div>
          
          <div className="mt-2 flex items-center gap-4 text-sm text-dark-400">
            <div className="flex items-center gap-1.5">
              <Users className="w-4 h-4" />
              <span className="truncate max-w-[200px]">
                {paper.authors.slice(0, 2).join(', ')}
                {paper.authors.length > 2 && ` +${paper.authors.length - 2}`}
              </span>
            </div>
            {paper.published && (
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4" />
                <span>{new Date(paper.published).toLocaleDateString()}</span>
              </div>
            )}
          </div>
          
          <p className="mt-3 text-sm text-dark-300 line-clamp-2">
            {paper.summary}
          </p>
          
          <div className="mt-4 flex items-center justify-end">
            <button
              disabled={isProcessing}
              className="flex items-center gap-2 text-sm text-primary-400 hover:text-primary-300 transition-colors disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <span>Generate Animation</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
