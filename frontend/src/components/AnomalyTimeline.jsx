import React from "react";

function severityConfig(severity) {
  switch (severity) {
    case "critical":
      return { color: "#dc2626", bg: "rgba(220,38,38,0.15)", label: "CRITICAL" };
    case "high":
      return { color: "#ea580c", bg: "rgba(234,88,12,0.15)", label: "HIGH" };
    case "medium":
      return { color: "#d97706", bg: "rgba(217,119,6,0.15)", label: "MEDIUM" };
    case "low":
      return { color: "#16a34a", bg: "rgba(22,163,74,0.15)", label: "LOW" };
    default:
      return { color: "#a0aec0", bg: "rgba(160,174,192,0.1)", label: severity };
  }
}

function AnomalyTimeline({ data }) {
  if (!data || !data.anomalies || data.anomalies.length === 0) {
    return (
      <div style={{ color: "#a0aec0", textAlign: "center", padding: "40px 0" }}>
        No anomalies detected
      </div>
    );
  }

  return (
    <div style={{ maxHeight: "400px", overflowY: "auto", paddingRight: "8px" }}>
      {data.anomalies.map((anomaly, idx) => {
        const sev = severityConfig(anomaly.severity);
        return (
          <div
            key={`${anomaly.declaration_id}-${idx}`}
            style={{
              display: "flex",
              gap: "16px",
              padding: "12px 0",
              borderBottom:
                idx < data.anomalies.length - 1
                  ? "1px solid #2a2a4a"
                  : "none",
            }}
          >
            {/* Timeline dot and line */}
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                minWidth: "20px",
              }}
            >
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  borderRadius: "50%",
                  backgroundColor: sev.color,
                  flexShrink: 0,
                  marginTop: "4px",
                }}
              />
              {idx < data.anomalies.length - 1 && (
                <div
                  style={{
                    width: "2px",
                    flexGrow: 1,
                    backgroundColor: "#2a2a4a",
                    marginTop: "4px",
                  }}
                />
              )}
            </div>

            {/* Content */}
            <div style={{ flexGrow: 1 }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  marginBottom: "4px",
                }}
              >
                <span
                  style={{
                    backgroundColor: sev.bg,
                    color: sev.color,
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontSize: "10px",
                    fontWeight: 700,
                    letterSpacing: "0.5px",
                  }}
                >
                  {sev.label}
                </span>
                <span
                  style={{
                    color: "#a0aec0",
                    fontSize: "12px",
                    fontFamily: "monospace",
                  }}
                >
                  Score: {anomaly.score.toFixed(1)}
                </span>
                <span style={{ color: "#4a5568", fontSize: "12px" }}>
                  {anomaly.declaration_date}
                </span>
              </div>

              <div style={{ color: "#e0e0e0", fontSize: "13px", fontWeight: 600 }}>
                {anomaly.declaration_number}
                {anomaly.importer_name && (
                  <span
                    style={{
                      color: "#a0aec0",
                      fontWeight: 400,
                      marginLeft: "8px",
                    }}
                  >
                    -- {anomaly.importer_name}
                  </span>
                )}
              </div>

              <div style={{ color: "#a0aec0", fontSize: "12px", marginTop: "4px" }}>
                <span
                  style={{
                    backgroundColor: "#2a2a4a",
                    padding: "1px 6px",
                    borderRadius: "3px",
                    fontFamily: "monospace",
                    fontSize: "11px",
                    marginRight: "8px",
                  }}
                >
                  {anomaly.rule_code}
                </span>
                {anomaly.rule_description || "No description available"}
              </div>
            </div>
          </div>
        );
      })}

      {data.total > data.anomalies.length && (
        <div
          style={{
            textAlign: "center",
            padding: "12px",
            color: "#a0aec0",
            fontSize: "12px",
          }}
        >
          Showing {data.anomalies.length} of {data.total} anomalies
        </div>
      )}
    </div>
  );
}

export default AnomalyTimeline;
