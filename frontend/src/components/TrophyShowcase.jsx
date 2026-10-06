import { useEffect, useRef, useState } from "react";
import { Play, Pause, RotateCcw, Maximize2, Sparkles, ShieldCheck, Flame } from "lucide-react";
import "./TrophyShowcase.css";

const TOTAL_FRAMES = 21;

const STAGE_TITLES = {
  0: "Stage 01: Pedestal Activation",
  1: "Stage 01: Pedestal Activation",
  2: "Stage 02: Golden Aura Ignition",
  3: "Stage 02: Golden Aura Ignition",
  4: "Stage 03: Resonance & Light Ripples",
  5: "Stage 03: Resonance & Light Ripples",
  6: "Stage 04: Intense Photonic Glow",
  7: "Stage 04: Intense Photonic Glow",
  8: "Stage 05: Golden Sparks Orbit",
  9: "Stage 05: Golden Sparks Orbit",
  10: "Stage 06: Molten Core Fusion",
  11: "Stage 07: Cosmic Energy Ignition",
  12: "Stage 08: Interior Energy Vortex",
  13: "Stage 09: Lid Levitation",
  14: "Stage 10: Beams of Pure Energy",
  15: "Stage 11: Vapor & Essence Dispersion",
  16: "Stage 12: Golden Beams Burst",
  17: "Stage 13: Cosmic Nebula Unlocked",
  18: "Stage 14: Cosmic Essence Spill",
  19: "Stage 15: Maximum Energy Peak",
  20: "Stage 16: Lid Descent & Loop"
};

export default function TrophyShowcase() {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const imagesRef = useRef([]);
  
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isHoverScrubbing, setIsHoverScrubbing] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(10); // fps

  // Preload all 21 frames
  useEffect(() => {
    let loadedCount = 0;
    const loadedImages = [];

    for (let i = 1; i <= TOTAL_FRAMES; i++) {
      const img = new Image();
      const num = i < 10 ? `0${i}` : `${i}`;
      img.src = `/trophy-sequence/frame-${num}.jpg`;
      img.onload = () => {
        loadedCount++;
        if (loadedCount === TOTAL_FRAMES) {
          setIsLoaded(true);
        }
      };
      loadedImages.push(img);
    }
    imagesRef.current = loadedImages;
  }, []);

  // Animation Loop
  useEffect(() => {
    if (!isPlaying || isHoverScrubbing) return;
    const interval = setInterval(() => {
      setCurrentFrame((prev) => (prev + 1) % TOTAL_FRAMES);
    }, 1000 / playbackSpeed);

    return () => clearInterval(interval);
  }, [isPlaying, isHoverScrubbing, playbackSpeed]);

  // Draw current frame to canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const img = imagesRef.current[currentFrame];

    if (img && img.complete) {
      canvas.width = canvas.clientWidth * window.devicePixelRatio || 800;
      canvas.height = canvas.clientHeight * window.devicePixelRatio || 500;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Calculate cover/contain dimensions
      const scale = Math.min(canvas.width / img.width, canvas.height / img.height);
      const x = (canvas.width - img.width * scale) / 2;
      const y = (canvas.height - img.height * scale) / 2;

      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
    }
  }, [currentFrame, isLoaded]);

  // Handle Mouse Scrubbing across canvas
  const handleMouseMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, x / rect.width));
    const frameIndex = Math.min(TOTAL_FRAMES - 1, Math.floor(percentage * TOTAL_FRAMES));
    setCurrentFrame(frameIndex);
  };

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  return (
    <div className={`trophy-showcase-card ${isFullscreen ? "fullscreen" : ""}`}>
      <div className="showcase-header">
        <div className="showcase-badge">
          <Sparkles size={14} className="sparkle-icon" />
          <span>Interactive 3D Trophy Showcase</span>
        </div>
        <div className="stage-indicator">
          <span className="live-dot" />
          {STAGE_TITLES[currentFrame] || "IPL Championship Trophy"}
        </div>
      </div>

      <div
        ref={containerRef}
        className="canvas-container"
        onMouseEnter={() => setIsHoverScrubbing(true)}
        onMouseLeave={() => setIsHoverScrubbing(false)}
        onMouseMove={handleMouseMove}
      >
        <canvas ref={canvasRef} className="trophy-canvas" />

        {!isLoaded && (
          <div className="canvas-loader">
            <div className="spinner" />
            <span>Loading 21-Frame Trophy Experience…</span>
          </div>
        )}

        {/* Ambient Glow Effects */}
        <div className="canvas-ambient-glow" />
        
        {/* Floating Stat Badges */}
        <div className="floating-badge badge-top-right">
          <Flame size={15} color="#e5b842" />
          <div>
            <strong>IPL Championship</strong>
            <small>Gold Trophy Experience</small>
          </div>
        </div>

        <div className="floating-badge badge-bottom-left">
          <ShieldCheck size={15} color="#2bd980" />
          <div>
            <strong>Ball-By-Ball DB</strong>
            <small>Deep Metric Precision</small>
          </div>
        </div>

        {isHoverScrubbing && (
          <div className="scrub-tooltip">
            Frame {currentFrame + 1} / {TOTAL_FRAMES} (Hover to Scrub)
          </div>
        )}
      </div>

      {/* Control Bar */}
      <div className="showcase-controls">
        <button
          className="control-btn play-btn"
          onClick={() => setIsPlaying(!isPlaying)}
          title={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? <Pause size={16} /> : <Play size={16} />}
        </button>

        <button
          className="control-btn"
          onClick={() => setCurrentFrame(0)}
          title="Reset Frame"
        >
          <RotateCcw size={16} />
        </button>

        <div className="timeline-scrubber">
          <input
            type="range"
            min="0"
            max={TOTAL_FRAMES - 1}
            value={currentFrame}
            onChange={(e) => setCurrentFrame(parseInt(e.target.value, 10))}
          />
          <div
            className="timeline-fill"
            style={{ width: `${((currentFrame + 1) / TOTAL_FRAMES) * 100}%` }}
          />
        </div>

        <div className="frame-counter">
          <span>{currentFrame + 1}</span> / {TOTAL_FRAMES}
        </div>

        <select
          className="speed-selector"
          value={playbackSpeed}
          onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
        >
          <option value="6">0.5x</option>
          <option value="10">1.0x</option>
          <option value="18">1.5x</option>
          <option value="25">2.0x</option>
        </select>

        <button
          className="control-btn"
          onClick={toggleFullscreen}
          title="Toggle Fullscreen"
        >
          <Maximize2 size={16} />
        </button>
      </div>
    </div>
  );
}
