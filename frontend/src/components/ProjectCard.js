import React from "react";
import "../style/style.css";

function ProjectCard({ data }) {
  if (!data || typeof data !== "object") return null;

  return (
    <div className="project-card">
      {Object.entries(data).map(([key, value]) => (
        <div key={key} className="project-field">
          <strong>{key}:</strong>{" "}
          {key.toLowerCase() === "url" ? (
            value ? (
              <div className="image-section">
                <img
                  src={value}
                  alt="Project"
                  className="project-image"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src =
                      "https://via.placeholder.com/300x200?text=Image+Not+Available";
                  }}
                />
                <p>
                  <a href={value} target="_blank" rel="noopener noreferrer">
                    View Full Image
                  </a>
                </p>
              </div>
            ) : (
              "No image available"
            )
          ) : (
            <span>{value || "Unknown"}</span>
          )}
        </div>
      ))}
    </div>
  );
}

export default ProjectCard;
