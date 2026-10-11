# Retail X — Security and Access Control Design

## 1. Purpose

This document defines the proposed security architecture and access-control
rules for Retail X. It builds on the user roles and access requirements
documented in M04-03.

The design describes how users should be authenticated, how permissions
should be checked, and how business information should be protected.

**Scope:** Security design documentation. This document does not claim that
the controls described here have already been implemented or deployed.

## 2. Security Objectives

The system should:

- Allow only authenticated users to access protected functions.
- Enforce permissions according to assigned user roles.
- Prevent unauthorised access to administrative functions.
- Protect sales, product, inventory, forecasting and business information.
- Protect user sessions and sensitive configuration.
- Record security-relevant events for investigation and accountability.
- Apply consistent access checks across the dashboard, forecasting,
  restocking and AI assistant features.

## 3. User Roles

### 3.1 Shop Owner / Manager

The Shop Owner / Manager is the primary business user. This role requires
access to normal retail operations, including products, sales, inventory,
dashboards, demand forecasts, restocking recommendations, alerts and the
AI assistant.

### 3.2 Administrator

The Administrator is responsible for authorised user management, role
assignment, permissions and system-level settings.

Administrative privileges should be limited to the responsibilities
necessary for system administration. Administrative actions should be
recorded in an audit log.

## 4. Proposed Security Architecture

The proposed access flow is:

1. The user submits authentication credentials through the application.
2. The authentication component validates the credentials.
3. The system establishes a protected authenticated session.
4. The application identifies the user's assigned role and permissions.
5. The user requests a protected page or operation.
6. The backend checks authentication and authorisation before processing
   the request.
7. The system allows an authorised operation or denies an unauthorised one.
8. Security-relevant events are recorded without exposing passwords,
   session tokens or other secrets.

Authentication alone must not be treated as permission to access every
feature. Authorisation checks must also be applied on the backend.

## 5. Role-Based Access Control

The following matrix reflects the existing M04-03 role requirements.
Permissions should be enforced consistently by the backend.

| Function | Shop Owner / Manager | Administrator |
|---|---|---|
| Sign in and sign out | Allowed | Allowed |
| Manage products | Allowed | Allowed |
| Record sales | Allowed | Allowed |
| View inventory | Allowed | Allowed |
| View sales information | Allowed | Allowed |
| View demand forecasts | Allowed | Allowed |
| View stockout risk | Allowed | Allowed |
| View restocking recommendations | Allowed | Allowed |
| View alerts and dashboard | Allowed | Allowed |
| Use AI assistant and grocery lists | Allowed | Allowed |
| Manage user accounts | Denied | Allowed |
| Assign roles and permissions | Denied | Allowed |
| Manage system-level settings | Denied | Allowed |

**Permission refinement:** Although the existing requirements permit the
Administrator to access business functions, the implementation team should
confirm whether administrators need all business-data permissions or only
the access necessary for support and administration.

## 6. Authentication and Session Security

The design requires the following controls:

- Credentials must be validated by a trusted authentication component.
- Passwords must never be stored in plaintext; a suitable password-hashing
  algorithm must be used if password-based authentication is implemented.
- Authentication errors must not disclose whether a particular account
  exists or reveal sensitive system details.
- Logout must invalidate the authenticated session.
- Sessions must expire according to an agreed inactivity and maximum
  lifetime policy.
- Session identifiers and tokens must not be exposed in URLs or logs.
- Production traffic must use HTTPS.
- Login attempts should be rate-limited to reduce automated guessing.
- Password reset and account recovery must verify the user's authority
  before changing credentials.

Exact session durations and password policies must be agreed before
implementation.

## 7. Authorisation Rules

- Deny access by default when a permission is missing or cannot be verified.
- Enforce permissions on the backend for every protected operation.
- Do not rely only on hidden buttons, frontend routes or interface controls.
- Validate role assignments and permission changes.
- Prevent Shop Owner / Manager accounts from changing their own role or
  granting themselves administrative permissions.
- Recheck permissions after role changes and invalidate affected sessions
  where appropriate.
- Apply the same access policy to API endpoints and AI assistant tools.
- Validate requested resource ownership before returning or changing
  business information.

