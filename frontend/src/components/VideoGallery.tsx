import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, Download, Play, Loader2, RefreshCw, 
  FolderOpen, ChevronRight,
  Grid, ArrowLeft, ExternalLink, Film, Sparkles
} from 'lucide-react';
import { VideoPlayer } from './VideoPlayer';
import { getVideos, getPapers, type VideoInfo } from '../services/api';

interface GalleryVideo extends VideoInfo {
  paper_title?: string;
  paper_arxiv_id?: string;
  animation_type?: string;
  segment_number?: number;
}

interface PaperGroup {
  paper_title: string;
  paper_arxiv_id: string;
  full_video?: GalleryVideo;
  full_videos: GalleryVideo[];  // All full introduction videos
  segments: GalleryVideo[];
}

interface VideoGalleryProps {
  onBack: () => void;
}

type ViewMode = 'grouped' | 'grid';

export function VideoGallery({ onBack }: VideoGalleryProps) {
  const [videos, setVideos] = useState<GalleryVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedVideo, setSelectedVideo] = useState<GalleryVideo | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<ViewMode>('grouped');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [videosData] = await Promise.all([
        getVideos(),
        getPapers()
      ]);
      
      const enrichedVideos: GalleryVideo[] = videosData.map(v => {
        const isFullIntro = v.file_path?.includes('full_introduction');
        const segmentMatch = v.file_path?.match(/segment_(\d+)/);
        const segmentNum = segmentMatch ? parseInt(segmentMatch[1]) : undefined;
        
        return {
          ...v,
          animation_type: isFullIntro ? 'Full Introduction' : 
                         segmentNum ? `Segment ${segmentNum}` : 'Animation',
          segment_number: segmentNum
        };
      });
      
      setVideos(enrichedVideos);
      
      // Auto-expand first group
      const firstPaper = enrichedVideos[0]?.paper_arxiv_id;
      if (firstPaper) setExpandedGroups(new Set([firstPaper]));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const groupedVideos = useMemo(() => {
    const groups: Map<string, PaperGroup> = new Map();
    
    const filtered = videos.filter(v => 
      !searchQuery || 
      v.paper_title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.animation_type?.toLowerCase().includes(searchQuery.toLowerCase())
    );
    
    filtered.forEach(video => {
      const key = video.paper_arxiv_id || 'unknown';
      
      if (!groups.has(key)) {
        groups.set(key, {
          paper_title: video.paper_title || 'Unknown Paper',
          paper_arxiv_id: key,
          full_video: undefined,
          full_videos: [],
          segments: []
        });
      }
      
      const group = groups.get(key)!;
      if (video.animation_type === 'Full Introduction') {
        // Check if this is the main combined video (has "Full" or "Introduction" in name)
        const videoName = video.video_id || '';
        const isMainFullVideo = videoName.toLowerCase().includes('fullintroduction') || 
                                videoName.toLowerCase().includes('full_introduction');
        if (isMainFullVideo && !group.full_video) {
          group.full_video = video;
        }
        group.full_videos.push(video);
      } else {
        group.segments.push(video);
      }
    });
    
    groups.forEach(g => g.segments.sort((a, b) => (a.segment_number || 0) - (b.segment_number || 0)));
    return Array.from(groups.values());
  }, [videos, searchQuery]);

  const toggleGroup = (id: string) => {
    const newExpanded = new Set(expandedGroups);
    newExpanded.has(id) ? newExpanded.delete(id) : newExpanded.add(id);
    setExpandedGroups(newExpanded);
  };

  const formatSize = (bytes: number) => {
    if (!bytes) return '';
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      {/* Header */}
      <div className="mb-8">
        <button 
          onClick={onBack} 
          className="flex items-center gap-2 text-slate-400 hover:text-cyan-400 mb-4 transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" /> 
          Back to Search
        </button>
        
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500/20 to-teal-500/20 border border-cyan-500/30">
              <Film className="w-6 h-6 text-cyan-400" />
            </div>
            <span className="bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent">
              Video Gallery
            </span>
            <span className="text-base text-slate-500 font-normal ml-2">
              ({videos.length} videos)
            </span>
          </h2>
          
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-400 hover:text-cyan-400 hover:border-cyan-500/30 transition-all"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <div className="flex-1 relative group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
          <input
            type="text"
            placeholder="Search videos..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 text-sm focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all outline-none"
          />
        </div>
        
        <div className="flex bg-slate-800/50 rounded-xl p-1.5 border border-slate-700/50">
          {[
            { id: 'grouped', icon: FolderOpen, label: 'Grouped' },
            { id: 'grid', icon: Grid, label: 'Grid' },
          ].map((m) => (
            <button
              key={m.id}
              onClick={() => setViewMode(m.id as ViewMode)}
              className={`p-2.5 rounded-lg transition-all ${
                viewMode === m.id 
                  ? 'bg-gradient-to-r from-cyan-500 to-teal-500 text-white shadow-lg shadow-cyan-500/25' 
                  : 'text-slate-400 hover:text-white'
              }`}
              title={m.label}
            >
              <m.icon className="w-4 h-4" />
            </button>
          ))}
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
            <Sparkles className="w-6 h-6 text-cyan-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
          </div>
          <p className="text-slate-400 mt-4">Loading videos...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-6 bg-red-500/10 border border-red-500/30 rounded-2xl text-center">
          <p className="text-red-400 mb-3">{error}</p>
          <button 
            onClick={fetchData} 
            className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Empty */}
      {!loading && !error && videos.length === 0 && (
        <div className="text-center py-20">
          <div className="w-20 h-20 rounded-full bg-slate-800/50 flex items-center justify-center mx-auto mb-4">
            <FolderOpen className="w-10 h-10 text-slate-600" />
          </div>
          <p className="text-slate-400 text-lg">No videos yet</p>
          <p className="text-slate-500 text-sm mt-2">Generate some animations to see them here</p>
        </div>
      )}

      {/* Grouped View */}
      {!loading && !error && viewMode === 'grouped' && groupedVideos.length > 0 && (
        <div className="space-y-4">
          {groupedVideos.map((group) => (
            <motion.div 
              key={group.paper_arxiv_id} 
              className="rounded-2xl overflow-hidden bg-gradient-to-br from-slate-900/80 to-slate-950/80 border border-slate-700/50"
              layout
            >
              <button
                onClick={() => toggleGroup(group.paper_arxiv_id)}
                className="w-full p-5 flex items-center justify-between hover:bg-white/5 transition-colors"
              >
                <div className="flex items-center gap-4 text-left">
                  <motion.div 
                    animate={{ rotate: expandedGroups.has(group.paper_arxiv_id) ? 90 : 0 }}
                    className="p-2 rounded-lg bg-slate-800/50"
                  >
                    <ChevronRight className="w-4 h-4 text-cyan-400" />
                  </motion.div>
                  <div>
                    <h3 className="font-semibold text-white">{group.paper_title}</h3>
                    <p className="text-sm text-slate-500 mt-1">
                      {group.full_videos.length + group.segments.length} video{group.full_videos.length + group.segments.length > 1 ? 's' : ''}
                    </p>
                  </div>
                </div>
                {group.full_video && (
                  <span className="text-xs px-3 py-1.5 bg-gradient-to-r from-cyan-500/20 to-teal-500/20 text-cyan-300 rounded-full border border-cyan-500/30">
                    ✨ Full Video
                  </span>
                )}
              </button>

              <AnimatePresence>
                {expandedGroups.has(group.paper_arxiv_id) && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden border-t border-slate-700/50"
                  >
                    <div className="p-5 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                      {/* Show main full video first if exists */}
                      {group.full_video && (
                        <VideoCard
                          video={group.full_video}
                          onPlay={() => setSelectedVideo(group.full_video!)}
                          formatSize={formatSize}
                          featured
                        />
                      )}
                      {/* Show other full introduction videos (not the main one) */}
                      {group.full_videos
                        .filter(v => v.video_id !== group.full_video?.video_id)
                        .map((video) => (
                          <VideoCard
                            key={video.video_id}
                            video={video}
                            onPlay={() => setSelectedVideo(video)}
                            formatSize={formatSize}
                          />
                        ))}
                      {/* Show segment videos */}
                      {group.segments.map((video) => (
                        <VideoCard
                          key={video.video_id}
                          video={video}
                          onPlay={() => setSelectedVideo(video)}
                          formatSize={formatSize}
                        />
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      )}

      {/* Grid View */}
      {!loading && !error && viewMode === 'grid' && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {videos.filter(v => !searchQuery || v.paper_title?.toLowerCase().includes(searchQuery.toLowerCase())).map((video) => (
            <VideoCard
              key={video.video_id}
              video={video}
              onPlay={() => setSelectedVideo(video)}
              formatSize={formatSize}
              showTitle
            />
          ))}
        </div>
      )}

      {/* Modal */}
      <AnimatePresence>
        {selectedVideo && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-sm p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedVideo(null)}
          >
            <motion.div
              className="bg-gradient-to-br from-slate-900 to-slate-950 rounded-2xl overflow-hidden max-w-4xl w-full border border-cyan-500/20 shadow-2xl shadow-cyan-500/10"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-white flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-cyan-400" />
                    {selectedVideo.animation_type}
                  </h3>
                  <p className="text-sm text-slate-400 mt-1">{selectedVideo.paper_title}</p>
                </div>
                <button 
                  onClick={() => setSelectedVideo(null)} 
                  className="p-2 text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-lg transition-colors"
                >
                  ✕
                </button>
              </div>
              <VideoPlayer video={selectedVideo} title={selectedVideo.animation_type} showDetails={false} />
              <div className="p-4 border-t border-slate-700/50 flex items-center justify-between">
                <a
                  href={`https://arxiv.org/abs/${selectedVideo.paper_arxiv_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-slate-400 hover:text-cyan-400 flex items-center gap-2 transition-colors"
                >
                  <ExternalLink className="w-4 h-4" /> View on arXiv
                </a>
                <a
                  href={selectedVideo.download_url}
                  className="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 rounded-xl text-white font-medium flex items-center gap-2 shadow-lg shadow-cyan-500/25 transition-all"
                >
                  <Download className="w-4 h-4" /> Download
                </a>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// Enhanced Video Card
function VideoCard({ video, onPlay, formatSize, featured, showTitle }: {
  video: GalleryVideo;
  onPlay: () => void;
  formatSize: (n: number) => string;
  featured?: boolean;
  showTitle?: boolean;
}) {
  const [loaded, setLoaded] = useState(false);
  const [isHovering, setIsHovering] = useState(false);

  return (
    <motion.div
      className={`relative rounded-xl overflow-hidden cursor-pointer group ${
        featured 
          ? 'ring-2 ring-cyan-500/50 shadow-lg shadow-cyan-500/20' 
          : 'border border-slate-700/50 hover:border-cyan-500/30'
      }`}
      onClick={onPlay}
      whileHover={{ scale: 1.03, y: -4 }}
      transition={{ type: 'spring', stiffness: 300 }}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      <div className="aspect-video bg-slate-900 relative">
        {!loaded && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-900">
            <Loader2 className="w-6 h-6 text-cyan-500/50 animate-spin" />
          </div>
        )}
        <video
          src={video.video_url}
          className={`w-full h-full object-cover transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
          muted
          preload="metadata"
          onLoadedData={() => setLoaded(true)}
          onMouseEnter={(e) => (e.target as HTMLVideoElement).play().catch(() => {})}
          onMouseLeave={(e) => { const v = e.target as HTMLVideoElement; v.pause(); v.currentTime = 0; }}
        />
        
        {/* Play overlay */}
        <motion.div 
          className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovering ? 1 : 0 }}
        >
          <motion.div 
            className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-teal-500 flex items-center justify-center shadow-lg shadow-cyan-500/40"
            whileHover={{ scale: 1.1 }}
          >
            <Play className="w-5 h-5 text-white ml-0.5" fill="white" />
          </motion.div>
        </motion.div>

        {/* Badges */}
        {featured && (
          <span className="absolute top-2 left-2 text-xs px-2.5 py-1 bg-gradient-to-r from-cyan-500 to-teal-500 text-white rounded-full font-medium shadow-lg">
            ✨ Full
          </span>
        )}
        {video.segment_number && (
          <span className="absolute top-2 right-2 text-xs px-2 py-1 bg-slate-900/90 text-cyan-300 rounded-lg font-mono border border-cyan-500/30">
            #{video.segment_number}
          </span>
        )}
      </div>
      
      <div className="p-3 bg-gradient-to-b from-slate-800/80 to-slate-900/80">
        <p className="text-sm text-white font-medium truncate">{video.animation_type}</p>
        {showTitle && <p className="text-xs text-slate-500 truncate mt-1">{video.paper_title}</p>}
        <p className="text-xs text-slate-600 mt-1">{formatSize(video.file_size)}</p>
      </div>
    </motion.div>
  );
}
