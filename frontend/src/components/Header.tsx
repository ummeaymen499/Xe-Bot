import { motion } from 'framer-motion';
import { Zap, Video, Home } from 'lucide-react';

interface HeaderProps {
  onNavigate?: (page: 'home' | 'gallery' | 'about') => void;
  currentPage?: string;
}

export function Header({ onNavigate, currentPage = 'home' }: HeaderProps) {
  return (
    <header className="py-4 px-4 md:px-6">
      <div className="max-w-6xl mx-auto">
        <div className="glass-card px-4 py-3 flex items-center justify-between">
          {/* Logo */}
          <motion.div 
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => onNavigate?.('home')}
            whileHover={{ scale: 1.02 }}
          >
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold gradient-text">Xe-Bot</span>
          </motion.div>

          {/* Nav */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => onNavigate?.('home')}
              className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 transition-all ${
                currentPage === 'home' ? 'bg-primary-600/20 text-primary-300' : 'text-dark-400 hover:text-white'
              }`}
            >
              <Home className="w-4 h-4" />
              <span className="hidden sm:inline">Home</span>
            </button>
            <button
              onClick={() => onNavigate?.('gallery')}
              className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1.5 transition-all ${
                currentPage === 'gallery' ? 'bg-primary-600/20 text-primary-300' : 'text-dark-400 hover:text-white'
              }`}
            >
              <Video className="w-4 h-4" />
              <span className="hidden sm:inline">Gallery</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
