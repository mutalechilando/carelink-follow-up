import { useCallback, useEffect, useState } from 'react'
import { getFollowUps,
    recordFollowUpContact,
 } from '../api/followUpApi'
import { StatusBadge } from '../components/StatusBadge'
import { ContactDialog } from '../components/ContactDialog'
import type {
  FollowUpPatient,
  FollowUpStatus,
  SortOption,
} from '../types/followUp'

const PAGE_SIZE = 25

const facilities = [
  { id: '', name: 'All facilities' },
  { id: 'FAC-0101', name: 'Mwansa Urban Clinic' },
  { id: 'FAC-0207', name: 'Kalemba Rural Health Centre' },
  { id: 'FAC-0312', name: 'Chembe District Hospital' },
]

const statuses: Array<{
  value: FollowUpStatus
  label: string
}> = [
  { value: 'overdue', label: 'Overdue' },
  { value: 'due_soon', label: 'Due soon' },
  { value: 'recently_missed', label: 'Recently missed' },
]

export function FollowUpPage() {
  const [patients, setPatients] = useState<FollowUpPatient[]>([])
  const [status, setStatus] = useState<FollowUpStatus>('overdue')
  const [facilityId, setFacilityId] = useState('')
  const [contactPatient, setContactPatient] = useState<FollowUpPatient | null>(null)
  const [sort, setSort] = useState<SortOption>('days_overdue')
  const [page, setPage] = useState(1)

  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadFollowUps = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await getFollowUps({
        facilityId: facilityId || undefined,
        status,
        overdueDays: 7,
        sort,
        page,
        pageSize: PAGE_SIZE,
      })

      setPatients(response.results)
      setTotal(response.pagination.total)
      setTotalPages(response.pagination.total_pages)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load follow-up patients.',
      )
    } finally {
      setLoading(false)
    }
  }, [facilityId, status, sort, page])

  const handleContactSubmit = async (
    contactedAt: string,
    note: string,
  ) => {
    if (!contactPatient) {
      return
    }
  
    await recordFollowUpContact(
      contactPatient.id,
      contactedAt,
      note,
    )
  
    await loadFollowUps()
  }

  useEffect(() => {
    void loadFollowUps()
  }, [loadFollowUps])

  function handleStatusChange(
    event: React.ChangeEvent<HTMLSelectElement>,
  ) {
    setStatus(event.target.value as FollowUpStatus)
    setPage(1)
  }

  function handleFacilityChange(
    event: React.ChangeEvent<HTMLSelectElement>,
  ) {
    setFacilityId(event.target.value)
    setPage(1)
  }

  function handleSortChange(
    event: React.ChangeEvent<HTMLSelectElement>,
  ) {
    setSort(event.target.value as SortOption)
    setPage(1)
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">CareLink EHR</p>
          <h1>Follow-up Worklist</h1>
          <p className="page-description">
            Patients requiring follow-up based on missed appointments.
          </p>
        </div>

        <div className="header-context" aria-label="Current reporting period">
          <span>As of</span>
          <strong>6 October 2026</strong>
        </div>
      </header>

      <section className="filters" aria-labelledby="filter-heading">
        <h2 id="filter-heading">Filter follow-ups</h2>

        <div className="filter-grid">
          <div className="form-field">
            <label htmlFor="facility">Facility</label>
            <select
              id="facility"
              value={facilityId}
              onChange={handleFacilityChange}
            >
              {facilities.map((facility) => (
                <option key={facility.id} value={facility.id}>
                  {facility.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="status">Status</label>
            <select
              id="status"
              value={status}
              onChange={handleStatusChange}
            >
              {statuses.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="sort">Sort</label>
            <select
              id="sort"
              value={sort}
              onChange={handleSortChange}
            >
              <option value="days_overdue">
                Most overdue first
              </option>
              <option value="-days_overdue">
                Least overdue first
              </option>
            </select>
          </div>
        </div>
      </section>

      <section
        className="worklist"
        aria-labelledby="worklist-heading"
        aria-live="polite"
      >
        <div className="section-heading">
          <div>
            <h2 id="worklist-heading">Patients</h2>
            <p>
              {total} {total === 1 ? 'patient' : 'patients'} found
            </p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={() => void loadFollowUps()}
            disabled={loading}
          >
            {loading ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>

        {loading && (
          <div className="state-panel" role="status">
            <strong>Loading follow-up patients…</strong>
            <span>Please wait while the worklist is retrieved.</span>
          </div>
        )}

        {!loading && error && (
          <div className="state-panel state-panel--error" role="alert">
            <strong>Unable to load the worklist</strong>
            <span>{error}</span>
            <button
              type="button"
              className="primary-button"
              onClick={() => void loadFollowUps()}
            >
              Try again
            </button>
          </div>
        )}

        {!loading && !error && patients.length === 0 && (
          <div className="state-panel">
            <strong>No patients require follow-up.</strong>
            <span>
              Try changing the facility or status filters.
            </span>
          </div>
        )}

        {!loading && !error && patients.length > 0 && (
          <>
            <div className="table-wrapper">
              <table>
                <caption className="sr-only">
                  Follow-up patients
                </caption>

                <thead>
                  <tr>
                    <th scope="col">Patient</th>
                    <th scope="col">Facility</th>
                    <th scope="col">Missed appointment</th>
                    <th scope="col">Days overdue</th>
                    <th scope="col">Status</th>
                    <th scope="col">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {patients.map((patient) => (
                    <tr key={patient.id}>
                      <td>
                        <strong>
                          {patient.first_name} {patient.last_name}
                        </strong>
                        <span className="secondary-text">
                          {patient.patient_number}
                        </span>
                      </td>

                      <td>
                        <strong>{patient.facility_name}</strong>
                        <span className="secondary-text">
                          {patient.facility_id}
                        </span>
                      </td>

                      <td>{patient.missed_appointment_date}</td>

                      <td>
                        <strong>{patient.days_overdue}</strong>
                      </td>

                      <td>
                        <StatusBadge
                          status={patient.follow_up_status}
                        />
                      </td>

                      <td>
                        <button
                          type="button"
                          className="button button--primary"
                          onClick={() => setContactPatient(patient)}
                        >
                          Contact
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <nav
                className="pagination"
                aria-label="Follow-up pagination"
              >
                <button
                  type="button"
                  className="secondary-button"
                  disabled={page === 1}
                  onClick={() => setPage((current) => current - 1)}
                >
                  Previous
                </button>

                <span>
                  Page {page} of {totalPages}
                </span>

                <button
                  type="button"
                  className="secondary-button"
                  disabled={page === totalPages}
                  onClick={() => setPage((current) => current + 1)}
                >
                  Next
                </button>
              </nav>
            )}

            {contactPatient && (
              <ContactDialog
                patientName={`${contactPatient.first_name} ${contactPatient.last_name}`}
                onClose={() => setContactPatient(null)}
                onSubmit={handleContactSubmit}
              />
            )}
          </>
        )}
      </section>
    </main>
  )
}