import React, { useMemo } from "react";

/**
 * Risk heatmap displayed as a color-coded table grid.
 * Rows = origin countries, columns = HS chapters.
 * Cell color intensity reflects the average risk score.
 */

function scoreToColor(score) {
  if (score >= 80) return { bg: "#dc2626", text: "#fff" };
  if (score >= 60) return { bg: "#ea580c", text: "#fff" };
  if (score >= 40) return { bg: "#d97706", text: "#fff" };
  if (score >= 20) return { bg: "#65a30d", text: "#fff" };
  return { bg: "#16a34a", text: "#fff" };
}

function RiskHeatmap({ data }) {
  const { countries, chapters, matrix } = useMemo(() => {
    if (!data || !data.cells || data.cells.length === 0) {
      return { countries: [], chapters: [], matrix: {} };
    }

    const countrySet = new Set();
    const chapterSet = new Set();
    const m = {};

    data.cells.forEach((cell) => {
      countrySet.add(cell.origin_country);
      chapterSet.add(cell.hs_chapter);
      const key = `${cell.origin_country}|${cell.hs_chapter}`;
      m[key] = cell;
    });

    return {
      countries: Array.from(countrySet).sort(),
      chapters: Array.from(chapterSet).sort(),
      matrix: m,
    };
  }, [data]);

  if (countries.length === 0) {
    return (
      <div style={{ color: "#a0aec0", textAlign: "center", padding: "40px 0" }}>
        No risk heatmap data available
      </div>
    );
  }

  const cellSize = "48px";

  return (
    <div style={{ overflowX: "auto", maxHeight: "400px", overflowY: "auto" }}>
      <table
        style={{
          borderCollapse: "collapse",
          fontSize: "11px",
          fontFamily: "monospace",
        }}
      >
        <thead>
          <tr>
            <th
              style={{
                position: "sticky",
                top: 0,
                left: 0,
                zIndex: 2,
                backgroundColor: "#1a1a2e",
                padding: "4px 8px",
                color: "#a0aec0",
              }}
            >
              Country
            </th>
            {chapters.map((ch) => (
              <th
                key={ch}
                style={{
                  position: "sticky",
                  top: 0,
                  zIndex: 1,
                  backgroundColor: "#1a1a2e",
                  padding: "4px",
                  color: "#a0aec0",
                  width: cellSize,
                  textAlign: "center",
                }}
              >
                HS {ch}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {countries.map((country) => (
            <tr key={country}>
              <td
                style={{
                  position: "sticky",
                  left: 0,
                  backgroundColor: "#1a1a2e",
                  padding: "4px 8px",
                  color: "#e0e0e0",
                  fontWeight: 600,
                }}
              >
                {country}
              </td>
              {chapters.map((ch) => {
                const cell = matrix[`${country}|${ch}`];
                if (!cell) {
                  return (
                    <td
                      key={ch}
                      style={{
                        width: cellSize,
                        height: cellSize,
                        backgroundColor: "#0f0f23",
                        border: "1px solid #2a2a4a",
                      }}
                    />
                  );
                }
                const colors = scoreToColor(cell.avg_score);
                return (
                  <td
                    key={ch}
                    title={`${country} / HS ${ch}: score ${cell.avg_score}, ${cell.declaration_count} declarations`}
                    style={{
                      width: cellSize,
                      height: cellSize,
                      backgroundColor: colors.bg,
                      color: colors.text,
                      textAlign: "center",
                      border: "1px solid #2a2a4a",
                      cursor: "pointer",
                      fontWeight: 600,
                    }}
                  >
                    {cell.avg_score.toFixed(0)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Legend */}
      <div
        style={{
          display: "flex",
          gap: "12px",
          marginTop: "12px",
          fontSize: "11px",
          color: "#a0aec0",
          alignItems: "center",
        }}
      >
        <span>Risk Level:</span>
        {[
          { label: "Low (0-20)", color: "#16a34a" },
          { label: "Med-Low (20-40)", color: "#65a30d" },
          { label: "Medium (40-60)", color: "#d97706" },
          { label: "High (60-80)", color: "#ea580c" },
          { label: "Critical (80+)", color: "#dc2626" },
        ].map(({ label, color }) => (
          <span key={label} style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <span
              style={{
                width: "12px",
                height: "12px",
                borderRadius: "2px",
                backgroundColor: color,
                display: "inline-block",
              }}
            />
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}

export default RiskHeatmap;
