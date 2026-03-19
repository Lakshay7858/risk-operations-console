import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ---- Trades ----------------------------------------------------------------

export async function fetchDeclarations({ page = 1, pageSize = 50, direction } = {}) {
  const params = { page, page_size: pageSize };
  if (direction) params.direction = direction;
  const { data } = await client.get("/trades", { params });
  return data;
}

export async function searchDeclarations(filters = {}) {
  const params = {};
  if (filters.hsCode) params.hs_code = filters.hsCode;
  if (filters.originCountry) params.origin_country = filters.originCountry;
  if (filters.destinationCountry) params.destination_country = filters.destinationCountry;
  if (filters.dateFrom) params.date_from = filters.dateFrom;
  if (filters.dateTo) params.date_to = filters.dateTo;
  if (filters.minValue) params.min_value = filters.minValue;
  if (filters.maxValue) params.max_value = filters.maxValue;
  if (filters.flaggedOnly) params.flagged_only = true;
  if (filters.page) params.page = filters.page;
  if (filters.pageSize) params.page_size = filters.pageSize;
  const { data } = await client.get("/trades/search", { params });
  return data;
}

export async function fetchDeclaration(id) {
  const { data } = await client.get(`/trades/${id}`);
  return data;
}

// ---- Analytics -------------------------------------------------------------

export async function fetchTradeVolume({
  granularity = "monthly",
  dateFrom,
  dateTo,
  direction,
  hsCode,
} = {}) {
  const params = { granularity };
  if (dateFrom) params.date_from = dateFrom;
  if (dateTo) params.date_to = dateTo;
  if (direction) params.direction = direction;
  if (hsCode) params.hs_code = hsCode;
  const { data } = await client.get("/analytics/volume", { params });
  return data;
}

export async function fetchTopTraders({
  direction = "import",
  limit = 20,
  dateFrom,
  dateTo,
} = {}) {
  const params = { direction, limit };
  if (dateFrom) params.date_from = dateFrom;
  if (dateTo) params.date_to = dateTo;
  const { data } = await client.get("/analytics/top-traders", { params });
  return data;
}

export async function fetchHSBreakdown({ dateFrom, dateTo, direction } = {}) {
  const params = {};
  if (dateFrom) params.date_from = dateFrom;
  if (dateTo) params.date_to = dateTo;
  if (direction) params.direction = direction;
  const { data } = await client.get("/analytics/hs-breakdown", { params });
  return data;
}

export async function fetchAnomalies({
  dateFrom,
  dateTo,
  minSeverity = "medium",
  limit = 50,
} = {}) {
  const params = { min_severity: minSeverity, limit };
  if (dateFrom) params.date_from = dateFrom;
  if (dateTo) params.date_to = dateTo;
  const { data } = await client.get("/analytics/anomalies", { params });
  return data;
}

// ---- Risk ------------------------------------------------------------------

export async function fetchRiskHeatmap({ dateFrom, dateTo } = {}) {
  const params = {};
  if (dateFrom) params.date_from = dateFrom;
  if (dateTo) params.date_to = dateTo;
  const { data } = await client.get("/risk/heatmap", { params });
  return data;
}

export async function fetchRiskDistribution({ dateFrom, dateTo } = {}) {
  const params = {};
  if (dateFrom) params.date_from = dateFrom;
  if (dateTo) params.date_to = dateTo;
  const { data } = await client.get("/risk/distribution", { params });
  return data;
}

export async function fetchRiskScores({
  page = 1,
  pageSize = 50,
  riskCategory,
  minScore,
} = {}) {
  const params = { page, page_size: pageSize };
  if (riskCategory) params.risk_category = riskCategory;
  if (minScore !== undefined) params.min_score = minScore;
  const { data } = await client.get("/risk/scores", { params });
  return data;
}

export default client;
