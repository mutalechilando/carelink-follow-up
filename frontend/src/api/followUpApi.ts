import { apiRequest } from './client'
import type {
  FollowUpResponse,
  FollowUpStatus,
  SortOption,
} from '../types/followUp'

interface GetFollowUpsParams {
  facilityId?: string
  status: FollowUpStatus
  overdueDays: number
  sort: SortOption
  page: number
  pageSize: number
}

export async function getFollowUps(
  params: GetFollowUpsParams,
): Promise<FollowUpResponse> {
  const searchParams = new URLSearchParams({
    status: params.status,
    overdue_days: String(params.overdueDays),
    sort: params.sort,
    page: String(params.page),
    page_size: String(params.pageSize),
  })

  if (params.facilityId) {
    searchParams.set('facility_id', params.facilityId)
  }

  return apiRequest<FollowUpResponse>(
    `/api/follow-up?${searchParams.toString()}`,
  )
}

export async function recordFollowUpContact(
  patientId: number,
  contactedAt: string,
  note: string,
): Promise<void> {
  await apiRequest<void>(
    `/api/follow-up/${patientId}/contacted`,
    {
      method: 'POST',
      body: JSON.stringify({
        contacted_at: contactedAt,
        note,
      }),
    },
  )
}