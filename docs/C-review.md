 CareLink Follow-Up — Code Review

 1. Review approach

I reviewed both extracts against five production concerns: patient confidentiality, clinical data integrity, reliability, scalability and accessibility in the clinic environment.

I have ranked each finding as:

- Critical — must be addressed before merge because it could cause serious security, clinical-data or availability consequences.
- Major — significant operational, scalability or maintainability risk that should normally be addressed before production.
- Minor — worthwhile improvement that does not by itself block the immediate merge.

The practical question throughout the review is: what could this failure mean to a clinic or patient?



 2. C1 — Back-end PatientService

 C1.1 Hard-coded database credentials

Severity: Critical


private static string ConnString =
"Server=10.20.1.14;Database=carelink;User Id=sa;Password=CareLink#2024;";


 Problem

A privileged database credential is hard-coded in source code, including use of the SQL sa account.

 Practical clinic risk

If the source code or deployed application is compromised, an attacker could obtain powerful database credentials and potentially read, modify or delete national patient information.

It also makes password rotation and separating development/test/production environments unsafe.

 Required action

Use environment-specific configuration/secrets management and a least-privilege application database account. Never commit production credentials to source control.



 C1.2 SQL injection in patient search

Severity: Critical


var sql = "SELECT * FROM patient WHERE facility_id = '" + facility +
"' AND (first_name LIKE '%" + q + "%' OR last_name LIKE '%" + q + "%')";


 Problem

User-controlled `facility` and `q` values are concatenated directly into SQL.

 Practical clinic risk

A malicious search value could alter the query and potentially bypass intended filtering or expose records outside the user's authorised scope. The broader risk is amplified because the application is using a highly privileged database account.

 Required action

Use parameterised queries or the ORM:


WHERE facility_id = @facility
AND (first_name LIKE @q OR last_name LIKE @q)


Also enforce authorisation separately from the query parameter.



 C1.3 No explicit authorisation check

Severity: Critical

The method accepts:


string userRole


but never uses it to determine whether the user is allowed to access the requested facility.

 Practical clinic risk

A clinician could potentially change:


facility=FAC-0207


and retrieve another facility's patients.

This is a direct confidentiality risk.

 Required action

Derive the user's facility/district scope from the authenticated identity on the server. Never trust a facility supplied by the browser as proof of authorisation.



 C1.4 National ID is written to application logs

Severity: Critical


Log.Info("search by " + userRole + " q=" + q + " first=" +
(results.Count > 0 ? results[0].NationalId : ""));


 Problem

The code logs a sensitive patient identifier and also logs the search term.

 Practical clinic risk

Operational staff, log aggregation systems or compromised logging infrastructure could gain access to patient identifiers outside the clinical workflow.

 Required action

Use correlation IDs, user IDs, facility IDs and operation IDs for troubleshooting. Do not log unnecessary PHI.



 C1.5 Database connection is not disposed

Severity: Major


var conn = new SqlConnection(ConnString);
conn.Open();


The connection is not wrapped in `using`/`finally`.

 Practical clinic risk

Repeated searches could consume database connections. Under a busy clinic or national morning peak, users could eventually experience slow searches or database connection failures.

 Required action

Use deterministic connection disposal and appropriate connection pooling.



 C1.6 `SaveEncounter` swallows every exception

Severity: Critical


catch (Exception ex) {
// ignore
}


 Problem

The method can fail without informing the caller or recording a useful diagnostic event.

 Practical clinic risk

A clinician could believe an encounter was saved when it was not. This creates a particularly dangerous failure mode: the UI may report success while the clinical record is missing.

 Required action

Catch expected exceptions, roll back failed transactions, return a meaningful error and log diagnostics using a correlation ID without PHI.



 C1.7 Encounter insert and patient update are not transactional

Severity: Critical

The method performs:


INSERT encounter
UPDATE patient


as two independent database operations.

 Practical clinic risk

The encounter could be saved while updating the patient's `last_visit_date` fails, leaving the patient's summary inconsistent with the encounter history.

The reverse can also become problematic if the implementation changes.

 Required action

Use a database transaction so the operations succeed or fail together.



 C1.8 SQL is also constructed unsafely in `SaveEncounter`

Severity: Critical


"INSERT INTO encounter ... " +
e.PatientId + ", '" + e.VisitDate + "', '" + e.Notes + "')"


and:


"UPDATE patient SET last_visit_date = '" + e.VisitDate +
"' WHERE id = " + e.PatientId


 Practical clinic risk

