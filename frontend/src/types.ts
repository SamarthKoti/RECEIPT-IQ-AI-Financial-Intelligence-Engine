export type User = {
  id: number;
  name: string;
  email: string;
  currency: string;
};
export type Item = {
  id?: number;
  name: string;
  quantity: string;
  unit: string;
  amount: string;
  line_index: number | null;
};
export type Receipt = {
  id: number;
  merchant: string;
  purchase_date: string | null;
  category: string;
  currency: string;
  subtotal: string | null;
  tax: string;
  discount: string;
  fees: string;
  rounding: string;
  total: string | null;
  status: string;
  original_name: string;
  raw_text: string;
  ocr_lines: { text: string; box: number[]; confidence: number }[];
  warnings: string[];
  confidence: number;
  created_at: string;
  items: Item[];
  image_url: string;
  possible_duplicate?: boolean;
};
export type Alert = {
  key: string;
  kind: string;
  title: string;
  evidence: string;
  lines: number[];
  state: string;
};
export type Investigation = {
  alerts: Alert[];
  price_trends: {
    name: string;
    unit: string;
    change: number | null;
    points: { date: string; price: number }[];
  }[];
  match_candidates: {
    item_id: number;
    historical_item_id: number;
    name: string;
    historical_name: string;
    merchant: string;
    date: string;
  }[];
  history_message: string;
  billing_message: string;
  price_message: string;
};
export type Overview = {
  total: string;
  count: number;
  confirmed: number;
  alerts: number;
  currency: string;
  recent: Receipt[];
  scope: string;
};
