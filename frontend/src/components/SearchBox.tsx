import { motion } from 'framer-motion';
import { Search, ArrowRight, Loader2, Atom, Brain, Code, Eye, MessageSquare, Bot, Shield, Network, Sparkles } from 'lucide-react';
import { useState } from 'react';

const quickTopics = [
  { id: 'quantum', name: 'Quantum', icon: Atom, color: 'from-cyan-400 to-teal-400', query: 'Quantum Computing' },
  { id: 'transformers', name: 'Transformers', icon: Brain, color: 'from-purple-400 to-pink-400', query: 'Transformers' },
  { id: 'llm', name: 'LLMs', icon: MessageSquare, color: 'from-violet-400 to-purple-400', query: 'Large Language Models' },
  { id: 'neural', name: 'Neural Nets', icon: Network, color: 'from-pink-400 to-rose-400', query: 'Neural Networks' },
  { id: 'vision', name: 'Vision', icon: Eye, color: 'from-emerald-400 to-green-400', query: 'Computer Vision' },
  { id: 'rl', name: 'RL', icon: Bot, color: 'from-orange-400 to-amber-400', query: 'Reinforcement Learning' },
  { id: 'nlp', name: 'NLP', icon: MessageSquare, color: 'from-teal-400 to-cyan-400', query: 'Natural Language Processing' },
  { id: 'security', name: 'Security', icon: Shield, color: 'from-red-400 to-orange-400', query: 'Cybersecurity' },
  { id: 'compilers', name: 'Compilers', icon: Code, color: 'from-indigo-400 to-blue-400', query: 'Compilers' },
];

interface SearchBoxProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export function SearchBox({ onSearch, isLoading = false }: SearchBoxProps) {
  const [query, setQuery] = useState('');
  const [focused, setFocused] = useState(false);

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
        <motion.div 
          className={`relative flex items-center rounded-2xl overflow-hidden transition-all duration-300 ${
            focused 
              ? 'glass-card ring-2 ring-primary-500/50 shadow-lg shadow-primary-500/20' 
              : 'glass-card'
          }`}
          animate={focused ? { scale: 1.01 } : { scale: 1 }}
        >
          <div className="pl-5 text-primary-400">
            <Search className="w-5 h-5" />
          </div>
          
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Enter arXiv ID or search topic..."
            className="flex-1 px-4 py-4 bg-transparent text-white placeholder-dark-400 outline-none text-lg"
            disabled={isLoading}
          />
          
          <motion.button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="m-2 px-6 py-3 bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 hover:from-primary-400 hover:via-secondary-400 hover:to-accent-400 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all flex items-center gap-2 font-medium shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </motion.button>
        </motion.div>
      </motion.form>

      {/* Quick Topics */}
      <motion.div
        className="mt-6 flex flex-wrap justify-center gap-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        {quickTopics.map((topic, index) => {
          const Icon = topic.icon;
          return (
            <motion.button
              key={topic.id}
              onClick={() => { setQuery(topic.query); onSearch(topic.query); }}
              className="group px-4 py-2 rounded-xl bg-dark-800/50 border border-dark-700/50 hover:border-primary-500/50 text-dark-300 hover:text-white text-sm flex items-center gap-2 transition-all duration-300 hover:bg-dark-800"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.03 }}
            >
              <div className={`w-6 h-6 rounded-lg bg-gradient-to-br ${topic.color} flex items-center justify-center`}>
                <Icon className="w-3.5 h-3.5 text-white" />
              </div>
              {topic.name}
            </motion.button>
          );
        })}
      </motion.div>

      <motion.p 
        className="mt-4 text-center text-xs text-dark-500"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        💡 Tip: Enter <code className="px-2 py-1 bg-dark-800/80 rounded-lg text-primary-400 font-mono">2301.00234</code> for direct arXiv paper
      </motion.p>
    </div>
  );
}
