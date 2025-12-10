import { motion } from 'framer-motion';
import { Play, Pause, Download, Maximize2, Volume2, VolumeX } from 'lucide-react';
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
  const [duration, setDuration] = useState(0);
  const [loaded, setLoaded] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;

    const onTime = () => setProgress((v.currentTime / v.duration) * 100 || 0);
    const onMeta = () => { setDuration(v.duration); setLoaded(true); };
    const onEnded = () => setIsPlaying(false);

    v.addEventListener('timeupdate', onTime);
    v.addEventListener('loadedmetadata', onMeta);
    v.addEventListener('ended', onEnded);

    return () => {
      v.removeEventListener('timeupdate', onTime);
      v.removeEventListener('loadedmetadata', onMeta);
      v.removeEventListener('ended', onEnded);
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

  const handleFullscreen = () => {
    videoRef.current?.requestFullscreen?.();
  };

  const formatTime = (s: number) => {
    if (!s || isNaN(s)) return '0:00';
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  return (
    <motion.div
      className="glass-card rounded-xl overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      {/* Video Container */}
      <div className="relative aspect-video bg-dark-900 group">
        <video
          ref={videoRef}
          src={video.video_url}
          className="w-full h-full object-contain"
          muted={isMuted}
          preload="metadata"
          playsInline
          onClick={togglePlay}
        />

        {/* Play overlay */}
        {!isPlaying && loaded && (
          <motion.div
            className="absolute inset-0 flex items-center justify-center bg-black/30 cursor-pointer"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={togglePlay}
          >
            <div className="w-14 h-14 rounded-full bg-primary-600/90 flex items-center justify-center">
              <Play className="w-6 h-6 text-white ml-1" />
            </div>
          </motion.div>
        )}

        {/* Controls */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity">
          {/* Progress */}
          <div
            className="h-1 bg-dark-600 rounded-full mb-2 cursor-pointer"
            onClick={handleSeek}
          >
            <div
              className="h-full bg-primary-500 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button onClick={togglePlay} className="p-1.5 hover:bg-white/10 rounded">
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </button>
              <button onClick={toggleMute} className="p-1.5 hover:bg-white/10 rounded">
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>
              <span className="text-xs text-dark-300">{formatTime(duration)}</span>
            </div>

            <div className="flex items-center gap-1">
              <button onClick={handleFullscreen} className="p-1.5 hover:bg-white/10 rounded">
                <Maximize2 className="w-4 h-4" />
              </button>
              <a
                href={video.download_url}
                className="p-1.5 hover:bg-white/10 rounded"
                onClick={(e) => e.stopPropagation()}
              >
                <Download className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Info */}
      {showDetails && (
        <div className="p-3">
          <h4 className="font-medium text-white text-sm truncate">{title || 'Animation'}</h4>
          {video.file_size && (
            <p className="text-xs text-dark-500 mt-1">
              {(video.file_size / (1024 * 1024)).toFixed(1)} MB
            </p>
          )}
        </div>
      )}
    </motion.div>
  );
}
