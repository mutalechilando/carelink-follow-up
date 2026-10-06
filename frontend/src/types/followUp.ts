export type FollowUpStatus =
  | 'overdue'
  | 'due_soon'
  | 'recently_missed'

export type SortOption = 'days_overdue' | '-days_overdue'

export interface FollowUpPatient {
  id: number
  patient_number: string
  first_name: string
  last_name: string
  facility_id: string
  facility_name: string
  missed_appointment_date: string
  days_overdue: number
  follow_up_status: FollowUpStatus
  phone_number: string
  last_contact_attempt: string | null
}

export interface Pagination {
  page: number
  page_size: number
  total: number
  total_pages: number
}

export interface FollowUpResponse {
  results: FollowUpPatient[]
  pagination: Pagination
}

export interface ApiError {
  error: {
    code: string
    message: string
    correlation_id: string
  }
}