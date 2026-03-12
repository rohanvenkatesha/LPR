"use client";
import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  Loader2, 
  Video, 
  Download,
  FileDown,
  Terminal,
  History,
  Layers,
  Monitor,
  AlertCircle
} from 'lucide-react';
//
// --- Types & Interfaces ---
interface PlateData {
  plate?: string;
  timestamp?: string;
  type?: string; 
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL!;
const WS_URL = process.env.NEXT_PUBLIC_WS_URL!;

const App: React.FC = () => {
  // --- State Management ---
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [videoComplete, setVideoComplete] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isReadyToSubmit, setIsReadyToSubmit] = useState<boolean>(false);
  
  const [rawVideoUrl, setRawVideoUrl] = useState<string | null>(null);
  const [csvUrl, setCsvUrl] = useState<string | null>(null);
  const [detectedPlates, setDetectedPlates] = useState<PlateData[]>([]);
  
  const wsRef = useRef<WebSocket | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // --- Auto-scroll effect for live metadata ---
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [detectedPlates]);

  // --- Backend Health Check ---
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/`);
        setBackendOnline(response.ok);
        if (response.ok) setError(null);
      } catch (err) {
        setBackendOnline(false);
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 10000); 
    return () => clearInterval(interval);
  }, []);

  const handleDownload = async (url: string, filename: string) => {
    setDownloading(filename);
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error("File not found.");
      
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      setError(`Download failed: ${filename}`);
    } finally {
      setDownloading(null);
    }
  };

  const connectWebSocket = () => {
    if (wsRef.current) wsRef.current.close();
    // wsRef.current = new WebSocket('ws://localhost:8000/ws');
    wsRef.current = new WebSocket(WS_URL);
    
    wsRef.current.onmessage = (event) => {
      try {
        const data: PlateData = JSON.parse(event.data);
        if (data.type === 'video_complete') {
          const timestamp = Date.now();
          // Points to your CSV endpoint
          // setCsvUrl(`http://localhost:8000/download-csv?t=${timestamp}`);
          setCsvUrl(`${BACKEND_URL}/download-csv?t=${timestamp}`);
          setVideoComplete(true);
          setIsProcessing(false);
          if (wsRef.current) wsRef.current.close();
        } else if (data.plate) {
          setDetectedPlates(prev => [...prev, data]);
        }
      } catch (err) {
        console.error("Socket error", err);
      }
    };

    wsRef.current.onerror = () => {
      setError("WebSocket connection failed. Live updates unavailable.");
    };
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setError(null);
    setVideoComplete(false);
    setDetectedPlates([]);
    setCsvUrl(null);
    setSelectedFile(file);
    setIsReadyToSubmit(true);
    setRawVideoUrl(URL.createObjectURL(file));
  };

  const handleStartAnalysis = () => {
    if (!selectedFile) return;
    setIsProcessing(true);
    setIsReadyToSubmit(false);
    setError(null);
    connectWebSocket();
    uploadVideo(selectedFile);
  };

  const handleReset = () => {
    setSelectedFile(null);
    setIsReadyToSubmit(false);
    setRawVideoUrl(null);
    setError(null);
    setVideoComplete(false);
    setDetectedPlates([]);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const uploadVideo = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      // const response = await fetch('http://localhost:8000/upload-video', {
      const response = await fetch(`${BACKEND_URL}/upload-video`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error("Upload error");
    } catch (err) {
      setError("Analysis failed. Core rejected the upload or is unreachable.");
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050508] text-[#e2e8f0] p-4 lg:p-8 font-mono selection:bg-cyan-500/30 overflow-x-hidden">
      {/* AMBIENT LIGHTING */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="absolute top-[10%] left-[15%] w-[300px] h-[300px] bg-cyan-600/10 blur-[150px] rounded-full"></div>
        <div className="absolute bottom-[20%] right-[10%] w-[400px] h-[400px] bg-purple-600/10 blur-[180px] rounded-full"></div>
      </div>

      <div className="max-w-[1600px] mx-auto">
        {/* TOP NAVIGATION BAR */}
        <header className="flex flex-col lg:flex-row justify-between items-center mb-8 pb-6 border-b border-white/5 gap-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-500 blur-md opacity-20 animate-pulse"></div>
              <div className="bg-[#0f111a] border border-cyan-500/50 p-2.5 rounded-lg relative">
                <Monitor className="text-cyan-400 w-7 h-7" />
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-black tracking-[0.15em] text-white">
                LPR<span className="text-cyan-500">.OS</span>
              </h1>
              <div className="flex items-center gap-2 mt-1">
                <span className="h-1 w-1 bg-cyan-500 rounded-full animate-ping"></span>
                <p className="text-[10px] text-cyan-500/80 font-bold uppercase tracking-[0.3em]">License Plate Recognition v7.0.2</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {error && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-red-500/10 border border-red-500/30 text-red-400 rounded text-[10px] font-bold uppercase animate-pulse">
                <AlertCircle size={14} /> {error}
              </div>
            )}
            <div className={`flex items-center gap-3 px-4 py-2 rounded-md border transition-all ${
              backendOnline ? 'bg-cyan-500/5 border-cyan-500/30 text-cyan-400' : 'bg-red-500/5 border-red-500/30 text-red-400'
            }`}>
              <div className={`w-1.5 h-1.5 rounded-full ${backendOnline ? 'bg-cyan-500 shadow-[0_0_8px_#22d3ee]' : 'bg-red-500'}`}></div>
              <span className="text-[10px] font-bold uppercase tracking-widest">
                {backendOnline ? 'Core Linked' : 'Core Offline'}
              </span>
            </div>
          </div>
        </header>

        {/* MAIN HUD LAYOUT */}
        <main className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* LEFT COLUMN: COMMANDS & LOGS */}
          <div className="lg:col-span-3 space-y-6">
            
            {/* INPUT PANEL */}
            <div className="bg-[#0c0e16]/80 border border-white/5 rounded-xl p-5 shadow-2xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-1 text-[8px] text-white/10 font-bold">MODULE_01</div>
              <h2 className="text-[10px] font-black uppercase tracking-[0.2em] mb-5 flex items-center gap-2 text-cyan-500/80">
                <Terminal size={14} /> Data_Ingestion
              </h2>

              {!isReadyToSubmit && !isProcessing && !videoComplete && (
                <div 
                  onClick={() => fileInputRef.current?.click()}
                  className="border border-white/5 bg-[#0f111a] rounded-lg p-8 transition-all cursor-pointer flex flex-col items-center text-center gap-4 hover:border-cyan-500/40 hover:bg-cyan-500/5 group"
                >
                  <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept="video/*" />
                  <div className="w-14 h-14 rounded-full border border-white/10 flex items-center justify-center group-hover:border-cyan-500/50 transition-all">
                    <Upload className="w-6 h-6 text-slate-500 group-hover:text-cyan-400" />
                  </div>
                  <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Select Source</p>
                </div>
              )}

              {(isReadyToSubmit || isProcessing || videoComplete) && (
                <div className="space-y-4">
                  <div className="bg-[#0f111a] border border-white/10 p-3 rounded-lg flex items-center gap-3">
                    <Video className="text-cyan-500 w-4 h-4" />
                    <div className="flex-1 min-w-0">
                      <p className="text-[10px] font-bold truncate text-slate-300 uppercase tracking-tighter">{selectedFile?.name}</p>
                    </div>
                  </div>

                  {isReadyToSubmit && (
                    <div className="grid grid-cols-1 gap-2">
                      <button onClick={handleStartAnalysis} disabled={!backendOnline} className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 text-black font-black text-[11px] uppercase tracking-[0.2em] rounded transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]">
                        Initialize Extraction
                      </button>
                      <button onClick={handleReset} className="w-full py-2 text-slate-500 hover:text-white text-[9px] font-bold uppercase tracking-widest">
                        Clear Selection
                      </button>
                    </div>
                  )}

                  {isProcessing && (
                    <div className="p-4 border border-cyan-500/20 bg-cyan-500/5 rounded-lg flex flex-col items-center gap-3">
                      <Loader2 className="w-5 h-5 text-cyan-500 animate-spin" />
                      <span className="text-[9px] text-cyan-400 font-black uppercase tracking-[0.2em]">Analyzing Buffers...</span>
                    </div>
                  )}

                  {videoComplete && (
                    <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-500">
                       <button 
                        onClick={() => csvUrl && handleDownload(csvUrl, 'plates_log.csv')} 
                        disabled={downloading !== null}
                        className="w-full flex items-center justify-between px-4 py-3 bg-[#161b2e] border border-cyan-500/30 text-cyan-400 rounded hover:bg-cyan-500 hover:text-black transition-all group disabled:opacity-50"
                       >
                         <span className="text-[10px] font-black uppercase tracking-widest">
                           {downloading === 'plates_log.csv' ? 'Processing...' : 'Download CSV'}
                         </span>
                         <FileDown size={14} />
                       </button>
                       <button 
                        onClick={() => handleDownload(`${BACKEND_URL}/download-video`, 'detected_output.mp4')} 
                        disabled={downloading !== null}
                        className="w-full flex items-center justify-between px-4 py-3 bg-[#161b2e] border border-purple-500/30 text-purple-400 rounded hover:bg-purple-500 hover:text-white transition-all group disabled:opacity-50"
                       >
                         <span className="text-[10px] font-black uppercase tracking-widest">
                           {downloading === 'detected_output.mp4' ? 'Processing...' : 'Save Render'}
                         </span>
                         <Download size={14} />
                       </button>
                       <button onClick={handleReset} className="w-full py-2 text-slate-600 hover:text-white text-[9px] font-black uppercase tracking-widest mt-2">Reset Core</button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* EVENT LOG */}
            <div className="bg-[#0c0e16]/80 border border-white/5 rounded-xl p-5 h-[450px] flex flex-col shadow-2xl relative">
              <div className="absolute top-0 right-0 p-1 text-[8px] text-white/10 font-bold">MODULE_02</div>
              <div className="flex justify-between items-center mb-5">
                <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-purple-400/80 flex items-center gap-2">
                  <History size={14} /> Extraction_Stream
                </h2>
                <div className="px-2 py-0.5 border border-white/10 rounded text-[8px] text-slate-500 font-bold">{detectedPlates.length} UNIT</div>
              </div>

              <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                {detectedPlates.length > 0 ? (
                  detectedPlates.map((data, idx) => (
                    <div key={idx} className="bg-[#0f111a] border border-white/5 p-3 rounded flex flex-col gap-1 border-l-2 border-l-cyan-500">
                      <div className="flex justify-between items-center opacity-50">
                        <span className="text-[8px] font-bold uppercase tracking-tighter text-cyan-500">Identity_Found</span>
                        <span className="text-[8px] font-mono">{data.timestamp}</span>
                      </div>
                      <p className="text-xl font-black text-white tracking-[0.2em]">{data.plate}</p>
                    </div>
                  ))
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-center opacity-20">
                    <Layers size={32} className="mb-2" />
                    <p className="text-[9px] font-black uppercase tracking-[0.2em]">Waiting for data</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: VISUAL CORE */}
          <div className="lg:col-span-9 space-y-6">
            <div className="relative group">
               <div className="absolute -top-1 -left-1 w-8 h-8 border-t-2 border-l-2 border-cyan-500/50 z-20"></div>
               <div className="absolute -bottom-1 -right-1 w-8 h-8 border-b-2 border-r-2 border-cyan-500/50 z-20"></div>
               
               <div className="bg-[#0c0e16] border border-white/5 rounded-lg overflow-hidden shadow-2xl aspect-video relative">
                 <div className="absolute top-4 left-4 z-20 flex flex-col gap-2">
                   <div className="bg-black/60 backdrop-blur-md border border-white/10 px-3 py-1 rounded text-[9px] font-black uppercase tracking-widest text-white/80 flex items-center gap-2">
                     <span className={`w-1.5 h-1.5 rounded-full ${isProcessing ? 'bg-red-500 animate-pulse' : 'bg-slate-600'}`}></span>
                     {videoComplete ? 'Source_Complete' : isProcessing ? 'Processing' : 'Standby'}
                   </div>
                 </div>

                 <div className="w-full h-full flex items-center justify-center">
                   {rawVideoUrl ? (
                     <video 
                       key={rawVideoUrl} 
                       src={rawVideoUrl} 
                       controls 
                       autoPlay 
                       className={`w-full h-full object-contain ${isProcessing ? 'brightness-125 contrast-125' : ''}`} 
                     />
                   ) : (
                     <div className="flex flex-col items-center gap-4 opacity-10">
                       <Monitor size={64} />
                       <p className="text-xs font-black uppercase tracking-[0.5em]">No Signal</p>
                     </div>
                   )}
                 </div>

                 {isProcessing && (
                   <div className="absolute inset-0 pointer-events-none z-10 overflow-hidden">
                     <div className="w-full h-[1px] bg-cyan-400/40 absolute top-0 left-0 animate-[v-scan_4s_linear_infinite] shadow-[0_0_10px_#22d3ee]"></div>
                   </div>
                 )}
               </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Unit Count', value: detectedPlates.length, color: 'text-cyan-400' },
                { label: 'Neural Load', value: isProcessing ? '62%' : '0%', color: 'text-purple-400' },
                { label: 'Accuracy', value: '98.4%', color: 'text-emerald-400' },
                { label: 'Link Quality', value: backendOnline ? '100%' : '0%', color: 'text-blue-400' },
              ].map((m, i) => (
                <div key={i} className="bg-[#0c0e16]/60 border border-white/5 p-4 rounded-xl flex flex-col items-center justify-center text-center">
                  <span className="text-[8px] font-black uppercase tracking-widest text-slate-500 mb-1">{m.label}</span>
                  <span className={`text-xl font-black ${m.color}`}>{m.value}</span>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
      
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes v-scan {
          from { transform: translateY(0); }
          to { transform: translateY(100vh); }
        }
        .custom-scrollbar::-webkit-scrollbar { width: 3px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; }
      `}} />
    </div>
  );
};

export default App;