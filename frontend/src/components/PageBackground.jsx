import "./PageBackground.css";

export default function PageBackground({ bgImage, children }) {
  return (
    <div className="section-bg-wrapper">
      {/* Background Image Layer */}
      <div
        className="section-bg-image"
        style={{ backgroundImage: `url(${bgImage})` }}
      >
        <div className="section-bg-overlay" />
        <div className="section-bg-gradient-bottom" />
      </div>

      {/* Page Content */}
      <div className="section-bg-content">{children}</div>
    </div>
  );
}
