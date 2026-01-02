import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  Download, 
  Maximize2, 
  Volume2, 
  VolumeX,
  Share2,
  Copy,
  Check,
  SkipBack,
  SkipForward,
  Clock,
  HardDrive
} from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import type { VideoInfo } from '../services/api';

interface VideoPlayerProps {
  video: VideoInfo;
  title?: string;
  index?: number;
  showDetails?: boolean;
}

export function VideoPlayer({ video, title, index = 0, showDetails = true }: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [loaded, setLoaded] = useState(false);
  const [showShareMenu, setShowShareMenu] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const [buffered, setBuffered] = useState(0);
  
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;

    const onTime = () => {
      setProgress((v.currentTime / v.duration) * 100 || 0);
      setCurrentTime(v.currentTime);
    };
    const onMeta = () => { setDuration(v.duration); setLoaded(true); };
    const onEnded = () => setIsPlaying(false);
    const onProgress = () => {
      if (v.buffered.length > 0) {
        setBuffered((v.buffered.end(v.buffered.length - 1) / v.duration) * 100);
      }
    };

    v.addEventListener('timeupdate', onTime);
    v.addEventListener('loadedmetadata', onMeta);
    v.addEventListener('ended', onEnded);
    v.addEventListener('progress', onProgress);

    return () => {
      v.removeEventListener('timeupdate', onTime);
      v.removeEventListener('loadedmetadata', onMeta);
      v.removeEventListener('ended', onEnded);
      v.removeEventListener('progress', onProgress);
    };
  }, []);

  const togglePlay = () => {
    if (videoRef.current) {
      isPlaying ? videoRef.current.pause() : videoRef.current.play();
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!videoRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    videoRef.current.currentTime = percent * duration;
  };

  const skipForward = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = Math.min(videoRef.current.currentTime + 10, duration);
    }
  };

  const skipBackward = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = Math.max(videoRef.current.currentTime - 10, 0);
    }
  };

  const handleFullscreen = () => {
    videoRef.current?.requestFullscreen?.();
  };

  const copyVideoLink = async () => {
    try {
      await navigator.clipboard.writeText(video.video_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const shareVideo = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: title || 'XE-Bot Animation',
          text: 'Check out this research paper animation!',
          url: video.video_url
        });
      } catch (err) {
        console.error('Share failed:', err);
      }
    } else {
      setShowShareMenu(!showShareMenu);
    }
  };

  const formatTime = (s: number) => {
    if (!s || isNaN(s)) return '0:00';
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  return (
    <motion.div
      className="relative rounded-2xl overflow-hidden bg-gradient-to-br from-slate-900/90 to-slate-950/90 border border-cyan-500/20 shadow-xl shadow-cyan-500/5"
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.1, type: 'spring', stiffness: 100 }}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {/* Glow effect */}
      <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500/20 via-teal-500/20 to-purple-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
      
      {/* Video Container */}
      <div className="relative aspect-video bg-slate-950 group">
        <video
          ref={videoRef}
          src={video.video_url}
          className="w-full h-full object-contain"
          muted={isMuted}
          preload="metadata"
          playsInline
          onClick={togglePlay}
        />

        {/* Loading shimmer */}
        {!loaded && (
          <div className="absolute inset-0 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 animate-pulse flex items-center justify-center">
            <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
          </div>
        )}

        {/* Play overlay */}
        <AnimatePresence>
          {!isPlaying && loaded && (
            <motion.div
              className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={togglePlay}
            >
              <motion.div
                className="w-20 h-20 rounded-full bg-gradient-to-r from-cyan-500 to-teal-500 flex items-center justify-center shadow-lg shadow-cyan-500/30"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <Play className="w-8 h-8 text-white ml-1" fill="white" />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Controls */}
        <motion.div 
          className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/60 to-transparent p-4"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: isHovering || !isPlaying ? 1 : 0, y: isHovering || !isPlaying ? 0 : 10 }}
          transition={{ duration: 0.2 }}
        >
          {/* Progress bar */}
          <div
            className="relative h-1.5 bg-slate-700/50 rounded-full mb-3 cursor-pointer group/progress"
            onClick={handleSeek}
          >
            {/* Buffered progress */}
            <div
              className="absolute h-full bg-slate-600/50 rounded-full transition-all"
              style={{ width: `${buffered}%` }}
            />
            {/* Played progress */}
            <div
              className="absolute h-full bg-gradient-to-r from-cyan-500 to-teal-400 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
            {/* Hover indicator */}
            <div 
              className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg shadow-cyan-500/50 opacity-0 group-hover/progress:opacity-100 transition-opacity"
              style={{ left: `calc(${progress}% - 8px)` }}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1">
              {/* Skip backward */}
              <button 
                onClick={skipBackward} 
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="Skip back 10s"
              >
                <SkipBack className="w-4 h-4 text-slate-300" />
              </button>
              
              {/* Play/Pause */}
              <button 
                onClick={togglePlay} 
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                {isPlaying ? (
                  <Pause className="w-5 h-5 text-white" />
                ) : (
                  <Play className="w-5 h-5 text-white" />
                )}
              </button>
              
              {/* Skip forward */}
              <button 
                onClick={skipForward} 
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="Skip forward 10s"
              >
                <SkipForward className="w-4 h-4 text-slate-300" />
              </button>
              
              {/* Volume */}
              <button 
                onClick={toggleMute} 
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                {isMuted ? (
                  <VolumeX className="w-4 h-4 text-slate-300" />
                ) : (
                  <Volume2 className="w-4 h-4 text-cyan-400" />
                )}
              </button>
              
              {/* Time */}
              <span className="text-xs text-slate-400 ml-2 font-mono">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>
            </div>

            <div className="flex items-center gap-1">
              {/* Share */}
              <div className="relative">
                <button 
                  onClick={shareVideo} 
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  title="Share"
                >
                  <Share2 className="w-4 h-4 text-slate-300" />
                </button>
                
                {/* Share dropdown */}
                <AnimatePresence>
                  {showShareMenu && (
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                      className="absolute bottom-full right-0 mb-2 p-2 bg-slate-800 rounded-lg border border-cyan-500/20 shadow-xl min-w-40"
                    >
                      <button
                        onClick={copyVideoLink}
                        className="flex items-center gap-2 w-full px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 rounded-lg transition-colors"
                      >
                        {copied ? (
                          <>
                            <Check className="w-4 h-4 text-green-400" />
                            <span className="text-green-400">Copied!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4" />
                            <span>Copy link</span>
                          </>
                        )}
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
              
              {/* Fullscreen */}
              <button 
                onClick={handleFullscreen} 
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                title="Fullscreen"
              >
                <Maximize2 className="w-4 h-4 text-slate-300" />
              </button>
              
              {/* Download */}
              <a
                href={video.download_url || video.video_url}
                download
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  // If no download URL, prevent default and try opening video URL
                  if (!video.download_url) {
                    e.preventDefault();
                    window.open(video.video_url, '_blank');
                  }
                }}
                title="Download"
              >
                <Download className="w-4 h-4 text-cyan-400" />
              </a>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Info */}
      {showDetails && (
        <div className="p-4 bg-gradient-to-b from-slate-900/50 to-slate-950/50">
          <h4 className="font-semibold text-white text-sm truncate mb-2">
            {title || 'Animation'}
          </h4>
          <div className="flex items-center gap-4 text-xs text-slate-500">
            {duration > 0 && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatTime(duration)}
              </span>
            )}
            {video.file_size && (
              <span className="flex items-center gap-1">
                <HardDrive className="w-3 h-3" />
                {(video.file_size / (1024 * 1024)).toFixed(1)} MB
              </span>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
}
