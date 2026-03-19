import React, { useState, useEffect } from "react";
import TradeVolumeChart from "./TradeVolumeChart";
import RiskHeatmap from "./RiskHeatmap";
import TopTraders from "./TopTraders";
import AnomalyTimeline from "./AnomalyTimeline";
import {
  fetchTradeVolume,
  fetchRiskHeatmap,
  fetchTopTraders,
  fetchAnomalies,
} from "../services/api";

const cardStyle = {
  backgroundColor: "#1a1a2e",
  borderRadius: "8px",
  padding: "20px",
  border: "1px solid #2a2a4a",
};

const kpiStyle = {
  ...cardStyle,
  textAlign: "center",
  minWidth: "180px",
};

const kpiValueStyle = {
  fontSize: "28px",
  fontWeight: 700,
  color: "#00d4ff",
  margin: "8px 0 4px",
};

const kpiLabelStyle = {
  fontSize: "12px",
  color: "#a0aec0",
  textTransform: "uppercase",
  letterSpacing: "1px",
};

function KPICard({ label, value, color }) {
  return (
    <div style={kpiStyle}>
      <div style={kpiLabelStyle}>{label}</div>
      <div style={{ ...kpiValueStyle, color: color || "#00d4ff" }}>{value}</div>
    </div>
  );
}

function Dashboard() {
  const [volumeData, setVolumeData] = useState(null);
  const [heatmapData, setHeatmapData] = useState(null);
  const [tradersData, setTradersData] = useState(null);
  const [anomalyData, setAnomalyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const [volume, heatmap, traders, anomalies] = await Promise.allSettled([
          fetchTradeVolume({ granularity: "monthly" }),
          fetchRiskHeatmap(),
          fetchTopTraders({ direction: "import", limit: 10 }),
          fetchAnomalies({ minSeverity: "medium", limit: 20 }),
        ]);

        if (volume.status === "fulfilled") setVolumeData(volume.value);
        if (heatmap.status === "fulfilled") setHeatmapData(heatmap.value);
        if (traders.status === "fulfilled") setTradersData(traders.value);
        if (anomalies.status === "fulfilled") setAnomalyData(anomalies.value);
      } catch (err) {
        setError("Failed to load dashboard data. Is the backend running?");
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const totalDeclarations = volumeData
    ? volumeData.data.reduce((sum, d) => sum + d.total_declarations, 0)
    : 0;
  const totalValue = volumeData
    ? volumeData.data.reduce((sum, d) => sum + d.total_value, 0)
    : 0;
  const anomalyCount = anomalyData ? anomalyData.total : 0;

  if (loading) {
    return (
      <div style={{ color: "#a0aec0", textAlign: "center", marginTop: "80px" }}>
        <div style={{ fontSize: "18px" }}>Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ color: "#ff6b6b", textAlign: "center", marginTop: "80px" }}>
        <div style={{ fontSize: "18px" }}>{error}</div>
        <p style={{ color: "#a0aec0", marginTop: "12px" }}>
          Run <code>docker-compose up</code> to start all services.
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* KPI row */}
      <div
        style={{
          display: "flex",
          gap: "16px",
          marginBottom: "24px",
          flexWrap: "wrap",
        }}
      >
        <KPICard
          label="Total Declarations"
          value={totalDeclarations.toLocaleString()}
        />
        <KPICard
          label="Total Trade Value"
          value={`$${(totalValue / 1e6).toFixed(1)}M`}
          color="#4ade80"
        />
        <KPICard
          label="Anomalies Detected"
          value={anomalyCount}
          color="#ff6b6b"
        />
        <KPICard
          label="Countries Monitored"
          value={
            heatmapData
              ? new Set(heatmapData.cells.map((c) => c.origin_country)).size
              : 0
          }
          color="#fbbf24"
        />
      </div>

      {/* Charts grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
          marginBottom: "24px",
        }}
      >
        <div style={cardStyle}>
          <h3 style={{ color: "#e0e0e0", marginTop: 0, marginBottom: "16px" }}>
            Trade Volume Trends
          </h3>
          <TradeVolumeChart data={volumeData} />
        </div>

        <div style={cardStyle}>
          <h3 style={{ color: "#e0e0e0", marginTop: 0, marginBottom: "16px" }}>
            Risk Heatmap
          </h3>
          <RiskHeatmap data={heatmapData} />
        </div>
      </div>

      {/* Bottom row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
        }}
      >
        <div style={cardStyle}>
          <h3 style={{ color: "#e0e0e0", marginTop: 0, marginBottom: "16px" }}>
            Top Importers
          </h3>
          <TopTraders data={tradersData} />
        </div>

        <div style={cardStyle}>
          <h3 style={{ color: "#e0e0e0", marginTop: 0, marginBottom: "16px" }}>
            Anomaly Timeline
          </h3>
          <AnomalyTimeline data={anomalyData} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
