import type { ApiError } from '../types/followUp'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

export class ApiRequestError extends Error {
  code: string
  correlationId: string

  constructor(error: ApiError['error']) {
    super(error.message)
    this.name = 'ApiRequestError'
    this.code = error.code
    this.correlationId = error.correlation_id
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Token ${
        import.meta.env.VITE_API_TOKEN ?? 'district-chembe'
      }`,
      ...options.headers,
    },
  })

  if (!response.ok) {
    let errorBody: ApiError | null = null

    try {
      errorBody = (await response.json()) as ApiError
    } catch {
      // The server returned a non-JSON error.
    }

    if (errorBody?.error) {
      throw new ApiRequestError(errorBody.error)
    }

    throw new Error(
      `Request failed with status ${response.status}.`,
    )
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}