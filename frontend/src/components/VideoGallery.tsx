import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Video, Search, Download, Play, Loader2, RefreshCw, 
  FolderOpen, ChevronRight,
  Grid, ArrowLeft, ExternalLink
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
          segments: []
        });
      }
      
      const group = groups.get(key)!;
      if (video.animation_type === 'Full Introduction') {
        group.full_video = video;
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
      <div className="mb-6">
        <button onClick={onBack} className="flex items-center gap-2 text-dark-400 hover:text-white mb-3">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Video className="w-6 h-6 text-primary-400" />
            Video Gallery
            <span className="text-base text-dark-400 font-normal">({videos.length})</span>
          </h2>
          
          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2 glass-hover rounded-lg text-dark-400 hover:text-white"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-5">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-800/50 border border-dark-700 rounded-lg text-white placeholder-dark-500 text-sm"
          />
        </div>
        
        <div className="flex bg-dark-800/50 rounded-lg p-1 border border-dark-700">
          {[
            { id: 'grouped', icon: FolderOpen },
            { id: 'grid', icon: Grid },
          ].map((m) => (
            <button
              key={m.id}
              onClick={() => setViewMode(m.id as ViewMode)}
              className={`p-2 rounded-md transition-all ${viewMode === m.id ? 'bg-primary-600 text-white' : 'text-dark-400 hover:text-white'}`}
            >
              <m.icon className="w-4 h-4" />
            </button>
          ))}
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-center">
          {error}
          <button onClick={fetchData} className="block mx-auto mt-2 text-sm underline">Retry</button>
        </div>
      )}

      {/* Empty */}
      {!loading && !error && videos.length === 0 && (
        <div className="text-center py-16">
          <FolderOpen className="w-12 h-12 text-dark-600 mx-auto mb-3" />
          <p className="text-dark-400">No videos yet</p>
        </div>
      )}

      {/* Grouped View */}
      {!loading && !error && viewMode === 'grouped' && groupedVideos.length > 0 && (
        <div className="space-y-3">
          {groupedVideos.map((group) => (
            <div key={group.paper_arxiv_id} className="glass-card rounded-xl overflow-hidden">
              <button
                onClick={() => toggleGroup(group.paper_arxiv_id)}
                className="w-full p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
              >
                <div className="flex items-center gap-3 text-left">
                  <motion.div animate={{ rotate: expandedGroups.has(group.paper_arxiv_id) ? 90 : 0 }}>
                    <ChevronRight className="w-4 h-4 text-dark-400" />
                  </motion.div>
                  <div>
                    <h3 className="font-medium text-white text-sm">{group.paper_title}</h3>
                    <p className="text-xs text-dark-500">{group.segments.length + (group.full_video ? 1 : 0)} videos</p>
                  </div>
                </div>
                {group.full_video && (
                  <span className="text-xs px-2 py-1 bg-primary-500/20 text-primary-300 rounded">Full</span>
                )}
              </button>

              <AnimatePresence>
                {expandedGroups.has(group.paper_arxiv_id) && (
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: 'auto' }}
                    exit={{ height: 0 }}
                    className="overflow-hidden border-t border-white/5"
                  >
                    <div className="p-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                      {group.full_video && (
                        <VideoCard
                          video={group.full_video}
                          onPlay={() => setSelectedVideo(group.full_video!)}
                          formatSize={formatSize}
                          featured
                        />
                      )}
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
            </div>
          ))}
        </div>
      )}

      {/* Grid View */}
      {!loading && !error && viewMode === 'grid' && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
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
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedVideo(null)}
          >
            <motion.div
              className="glass-card rounded-xl overflow-hidden max-w-4xl w-full"
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-3 border-b border-white/10 flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-white">{selectedVideo.animation_type}</h3>
                  <p className="text-xs text-dark-400">{selectedVideo.paper_title}</p>
                </div>
                <button onClick={() => setSelectedVideo(null)} className="p-1 text-dark-400 hover:text-white">✕</button>
              </div>
              <VideoPlayer video={selectedVideo} title={selectedVideo.animation_type} showDetails={false} />
              <div className="p-3 border-t border-white/10 flex items-center justify-between">
                <a
                  href={`https://arxiv.org/abs/${selectedVideo.paper_arxiv_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-dark-400 hover:text-primary-400 flex items-center gap-1"
                >
                  <ExternalLink className="w-3 h-3" /> arXiv
                </a>
                <a
                  href={selectedVideo.download_url}
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-500 rounded-lg text-sm flex items-center gap-2"
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

// Minimal Video Card
function VideoCard({ video, onPlay, formatSize, featured, showTitle }: {
  video: GalleryVideo;
  onPlay: () => void;
  formatSize: (n: number) => string;
  featured?: boolean;
  showTitle?: boolean;
}) {
  const [loaded, setLoaded] = useState(false);

  return (
    <motion.div
      className={`relative rounded-lg overflow-hidden cursor-pointer group ${featured ? 'border border-primary-500/30' : 'border border-dark-700/50'}`}
      onClick={onPlay}
      whileHover={{ scale: 1.02 }}
    >
      <div className="aspect-video bg-dark-900 relative">
        {!loaded && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Loader2 className="w-5 h-5 text-dark-600 animate-spin" />
          </div>
        )}
        <video
          src={video.video_url}
          className={`w-full h-full object-cover transition-opacity ${loaded ? 'opacity-100' : 'opacity-0'}`}
          muted
          preload="metadata"
          onLoadedData={() => setLoaded(true)}
          onMouseEnter={(e) => (e.target as HTMLVideoElement).play().catch(() => {})}
          onMouseLeave={(e) => { const v = e.target as HTMLVideoElement; v.pause(); v.currentTime = 0; }}
        />
        
        {/* Play overlay */}
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center">
            <Play className="w-5 h-5 text-white ml-0.5" />
          </div>
        </div>

        {/* Badges */}
        {featured && (
          <span className="absolute top-1.5 left-1.5 text-[10px] px-1.5 py-0.5 bg-primary-600 text-white rounded">Full</span>
        )}
        {video.segment_number && (
          <span className="absolute top-1.5 right-1.5 text-[10px] px-1.5 py-0.5 bg-dark-900/80 text-white rounded">#{video.segment_number}</span>
        )}
      </div>
      
      <div className="p-2 bg-dark-800/50">
        <p className="text-xs text-white truncate">{video.animation_type}</p>
        {showTitle && <p className="text-[10px] text-dark-500 truncate">{video.paper_title}</p>}
        <p className="text-[10px] text-dark-500">{formatSize(video.file_size)}</p>
      </div>
    </motion.div>
  );
}
