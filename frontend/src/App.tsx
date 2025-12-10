import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Video, FileText, Zap, Library, Brain, CheckCircle2 } from 'lucide-react';
import { Header, SearchBox, PaperCard, VideoPlayer, ProcessingSteps, SegmentList, VideoGallery } from './components';
import { searchByDomain, startAsyncProcess, pollJobUntilComplete, type ArxivSearchResult, type VideoInfo, type Segment, type JobStatus } from './services/api';

type AppState = 'home' | 'results' | 'processing' | 'completed' | 'gallery';

interface ProcessingStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

function App() {
  const [state, setState] = useState<AppState>('home');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<ArxivSearchResult[]>([]);
  const [videos, setVideos] = useState<VideoInfo[]>([]);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [paperTitle, setPaperTitle] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>([
    { id: 'fetch', title: 'Fetching Paper', description: 'Downloading...', status: 'pending' },
    { id: 'extract', title: 'Extracting', description: 'Analyzing...', status: 'pending' },
    { id: 'segment', title: 'Segmenting', description: 'Breaking down...', status: 'pending' },
    { id: 'animate', title: 'Animating', description: 'Creating visuals...', status: 'pending' },
  ]);

  const handleSearch = async (query: string) => {
    setIsSearching(true);
    setError(null);
    
    try {
      const isArxivId = /^\d{4}\.\d{4,5}(v\d+)?$/.test(query);
      
      if (isArxivId) {
        setIsSearching(false);
        handleSelectPaper(query);
      } else {
        const results = await searchByDomain(query);
        setSearchResults(results);
        setState('results');
        setIsSearching(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setIsSearching(false);
    }
  };

  const handleSelectPaper = async (arxivId: string) => {
    setState('processing');
    setError(null);
    setProcessingSteps(steps => steps.map(s => ({ ...s, status: 'pending' as const })));
    
    try {
      const updateStep = (stepId: string, status: 'active' | 'completed' | 'error', description?: string) => {
        setProcessingSteps(steps => steps.map(s => 
          s.id === stepId ? { ...s, status, description: description || s.description } : s
        ));
      };

      // Start async job
      updateStep('fetch', 'active', 'Starting job...');
      const { job_id } = await startAsyncProcess(arxivId);
      updateStep('fetch', 'completed', 'Job started');
      
      // Poll for status updates
      const handleProgress = (status: JobStatus) => {
        const stage = status.stage?.toLowerCase() || '';
        
        if (stage.includes('fetch')) {
          updateStep('fetch', 'active', 'Downloading paper...');
        } else if (stage.includes('extract')) {
          updateStep('fetch', 'completed');
          updateStep('extract', 'active', 'Analyzing content...');
        } else if (stage.includes('segment')) {
          updateStep('extract', 'completed');
          updateStep('segment', 'active', 'Breaking into parts...');
        } else if (stage.includes('animat')) {
          updateStep('segment', 'completed');
          updateStep('animate', 'active', `Rendering... ${status.progress || 0}%`);
        }
      };
      
      updateStep('extract', 'active', 'Processing...');
      
      const finalStatus = await pollJobUntilComplete(job_id, handleProgress, 3000);
      
      // Mark all steps completed
      setProcessingSteps(steps => steps.map(s => ({ ...s, status: 'completed' as const })));
      
      // Job result has videos at top level, not nested in result
      setPaperTitle(finalStatus.paper?.title || 'Research Paper');
      setSegments([]); // Segments not returned in job status
      
      // Convert job videos to VideoInfo format
      const jobVideos = finalStatus.videos || [];
      setVideos(jobVideos.map((v, i) => ({
        video_id: `job_${job_id}_${i}`,
        video_url: v.video_url,
        download_url: v.download_url,
        file_path: '',
        file_size: 0,
        animation_type: v.type || 'segment',
        paper_title: finalStatus.paper?.title
      })));
      
      setState('completed');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Processing failed');
      setProcessingSteps(steps => steps.map(s => 
        s.status === 'active' || s.status === 'pending' ? { ...s, status: 'error' as const } : s
      ));
    }
  };

  const handleReset = () => {
    setState('home');
    setIsSearching(false);
    setSearchResults([]);
    setVideos([]);
    setSegments([]);
    setPaperTitle('');
    setError(null);
  };

  const handleNavigate = (page: 'home' | 'gallery' | 'about') => {
    if (page === 'gallery') setState('gallery');
    else handleReset();
  };

  return (
    <div className="min-h-screen relative">
      {/* Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-dark-950 via-dark-900 to-primary-950" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/10 rounded-full blur-[100px]" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[100px]" />
      </div>

      <Header onNavigate={handleNavigate} currentPage={state === 'gallery' ? 'gallery' : 'home'} />

      <main className="max-w-6xl mx-auto px-4 py-8">
        <AnimatePresence mode="wait">
          {/* Gallery */}
          {state === 'gallery' && <VideoGallery onBack={handleReset} />}

          {/* Home */}
          {state === 'home' && (
            <motion.div
              key="home"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center pt-8"
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-10"
              >
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                  <span className="gradient-text">Research to Animation</span>
                </h1>
                <p className="text-dark-300 max-w-lg mx-auto">
                  Transform academic papers into visual explanations with AI
                </p>
              </motion.div>

              <SearchBox onSearch={handleSearch} isLoading={isSearching} />

              <motion.button
                onClick={() => setState('gallery')}
                className="mt-8 px-5 py-2.5 glass-hover rounded-lg text-dark-400 hover:text-white flex items-center gap-2 mx-auto text-sm"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <Library className="w-4 h-4" />
                Browse Gallery
              </motion.button>

              {/* Features */}
              <motion.div
                className="mt-16 grid md:grid-cols-3 gap-4 max-w-3xl mx-auto"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                {[
                  { icon: FileText, title: 'Extract', desc: 'AI extracts key concepts', color: 'text-blue-400' },
                  { icon: Brain, title: 'Segment', desc: 'Breaks into digestible parts', color: 'text-purple-400' },
                  { icon: Video, title: 'Animate', desc: 'Creates Manim animations', color: 'text-pink-400' },
                ].map((f) => (
                  <div key={f.title} className="glass-card rounded-xl p-4 text-left">
                    <f.icon className={`w-6 h-6 ${f.color} mb-2`} />
                    <h3 className="font-medium text-white text-sm">{f.title}</h3>
                    <p className="text-xs text-dark-400">{f.desc}</p>
                  </div>
                ))}
              </motion.div>

              {error && (
                <div className="mt-6 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                  {error}
                </div>
              )}
            </motion.div>
          )}

          {/* Results */}
          {state === 'results' && (
            <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">{searchResults.length} Results</h2>
                <button onClick={handleReset} className="text-sm text-dark-400 hover:text-white">← Back</button>
              </div>
              <div className="grid gap-3">
                {searchResults.map((paper, i) => (
                  <PaperCard key={paper.arxiv_id} paper={paper} onSelect={handleSelectPaper} index={i} />
                ))}
              </div>
            </motion.div>
          )}

          {/* Processing */}
          {state === 'processing' && (
            <motion.div
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="max-w-md mx-auto text-center pt-12"
            >
              <motion.div
                className="w-16 h-16 mx-auto mb-6 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center"
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              >
                <Zap className="w-8 h-8 text-white" />
              </motion.div>
              <h2 className="text-xl font-bold text-white mb-2">Generating</h2>
              <p className="text-dark-400 text-sm mb-6">This may take a few minutes...</p>

              <ProcessingSteps steps={processingSteps} />

              {error && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                  {error}
                  <button onClick={handleReset} className="block mt-2 underline text-xs">Try again</button>
                </div>
              )}
            </motion.div>
          )}

          {/* Completed */}
          {state === 'completed' && (
            <motion.div key="completed" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <div className="glass-card rounded-xl p-4 mb-6 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-400" />
                  <div>
                    <h2 className="font-medium text-white">{paperTitle}</h2>
                    <p className="text-xs text-dark-400">{videos.length} animations</p>
                  </div>
                </div>
                <button
                  onClick={handleReset}
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-500 rounded-lg text-sm flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" /> New
                </button>
              </div>

              <div className="grid lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2 grid md:grid-cols-2 gap-3">
                  {videos.map((video, i) => (
                    <VideoPlayer
                      key={video.video_id}
                      video={video}
                      title={segments[i]?.topic || `Animation ${i + 1}`}
                      index={i}
                    />
                  ))}
                </div>
                <SegmentList segments={segments} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-dark-500 text-xs">
        <div className="flex items-center justify-center gap-2">
          <Zap className="w-4 h-4 text-primary-500" />
          <span>Xe-Bot</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
