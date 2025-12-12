import { motion } from 'framer-motion';
import { Zap, Video, Home, Sparkles } from 'lucide-react';

interface HeaderProps {
  onNavigate?: (page: 'home' | 'gallery' | 'about') => void;
  currentPage?: string;
}

export function Header({ onNavigate, currentPage = 'home' }: HeaderProps) {
  return (
    <header className="py-4 px-4 md:px-6 relative z-10">
      <div className="max-w-6xl mx-auto">
        <motion.div 
          className="glass-card px-4 py-3 flex items-center justify-between"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {/* Logo */}
          <motion.div 
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => onNavigate?.('home')}
            whileHover={{ scale: 1.02 }}
          >
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-400 via-secondary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/30">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <motion.div
                className="absolute -top-1 -right-1"
                animate={{ rotate: [0, 15, -15, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Sparkles className="w-4 h-4 text-amber-400" />
              </motion.div>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold gradient-text-hero">Xe-Bot</span>
              <span className="text-[10px] text-dark-400 -mt-1 hidden sm:block">Research Animation AI</span>
            </div>
          </motion.div>

          {/* Nav */}
          <div className="flex items-center gap-2">
            <motion.button
              onClick={() => onNavigate?.('home')}
              className={`px-4 py-2 rounded-xl text-sm flex items-center gap-2 transition-all duration-300 ${
                currentPage === 'home' 
                  ? 'bg-gradient-to-r from-primary-500/20 to-secondary-500/20 text-primary-300 border border-primary-500/30' 
                  : 'text-dark-400 hover:text-white hover:bg-white/5'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Home className="w-4 h-4" />
              <span className="hidden sm:inline">Home</span>
            </motion.button>
            <motion.button
              onClick={() => onNavigate?.('gallery')}
              className={`px-4 py-2 rounded-xl text-sm flex items-center gap-2 transition-all duration-300 ${
                currentPage === 'gallery' 
                  ? 'bg-gradient-to-r from-primary-500/20 to-secondary-500/20 text-primary-300 border border-primary-500/30' 
                  : 'text-dark-400 hover:text-white hover:bg-white/5'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Video className="w-4 h-4" />
              <span className="hidden sm:inline">Gallery</span>
            </motion.button>
          </div>
        </motion.div>
      </div>
    </header>
  );
}
