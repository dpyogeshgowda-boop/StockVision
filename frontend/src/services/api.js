import axios from "axios";

export const getApiBaseUrl = () => {
    if (import.meta.env?.VITE_API_BASE_URL) {
        return import.meta.env.VITE_API_BASE_URL;
    }
    if (typeof window !== "undefined") {
        const isCapacitor = window.Capacitor && typeof window.Capacitor.isNativePlatform === "function" && window.Capacitor.isNativePlatform();
        const isAndroid = typeof navigator !== "undefined" && /android/i.test(navigator.userAgent);
        if (isCapacitor || isAndroid) {
            return "http://10.0.2.2:8000";
        }
        if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
            return "http://127.0.0.1:8000";
        }
    }
    return "http://10.0.2.2:8000";
};

const API = axios.create({
    baseURL: getApiBaseUrl(),
});

export const getMarketSummary = async () => {
    const response = await API.get("/market-summary");
    return response.data;
};

export const getMarketData = async () => {
    const response = await API.get("/market-data?limit=250");
    return response.data;
};

export const getTechnicalIndicators = async () => {
    const response = await API.get("/technical-indicators");
    return response.data;
};

export default API;