## 8. Business Data and AI Assistant Protection

Retail X processes business information such as products, sales, stock
levels and forecasts. The following safeguards are proposed:

- Only authorised users may retrieve or modify protected business data.
- Data belonging to one shop must not be exposed to another shop if the
  application supports multiple shops.
- Sensitive configuration and credentials must be stored outside source
  code and excluded from version control.
- AI assistant requests must use the authenticated user's permissions.
- AI-generated responses must not bypass access checks or expose data the
  requesting user is not authorised to view.
- External AI services, if used, should receive only the information needed
  for the requested operation.
- Logs must not contain passwords, access tokens or unnecessary sensitive
  business information.

## 9. Audit Logging and Monitoring

The system should record relevant security events, including:

- Successful and failed login attempts.
- Logout and session expiration events.
- Access-denied events.
- User creation, deactivation and role changes.
- Changes to security-sensitive settings.
- Other privileged administrative operations.

Each event should record the timestamp, event type, outcome and relevant
actor identifier where available. Logs must be access-controlled and
protected against unauthorised modification.

Secrets, passwords and complete session tokens must never be written to
audit logs. Log retention and monitoring procedures must be defined before
deployment.

## 10. Threats and Mitigations

| Threat | Proposed mitigation |
|---|---|
| Unauthorised account access | Secure authentication, rate limiting and protected recovery |
| Privilege escalation | Backend permission checks and restricted role management |
| Direct API access bypassing the UI | Server-side authorisation on every protected operation |
| Session theft or misuse | HTTPS, protected session storage, expiry and logout invalidation |
| Exposure of business information | Access checks, resource ownership validation and data minimisation |
| AI assistant information leakage | Permission-aware tool access and restricted context |
| Abuse of administrator privileges | Least privilege, audit logging and review of privileged actions |
| Secrets committed to source control | Environment-based configuration and secret-management controls |

## 11. Verification and Acceptance Criteria

The design should be verified against the following criteria before the
security controls are accepted for implementation:

| ID | Verification | Expected result |
|---|---|---|
| SEC-01 | Request a protected resource without signing in | Access is denied |
| SEC-02 | Attempt to open an administrative function as Shop Owner / Manager | Access is denied |
| SEC-03 | Access an allowed business function as Shop Owner / Manager | Access is granted |
| SEC-04 | Access an allowed user-management function as Administrator | Access is granted |
| SEC-05 | Attempt a protected operation directly through an API | Backend permissions are enforced |
| SEC-06 | Sign out and reuse the previous session | The old session is rejected |
| SEC-07 | Attempt to access another shop's data, where applicable | Unauthorised access is denied |
| SEC-08 | Review security logs after denied access and role changes | Relevant events are recorded without secrets |
| SEC-09 | Inspect AI assistant tool permissions | Tools enforce the user's permissions |
| SEC-10 | Inspect repository and application configuration | No live credentials or tokens are committed |

These are proposed acceptance tests. They must be executed against the
implemented system when the relevant authentication and authorisation
features are available.

## 12. Evidence and Traceability

This design supports the following requirements from M04-03:

- AR-01 — User Authentication
- AR-02 — Role Identification
- AR-03 — Role-Based Access
- AR-04 — Restricted Functions
- AR-05 — Business Data Protection
- AR-06 — Session Security
- AR-07 — Administrative Access
- AR-08 — Access Consistency

Evidence for M06-05 will include this design document, the security
architecture diagram, a review of the documented role permissions and
verification criteria, and the Git commit and pull request associated
with Issue #32.

## 13. Limitations and Implementation Dependencies

This document defines a proposed design; it is not evidence of a completed
security implementation or a penetration test.

Implementation requires confirmation of the authentication technology,
session policy, deployment configuration, business-data ownership model,
AI integration boundaries and audit-log retention policy.

The implementation team should review this design alongside the
application architecture before developing or deploying security controls.

## 14. Conclusion

The proposed security design establishes authentication, role-based
authorisation, protected sessions, business-data safeguards, audit logging
and testable acceptance criteria for Retail X.

These controls provide a basis for subsequent implementation and verification
while preserving the distinction between documented design and working
security functionality.
