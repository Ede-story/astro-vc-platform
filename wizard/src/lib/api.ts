import { CalculateRequest, CalculateResponse } from '@/types/astro';

// API Base URL - uses environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://star-meet.com/star-api';

/**
 * Fetch chart calculation from StarMeet API
 */
export async function fetchCalculation(data: CalculateRequest): Promise<CalculateResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Health check
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
