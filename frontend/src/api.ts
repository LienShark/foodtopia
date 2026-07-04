const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8080";
const TOKEN_KEY = "foodtopia_access_token";

export type DescriptionMode = "hidden" | "partial" | "full";
export type SurpriseBagStatus = "draft" | "active" | "sold_out" | "expired" | "hidden";
export type MerchantUserRole = "owner" | "staff";
export type MerchantStatus = "approved" | "suspended";

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
}

export interface MerchantCreate {
  name: string;
  google_place_id: string;
  address: string;
  lat: number;
  lng: number;
  phone?: string | null;
  business_type: string;
}

export interface MerchantOwnerCreate {
  name: string;
  phone?: string | null;
  email?: string | null;
  password?: string | null;
  line_user_id?: string | null;
}

export interface MerchantRegisterRequest {
  merchant: MerchantCreate;
  owner: MerchantOwnerCreate;
  approval_code: string;
}

export interface MerchantRead {
  id: string;
  name: string;
  google_place_id: string;
  address: string;
  lat: number;
  lng: number;
  phone?: string | null;
  business_type: string;
  status: MerchantStatus;
}

export interface MerchantUserRead {
  id: string;
  merchant_id: string;
  name: string;
  phone?: string | null;
  email?: string | null;
  line_user_id?: string | null;
  role: MerchantUserRole;
}

export interface MerchantRegisterResponse {
  merchant: MerchantRead;
  owner: MerchantUserRead;
}

export interface SurpriseBagCreate {
  title: string;
  category: string;
  description?: string | null;
  description_mode: DescriptionMode;
  price: number;
  original_value?: number | null;
  quantity: number;
  pickup_start_at?: string | null;
  pickup_end_at?: string | null;
  allergens: string[];
  dietary_flags: string[];
  storage_note?: string | null;
}

export interface SurpriseBagRead extends SurpriseBagCreate {
  id: string;
  merchant_id: string;
  quantity_sold: number;
  quantity_reserved: number;
  status: SurpriseBagStatus;
  created_at: string;
  updated_at: string;
}

export interface PublicSurpriseBagRead {
  id: string;
  merchant_id: string;
  merchant_name: string;
  title: string;
  category: string;
  description?: string | null;
  description_mode: DescriptionMode;
  price: number;
  original_value?: number | null;
  available_quantity: number;
  pickup_start_at?: string | null;
  pickup_end_at?: string | null;
  allergens: string[];
  dietary_flags: string[];
}

interface ApiFetchOptions extends RequestInit {
  auth?: boolean;
}

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) ?? "";
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 15000);

  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  headers.set("ngrok-skip-browser-warning", "true");

  if (options.auth !== false) {
    const token = getToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("後端連線逾時，請確認後端 ngrok 與 FastAPI 都有開著");
    }

    throw new Error(
      `後端連線失敗，請確認 VITE_API_BASE_URL 是否是後端 ngrok 網址：${API_BASE_URL}`,
    );
  } finally {
    window.clearTimeout(timeoutId);
  }

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(" / ")
      : detail || `HTTP ${response.status}`;

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function registerMerchant(
  payload: MerchantRegisterRequest,
): Promise<MerchantRegisterResponse> {
  return apiFetch("/merchant-auth/register", {
    method: "POST",
    auth: false,
    body: JSON.stringify(payload),
  });
}

export function loginEmail(email: string, password: string): Promise<TokenResponse> {
  return apiFetch("/merchant-auth/login/email", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ email, password }),
  });
}

export function loginLine(lineUserId: string): Promise<TokenResponse> {
  return apiFetch("/merchant-auth/login/line", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ line_user_id: lineUserId }),
  });
}

export function getCurrentMerchantUser(): Promise<MerchantUserRead> {
  return apiFetch("/merchant-auth/me");
}

export function createSurpriseBag(payload: SurpriseBagCreate): Promise<SurpriseBagRead> {
  return apiFetch("/merchant/surprise-bags", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listMerchantSurpriseBags(): Promise<SurpriseBagRead[]> {
  return apiFetch("/merchant/surprise-bags");
}

export function listPublicSurpriseBags(
  params: { sort?: "new" | "popular"; category?: string } = {},
): Promise<PublicSurpriseBagRead[]> {
  const searchParams = new URLSearchParams();
  searchParams.set("sort", params.sort ?? "new");

  if (params.category) {
    searchParams.set("category", params.category);
  }

  return apiFetch(`/surprise-bags?${searchParams.toString()}`, {
    auth: false,
  });
}

export function getPublicSurpriseBag(
  surpriseBagId: string,
): Promise<PublicSurpriseBagRead> {
  return apiFetch(`/surprise-bags/${surpriseBagId}`, {
    auth: false,
  });
}

export function listPublicMerchantSurpriseBags(
  merchantId: string,
): Promise<PublicSurpriseBagRead[]> {
  return apiFetch(`/merchants/${merchantId}/surprise-bags`, {
    auth: false,
  });
}