A malicious or unexpected clinical note could break the SQL statement or potentially be interpreted as SQL. Apart from security implications, an apostrophe in a legitimate note could cause a save to fail.

 Required action

Use parameterised commands.



 C1.9 `DueForFollowUp` creates an N+1 query pattern

Severity: Major


var all = Search("", facility, "system");

foreach (var p in all) {
    foreach (var v in GetVisits(p.Id)) {


 Problem

The code first loads patients and then calls `GetVisits()` separately for every patient.

 Practical clinic risk

A facility with thousands of patients could generate thousands of database queries for one worklist request. The follow-up screen could become very slow or time out during busy periods.

 Required action

Calculate follow-up eligibility in the database using joins/subqueries and indexes, with server-side pagination.



 C1.10 Follow-up logic does not match the required clinical rule

Severity: Major

The code checks:


if (v.NextAppointmentDate < DateTime.Now)


but does not establish that the appointment belongs to the patient's most recent relevant visit or that there has been no later visit since the missed appointment.

 Practical clinic risk

A patient who has already returned to the clinic could incorrectly appear on the follow-up list. Staff may waste time contacting patients who no longer require follow-up.

 Required action

Define and implement the business rule explicitly:

> The patient's most recent visit set the appointment date, the appointment is sufficiently overdue, and there has been no visit since that appointment.



 C1.11 No pagination or result limit

Severity: Major

`Search` returns every matching patient.

 Practical clinic risk

A broad search could return thousands of records, increasing database load, network traffic and browser memory usage.

 Required action

Use server-side pagination and sensible maximum page sizes.



 3. C2 — Front-end FollowUpList

 C2.1 `any` removes type safety

Severity: Major

typescript
export function FollowUpList(props: any)
const [patients, setPatients] = useState<any>([])


 Practical clinic risk

Backend changes or malformed responses can cause runtime errors that are only discovered when clinicians use the system.

 Required action

Define explicit TypeScript interfaces for API requests/responses and patient records.



 C2.2 API calls are made directly from the component

Severity: Major

typescript
fetch('/api/follow-up?facility=' + facility)


 Problem

Networking, error handling and presentation are tightly coupled.

 Practical clinic risk

When connectivity is unreliable, every screen has to implement its own retry/error/authentication behaviour. This leads to inconsistent handling of failures.

 Required action

Use a typed API/service layer with central authentication and error handling.



 C2.3 HTTP failures are treated as successful responses

Severity: Major

typescript
.then(r => r.json())
.then(d => { setPatients(d); setLoading(false); });


There is no check for `r.ok`.

 Practical clinic risk

A 401, 403 or 500 response may be interpreted as patient data. The screen can fail confusingly instead of telling the clinician that the request failed.

 Required action

Check HTTP status and convert API errors into a consistent UI error state.



 C2.4 The polling effect has no dependency array

Severity: Major

typescript
useEffect(() => {
    const t = setInterval(...)
    return () => clearInterval(t);
});


 Problem

The interval is recreated after every render, producing unnecessary setup/teardown and potentially changing the timing of polling; combined with other state updates, this can create excessive request activity and unpredictable polling behaviour.

 Practical clinic risk

One clinic computer could generate an increasing number of API requests. Across hundreds or thousands of users this could create substantial unnecessary national traffic and database load.

 Required action

If polling is actually required, give it a controlled dependency array and interval. For this workflow, explicit refresh or a much less aggressive refresh strategy would be preferable.



 C2.5 Three-second polling is unnecessarily aggressive

Severity: Major

typescript
setInterval(..., 3000)


 Practical clinic risk

Thousands of users could collectively generate a large number of requests every few seconds even when no follow-up data has changed.

This consumes network capacity at intermittent facilities and database/application capacity nationally.

 Required action

Use event-driven invalidation where justified, or a modest refresh interval. Refresh after a successful write.



 C2.6 Sorting mutates React state

Severity: Critical

typescript
patients.sort(...)
setPatients(patients)


 Problem

`.sort()` mutates the existing state array.

 Practical clinic risk

The component can enter unpredictable render behaviour and can display stale or incorrectly ordered patient information.

 Required action

Treat state as immutable and preferably perform sorting server-side:

typescript
const sorted = [...patients].sort(...)


For this application, the API should own sorting.



 C2.7 The component creates a state-update/render loop

Severity: Critical

typescript
useEffect(() => {
    patients.sort(...)
    setPatients(patients);
}, [patients]);


 Problem

The effect depends on `patients` and calls `setPatients()` whenever `patients` changes.

 Practical clinic risk

This creates an unnecessary state-update cycle and risks repeated renders; the sorting should not be implemented as an effect. Combined with the polling effect, it can significantly increase network and CPU activity.

 Required action

Remove the effect entirely and request the desired ordering from the API.



 C2.8 Filtering is client-side

Severity: Major

typescript
const visible = patients.filter(...)


 Practical clinic risk

If the API returns only a subset of a 10,000+ patient worklist, the clinician can search only the records currently loaded into the browser.

If the application downloads everything instead, it creates unnecessary memory, bandwidth and PHI exposure.

 Required action

Perform filtering/search server-side with pagination.



 C2.9 Array index is used as the React key

Severity: Major

typescript
key={i}


 Practical clinic risk

After sorting or filtering, React may associate UI state with the wrong patient row.

 Required action

Use a stable patient/record identifier.



 C2.10 Patient object is mutated directly

Severity: Major

typescript
p.contacted = true;


 Practical clinic risk

React may not re-render correctly, leaving the clinician with a screen that does not accurately reflect the contact action.

 Required action

Update state immutably after the server confirms success.



 C2.11 Contact result is not checked

Severity: Major

typescript
fetch('/api/follow-up/' + p.id + '/contacted', { method: 'POST' });


 Problem

The code does not wait for or check the result.

 Practical clinic risk

A clinician may click "mark contacted", receive no indication that the save failed, and continue assuming the patient was recorded as contacted.

 Required action

Await the request, check the response, display failure/retry state and only update the UI after successful persistence.



 C2.12 No authentication is visible

Severity: Critical

No authentication context or authenticated API client is visible in this component. The review therefore requires confirmation that authentication and authorisation are enforced centrally rather than assuming the client is trusted.

 Practical clinic risk

If the backend does not enforce this independently, patient data could be exposed across facilities.

 Required action

Use the central authenticated API client and enforce server-side authorisation.



 C2.13 Accessibility depends on a clickable `div`

Severity: Major

tsx
<div onClick={() => markContacted(p)}>
    mark contacted
</div>


 Problem

A `div` is not keyboard-operable by default and does not communicate button semantics to assistive technology.

 Practical clinic risk

A keyboard-only clinician may be unable to record the follow-up action.

 Required action

Use:

tsx
<button type="button">
    Mark contacted
</button>


with an accessible name.



 C2.14 Status is communicated using colour alone

Severity: Major

tsx
style={{ color: p.days_overdue > 30 ? 'red' : 'black' }}


 Practical clinic risk

Users who cannot distinguish the colours may not recognise which patients are significantly overdue.

 Required action

Use text such as "31 days overdue" or an explicit status badge, with colour used only as an additional visual cue.



 C2.15 No loading/error/empty distinction for refresh failures

Severity: Major

The initial request manages `loading`, but subsequent polling does not provide a meaningful error state.

 Practical clinic risk

The clinician may continue seeing old data without knowing that the system can no longer retrieve current information.

 Required action

Show the last successful sync/request time and distinguish stale data from current data.



 4. Three Issues I Require Fixed Before Merge

Although there are many issues, I would make these three merge blockers:

 1. Security and authorisation

Fix SQL injection, remove hard-coded database credentials, stop logging PHI, and enforce server-side facility/role authorisation.

Why: A national EHR cannot be merged with a known path to unauthorised patient access.

 2. Clinical data integrity

Make `SaveEncounter` transactional, parameterised and observable. Never swallow exceptions.

Why: A clinician must never be told or left to assume that a clinical record was saved when it was not.

 3. Follow-up scalability and correctness

Replace the N+1/client-side approach with a database-backed, paginated query implementing the actual follow-up rule.

Why: The supplied implementation will not reliably support 10,000+ patient lists or national concurrency, and incorrect follow-up eligibility can waste clinical staff time.

The frontend polling/render-loop issues would also be fixed immediately as part of the same workstream, but the three above are my formal merge blockers.



 5. Refactor — C1 PatientService

 Why I chose C1

I chose the backend extract because it contains the highest-risk combination of problems:

1. SQL injection and privileged hard-coded credentials;
2. silent failure of clinical writes;
3. lack of transactionality between related clinical updates.

These can directly affect patient confidentiality and the correctness of clinical records, so they are more important to address than simply restructuring the frontend.

I would not attempt to rewrite the entire service in this refactor.

 Refactored extract

The following is representative C-style pseudocode showing the intended pattern.

public class PatientService
{
    private readonly string _connectionString;

    public PatientService(IConfiguration config)
    {
        _connectionString =
            config.GetConnectionString("CareLink")
            ?? throw new InvalidOperationException(
                "CareLink database configuration is missing.");
    }

    public List<Patient> Search(
        string q,
        string facility,
        UserContext user)
    {
        if (!user.CanReadFacility(facility))
        {
            throw new ForbiddenException();
        }

        using var conn = new SqlConnection(_connectionString);
        conn.Open();

        const string sql = @"
            SELECT id, patient_number, first_name, last_name,
                   national_id, facility_id
            FROM patient
            WHERE facility_id = @facility
              AND (
                    first_name LIKE @query
                    OR last_name LIKE @query
                  )
            ORDER BY last_name, first_name
            OFFSET @offset ROWS
            FETCH NEXT @pageSize ROWS ONLY";

        using var cmd = new SqlCommand(sql, conn);

        cmd.Parameters.AddWithValue("@facility", facility);
        cmd.Parameters.AddWithValue("@query", $"%{q}%");
        cmd.Parameters.AddWithValue("@offset", 0);
        cmd.Parameters.AddWithValue("@pageSize", 50);

        using var reader = cmd.ExecuteReader();

        var results = new List<Patient>();

        while (reader.Read())
        {
            results.Add(Map(reader));
        }

        Log.Info(
            "Patient search completed. " +
            "UserId={UserId}, Facility={Facility}, ResultCount={Count}",
            user.Id,
            facility,
            results.Count);

        return results;
    }

    public void SaveEncounter(
        Encounter e,
        UserContext user,
        string correlationId)
    {
        if (!user.CanWriteFacility(e.FacilityId))
        {
            throw new ForbiddenException();
        }

        using var conn = new SqlConnection(_connectionString);
        conn.Open();

        using var transaction = conn.BeginTransaction();

        try
        {
            const string insertEncounter = @"
                INSERT INTO encounter
                    (patient_id, visit_date, notes)
                VALUES
                    (@patientId, @visitDate, @notes)";

            using var encounterCommand =
                new SqlCommand(
                    insertEncounter,
                    conn,
                    transaction);

            encounterCommand.Parameters.AddWithValue(
                "@patientId",
                e.PatientId);

            encounterCommand.Parameters.AddWithValue(
                "@visitDate",
                e.VisitDate);

            encounterCommand.Parameters.AddWithValue(
                "@notes",
                e.Notes);

            encounterCommand.ExecuteNonQuery();

            const string updatePatient = @"
                UPDATE patient
                SET last_visit_date = @visitDate
                WHERE id = @patientId";

            using var patientCommand =
                new SqlCommand(
                    updatePatient,
                    conn,
                    transaction);

            patientCommand.Parameters.AddWithValue(
                "@visitDate",
                e.VisitDate);

            patientCommand.Parameters.AddWithValue(
                "@patientId",
                e.PatientId);

            patientCommand.ExecuteNonQuery();

            transaction.Commit();
        }
        catch (Exception ex)
        {
            transaction.Rollback();

            Log.Error(
                ex,
                "Failed to save encounter. " +
                "CorrelationId={CorrelationId}, " +
                "PatientId={PatientId}",
                correlationId,
                e.PatientId);

            throw;
        }
    }
}


 What this refactor fixes

It specifically addresses the most serious problems without attempting to redesign the whole service:

- credentials come from configuration/secrets rather than source code;
- database connections are disposed;
- SQL parameters prevent injection;
- facility access is checked against the authenticated user;
- patient searches are paginated;
- PHI is removed from routine logging;
- encounter creation and patient update occur in one transaction;
- failures are rolled back and surfaced to the caller;
- a correlation ID is available for operational troubleshooting.

The complete `DueForFollowUp` implementation would then be refactored separately into a database-side query using the actual CareLink follow-up business rule, with appropriate indexes and pagination.



 6. Overall Recommendation

The code demonstrates the intended business workflow, but I would not merge it as supplied.

The safest path is not a wholesale rewrite. I would preserve the business behaviour while addressing the security and clinical-integrity blockers first, then replace the inefficient follow-up query and frontend polling/render behaviour.

The standard I would apply is:

> A clinic should never lose a clinical write, expose another facility's patients, or be given the impression that stale or failed data is current.