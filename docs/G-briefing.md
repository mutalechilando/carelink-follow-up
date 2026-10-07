 Executive Briefing: Mandatory Reporting Field

 Issue

The Ministry has requested a new mandatory reporting field across all 1,500 facilities within two weeks. Engineering estimates six weeks because the change requires database migration, a synchronisation format change that older clients cannot read, and a security review of a new external interface.

The two-week deadline therefore creates material operational and data-integrity risk if the change is deployed as a single national release.

 Options

1. Force a national release in two weeks.  
This meets the requested deadline but creates significant risk: older clients may fail to synchronise, facility databases may become inconsistent, and an incomplete security review could expose sensitive health information. A national failure could disrupt reporting and clinical operations across 1,500 facilities.

2. Reject the deadline and deliver in six weeks.  
This provides the safest engineering path and allows migration, compatibility testing and security review to be completed properly. However, it does not meet the Ministry's reporting requirement and could delay an important programme or regulatory objective.

3. Deliver through a staged, backward-compatible rollout.  
Introduce the field and server capability without requiring older clients to change immediately. Allow old and new versions to operate safely together, pilot with a controlled group of facilities, complete security and migration validation, then progressively activate mandatory reporting nationally.

 Recommendation

I recommend Option 3, treating the two-week date as the deadline for delivering a safe, pilot-ready capability, followed by controlled national activation.

The rollout should have explicit go/no-go criteria covering data integrity, compatibility, security approval, performance and rollback. Feature flags should allow the Ministry to activate the requirement progressively while the remaining facilities are validated.

If the requirement cannot be made backward-compatible and the Ministry insists on mandatory activation at all 1,500 facilities within two weeks, I would escalate the decision rather than bypass migration or security controls. The Ministry should then explicitly choose between changing the deadline/scope and accepting the associated operational and security risk.

This approach preserves the Ministry's urgency while avoiding a national release that could compromise service continuity, data integrity or patient information.