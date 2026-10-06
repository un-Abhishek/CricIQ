import { useEffect, useRef, useState } from "react";
import { RotateCcw, Sparkles } from "lucide-react";
import "./TrophyShowcase.css";

const TOTAL_FRAMES = 21;

export default function TrophyBackground({ children, onAnimationFinished }) {
  const canvasRef = useRef(null);
  const imagesRef = useRef([]);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isFinished, setIsFinished] = useState(false);

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

  // Play sequence once on load
  const playIntroSequence = () => {
    setCurrentFrame(0);
    setIsFinished(false);
    setIsPlaying(true);
  };

  useEffect(() => {
    if (!isLoaded || !isPlaying) return;

    const fps = 16; // ~1.3s total animation
    const interval = setInterval(() => {
      setCurrentFrame((prev) => {
        if (prev >= TOTAL_FRAMES - 1) {
          clearInterval(interval);
          setIsPlaying(false);
          setIsFinished(true);
          if (onAnimationFinished) onAnimationFinished();
          return TOTAL_FRAMES - 1; // Stay on last frame (frame 21)
        }
        return prev + 1;
      });
    }, 1000 / fps);

    return () => clearInterval(interval);
  }, [isLoaded, isPlaying, onAnimationFinished]);

  // Draw current frame to canvas cover
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const img = imagesRef.current[currentFrame];

    if (img && img.complete) {
      canvas.width = canvas.clientWidth * window.devicePixelRatio || window.innerWidth;
      canvas.height = canvas.clientHeight * window.devicePixelRatio || 700;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Cover scaling math
      const scale = Math.max(canvas.width / img.width, canvas.height / img.height);
      const x = (canvas.width - img.width * scale) / 2;
      const y = (canvas.height - img.height * scale) / 2;

      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
    }
  }, [currentFrame, isLoaded]);

  return (
    <div className="trophy-bg-wrapper">
      {/* Canvas Background */}
      <div className="trophy-bg-canvas-container">
        <canvas ref={canvasRef} className="trophy-bg-canvas" />

        {/* Ambient Dark Overlay to make Dashboard content pop */}
        <div className="trophy-bg-overlay" />
        <div className="trophy-bg-gradient-bottom" />
      </div>

      {/* Replay Intro Floating Button */}
      <button
        className="replay-intro-btn"
        onClick={playIntroSequence}
        title="Replay Opening Trophy Animation"
      >
        <RotateCcw size={14} />
        <span>Replay Intro</span>
      </button>

      {/* Dashboard Foreground Content */}
      <div className={`trophy-bg-content ${isFinished ? "content-visible" : "content-entering"}`}>
        {children}
      </div>
    </div>
  );
}
