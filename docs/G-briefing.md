 Executive Briefing: Mandatory Reporting Field

 Issue

The Ministry has requested a new mandatory reporting field across all 1,500 facilities within two weeks. Engineering estimates six weeks because the change requires database migration, a synchronisation format change that older clients cannot read, and a security review of a new external interface.

The two-week deadline therefore creates a material operational and data-integrity risk if the change is deployed as a single national release.

 Options

1. Force a national release in two weeks.  
This meets the requested deadline, but creates significant risk: older clients may fail to synchronise, facility databases may become inconsistent, and an uncompleted security review could expose sensitive health information. A national failure would be difficult to recover from and could disrupt reporting across 1,500 facilities.

2. Reject the deadline and deliver in six weeks.  
This provides the safest engineering path and allows migration, compatibility testing and security review to be completed properly. However, it does not meet the Ministry's reporting requirement and may delay an important programme or regulatory objective.

3. Deliver through a staged, backward-compatible rollout.  
Introduce the field and server-side capability first without making older clients depend on it. Use a compatibility layer/versioned synchronisation format so existing clients continue operating. Pilot with a controlled group of facilities, complete the security review and migration validation, then progressively enable mandatory reporting nationally.

 Recommendation

I recommend Option 3, with the two-week requirement treated as the deadline for making the new reporting capability available, not for forcing an unsafe national activation.

The rollout should have explicit go/no-go criteria covering data integrity, synchronisation compatibility, security approval, performance and rollback. A pilot should begin as soon as the first safe version is available, with feature flags allowing the Ministry to activate the requirement progressively.

If the new requirement cannot be made backward-compatible and the Ministry insists on mandatory activation at all 1,500 facilities within two weeks, I would escalate the decision rather than bypass the migration or security controls. The Ministry should then choose explicitly between changing the deadline/scope and accepting the operational and security risk.

This approach preserves the Ministry's urgency while avoiding a national release that could compromise service continuity, data integrity or patient information.