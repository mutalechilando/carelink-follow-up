import type { FollowUpStatus } from '../types/followUp'

interface StatusBadgeProps {
  status: FollowUpStatus
}

const labels: Record<FollowUpStatus, string> = {
  overdue: 'Overdue',
  due_soon: 'Due soon',
  recently_missed: 'Recently missed',
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={`status-badge status-badge--${status}`}
      aria-label={`Follow-up status: ${labels[status]}`}
    >
      {labels[status]}
    </span>
  )
}