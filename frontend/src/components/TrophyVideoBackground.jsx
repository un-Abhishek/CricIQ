import { useEffect, useRef, useState } from "react";

export default function TrophyVideoBackground({ children, videoSpeed = 1.0 }) {
  const videoRef = useRef(null);
  const [isEnded, setIsEnded] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    // Reset video state on mount / navigate to Dashboard
    video.currentTime = 0.0;
    video.muted = true;
    video.playbackRate = videoSpeed;
    setIsEnded(false);
    setIsTransitioning(false);

    let transitionTriggered = false;

    const playVideo = () => {
      video.muted = true;
      video.playbackRate = videoSpeed;
      const promise = video.play();
      if (promise !== undefined) {
        promise.catch((err) => {
          console.warn("Video play notice:", err);
        });
      }
    };

    const handleTimeUpdate = () => {
      if (!video.duration) return;

      // As video approaches the end, freeze smoothly on the LAST frame
      if (video.currentTime >= video.duration - 0.3 && !transitionTriggered) {
        transitionTriggered = true;
        setIsTransitioning(true);

        setTimeout(() => {
          if (video && video.duration) {
            video.currentTime = Math.max(0, video.duration - 0.05); // Freeze on LAST frame
            video.pause();
            setIsEnded(true);

            setTimeout(() => {
              setIsTransitioning(false);
            }, 150);
          }
        }, 250);
      }
    };

    const handleEnded = () => {
      if (!isEnded) {
        setIsEnded(true);
        if (video && video.duration) {
          video.currentTime = Math.max(0, video.duration - 0.05); // Freeze on LAST frame
          video.pause();
        }
      }
    };

    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("ended", handleEnded);

    // Attempt playback immediately and on loadedmetadata / canplay
    playVideo();
    video.addEventListener("canplay", playVideo, { once: true });
    video.addEventListener("loadedmetadata", playVideo, { once: true });

    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
      video.removeEventListener("ended", handleEnded);
      video.removeEventListener("canplay", playVideo);
      video.removeEventListener("loadedmetadata", playVideo);
    };
  }, [videoSpeed]);

  return (
    <div className="trophy-bg-wrapper">
      {/* HTML5 Video Background */}
      <div className="trophy-bg-canvas-container">
        <video
          ref={videoRef}
          className="trophy-bg-video"
          src="/trophy-video.mp4"
          muted
          playsInline
          autoPlay
          preload="auto"
        />

        {/* Ambient Overlay for text readability */}
        <div className="trophy-bg-overlay" />
        <div className="trophy-bg-gradient-bottom" />

        {/* Smooth Cinematic Dissolve Overlay to Last Frame */}
        <div className={`dissolve-overlay ${isTransitioning ? "active" : ""}`} />
      </div>

      {/* Dashboard Content */}
      <div className={`trophy-bg-content ${isEnded ? "content-visible" : "content-entering"}`}>
        {children}
      </div>
    </div>
  );
}
