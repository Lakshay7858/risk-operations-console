import React from "react";

const tableStyles = {
  width: "100%",
  borderCollapse: "collapse",
  fontSize: "13px",
};

const thStyle = {
  textAlign: "left",
  padding: "10px 12px",
  color: "#a0aec0",
  borderBottom: "2px solid #2a2a4a",
  fontSize: "11px",
  textTransform: "uppercase",
  letterSpacing: "0.5px",
};

const tdStyle = {
  padding: "10px 12px",
  color: "#e0e0e0",
  borderBottom: "1px solid #2a2a4a",
};

function riskBadge(score) {
  if (score === null || score === undefined) {
    return <span style={{ color: "#a0aec0" }}>--</span>;
  }

  let bg, text;
  if (score >= 75) {
    bg = "#dc2626";
    text = "#fff";
  } else if (score >= 50) {
    bg = "#ea580c";
    text = "#fff";
  } else if (score >= 25) {
    bg = "#d97706";
    text = "#fff";
  } else {
    bg = "#16a34a";
    text = "#fff";
  }

  return (
    <span
      style={{
        backgroundColor: bg,
        color: text,
        padding: "2px 8px",
        borderRadius: "10px",
        fontSize: "11px",
        fontWeight: 600,
      }}
    >
      {score.toFixed(1)}
    </span>
  );
}

function TopTraders({ data }) {
  if (!data || !data.traders || data.traders.length === 0) {
    return (
      <div style={{ color: "#a0aec0", textAlign: "center", padding: "40px 0" }}>
        No trader data available
      </div>
    );
  }

  return (
    <div style={{ overflowX: "auto", maxHeight: "400px", overflowY: "auto" }}>
      <table style={tableStyles}>
        <thead>
          <tr>
            <th style={thStyle}>#</th>
            <th style={thStyle}>Name</th>
            <th style={thStyle}>Country</th>
            <th style={{ ...thStyle, textAlign: "right" }}>Declarations</th>
            <th style={{ ...thStyle, textAlign: "right" }}>Total Value</th>
            <th style={{ ...thStyle, textAlign: "center" }}>Risk Score</th>
          </tr>
        </thead>
        <tbody>
          {data.traders.map((trader, idx) => (
            <tr
              key={trader.importer_id}
              style={{
                backgroundColor: idx % 2 === 0 ? "transparent" : "rgba(255,255,255,0.02)",
                transition: "background-color 0.2s",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.backgroundColor = "rgba(0,212,255,0.05)")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.backgroundColor =
                  idx % 2 === 0 ? "transparent" : "rgba(255,255,255,0.02)")
              }
            >
              <td style={{ ...tdStyle, color: "#a0aec0", width: "40px" }}>
                {idx + 1}
              </td>
              <td style={{ ...tdStyle, fontWeight: 600 }}>{trader.name}</td>
              <td style={tdStyle}>
                <span
                  style={{
                    backgroundColor: "#2a2a4a",
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontSize: "11px",
                    fontFamily: "monospace",
                  }}
                >
                  {trader.country_code}
                </span>
              </td>
              <td style={{ ...tdStyle, textAlign: "right", fontFamily: "monospace" }}>
                {trader.declaration_count.toLocaleString()}
              </td>
              <td style={{ ...tdStyle, textAlign: "right", fontFamily: "monospace" }}>
                ${(trader.total_value / 1e6).toFixed(2)}M
              </td>
              <td style={{ ...tdStyle, textAlign: "center" }}>
                {riskBadge(trader.avg_risk_score)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TopTraders;
