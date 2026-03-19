import React, { useMemo } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function TradeVolumeChart({ data }) {
  const chartData = useMemo(() => {
    if (!data || !data.data || data.data.length === 0) {
      return null;
    }

    const labels = data.data.map((d) => d.period);
    return {
      labels,
      datasets: [
        {
          label: "Declarations",
          data: data.data.map((d) => d.total_declarations),
          borderColor: "#00d4ff",
          backgroundColor: "rgba(0, 212, 255, 0.1)",
          fill: true,
          tension: 0.3,
          pointRadius: 3,
          pointHoverRadius: 6,
          yAxisID: "y",
        },
        {
          label: "Value ($M)",
          data: data.data.map((d) => d.total_value / 1e6),
          borderColor: "#4ade80",
          backgroundColor: "rgba(74, 222, 128, 0.1)",
          fill: false,
          tension: 0.3,
          pointRadius: 3,
          pointHoverRadius: 6,
          yAxisID: "y1",
        },
      ],
    };
  }, [data]);

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    interaction: {
      mode: "index",
      intersect: false,
    },
    plugins: {
      legend: {
        labels: { color: "#a0aec0", usePointStyle: true },
      },
      tooltip: {
        backgroundColor: "#1a1a2e",
        titleColor: "#e0e0e0",
        bodyColor: "#a0aec0",
        borderColor: "#2a2a4a",
        borderWidth: 1,
        callbacks: {
          label: (context) => {
            const label = context.dataset.label;
            const value = context.parsed.y;
            if (label === "Value ($M)") {
              return `${label}: $${value.toFixed(1)}M`;
            }
            return `${label}: ${value.toLocaleString()}`;
          },
        },
      },
    },
    scales: {
      x: {
        ticks: { color: "#a0aec0" },
        grid: { color: "rgba(255,255,255,0.05)" },
      },
      y: {
        type: "linear",
        position: "left",
        ticks: { color: "#00d4ff" },
        grid: { color: "rgba(255,255,255,0.05)" },
        title: {
          display: true,
          text: "Declarations",
          color: "#00d4ff",
        },
      },
      y1: {
        type: "linear",
        position: "right",
        ticks: {
          color: "#4ade80",
          callback: (val) => `$${val}M`,
        },
        grid: { drawOnChartArea: false },
        title: {
          display: true,
          text: "Value ($M)",
          color: "#4ade80",
        },
      },
    },
  };

  if (!chartData) {
    return (
      <div style={{ color: "#a0aec0", textAlign: "center", padding: "40px 0" }}>
        No volume data available
      </div>
    );
  }

  return <Line data={chartData} options={options} />;
}

export default TradeVolumeChart;
