import { motion } from 'framer-motion';
import { Search, ArrowRight, Loader2, Atom, Brain, Code, Eye, MessageSquare, Bot, Shield, Network } from 'lucide-react';
import { useState } from 'react';

const quickTopics = [
  { id: 'quantum', name: 'Quantum', icon: Atom, color: 'text-cyan-400', query: 'Quantum Computing' },
  { id: 'transformers', name: 'Transformers', icon: Brain, color: 'text-purple-400', query: 'Transformers' },
  { id: 'llm', name: 'LLMs', icon: MessageSquare, color: 'text-violet-400', query: 'Large Language Models' },
  { id: 'neural', name: 'Neural Nets', icon: Network, color: 'text-pink-400', query: 'Neural Networks' },
  { id: 'vision', name: 'Vision', icon: Eye, color: 'text-emerald-400', query: 'Computer Vision' },
  { id: 'rl', name: 'RL', icon: Bot, color: 'text-orange-400', query: 'Reinforcement Learning' },
  { id: 'nlp', name: 'NLP', icon: MessageSquare, color: 'text-teal-400', query: 'Natural Language Processing' },
  { id: 'security', name: 'Security', icon: Shield, color: 'text-red-400', query: 'Cybersecurity' },
  { id: 'compilers', name: 'Compilers', icon: Code, color: 'text-indigo-400', query: 'Compilers' },
];

interface SearchBoxProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export function SearchBox({ onSearch, isLoading = false }: SearchBoxProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <motion.form
        onSubmit={handleSubmit}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="relative flex items-center glass-card rounded-xl overflow-hidden">
          <div className="pl-4 text-primary-400">
            <Search className="w-5 h-5" />
          </div>
          
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter arXiv ID or search topic..."
            className="flex-1 px-4 py-4 bg-transparent text-white placeholder-dark-400 outline-none"
            disabled={isLoading}
          />
          
          <motion.button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="m-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-500 hover:to-purple-500 disabled:opacity-50 rounded-xl transition-all flex items-center gap-2 font-medium"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <span>Generate</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </motion.button>
        </div>
      </motion.form>

      {/* Quick Topics */}
      <motion.div
        className="mt-5 flex flex-wrap justify-center gap-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        {quickTopics.map((topic) => {
          const Icon = topic.icon;
          return (
            <motion.button
              key={topic.id}
              onClick={() => { setQuery(topic.query); onSearch(topic.query); }}
              className="px-3 py-1.5 rounded-full bg-dark-800/50 border border-dark-700 hover:border-dark-500 text-dark-300 hover:text-white text-sm flex items-center gap-1.5 transition-all"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Icon className={`w-3.5 h-3.5 ${topic.color}`} />
              {topic.name}
            </motion.button>
          );
        })}
      </motion.div>

      <p className="mt-3 text-center text-xs text-dark-500">
        Tip: <code className="px-1.5 py-0.5 bg-dark-800/50 rounded text-dark-400">2301.00234</code> for direct arXiv
      </p>
    </div>
  );
}
