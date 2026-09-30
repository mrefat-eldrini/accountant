# Release Notes

## v0.4.0 — 2026-09-30

### Added
- Administration section available only to Admin users.
- Audit Log with user, action, module, reference, details, timestamp, and IP address.
- System Log and System Status page.
- Full application backup download in portable JSON format.
- Admin-only restore from validated Accountant Pro backup.
- Company Settings for company name, currency, VAT rate, fiscal-year start, and backup retention days.
- Audit events for login success/failure, logout, user management, password reset, accounting record creation, backup, restore, and settings changes.
- Viewer role is now explicitly read-only for accounting write operations.
- Dynamic application currency display from Company Settings.
- Automated permission tests for Admin and Viewer.
- Automated backup creation and restore test.

### Security / Permissions
- Backup, restore, system logs, audit logs, settings, and user management are restricted to Admin.
- Accountant can perform accounting operations but cannot access Administration.
- Viewer can view accounting screens but cannot create accounting records or access Administration.
- Password values are never written to audit logs.
- Restore requires an explicit confirmation and records a restore audit event.

### Backup Scope
The portable backup currently includes:
- Users
- Chart of Accounts
- Customers
- Vendors
- Transactions
- Invoices
- Expenses
- Journal Entries
- Company Settings

Audit and system logs are intentionally preserved during restore so the restore event itself remains traceable.

### Release Engineering
- `develop` was synchronized to the current `main` release before v0.4.0 promotion to prevent branch-history drift.

### Verification Results
- Initial behavioral CI detected a failing role-navigation assertion; the test was corrected because translation text caused a false positive.
- Corrected feature CI: **PASSED** — GitHub Actions run `36766125265`.
- Develop local CI after v0.4.0 promotion: **PASSED** — run `36766186886`.
- Deployed-environment verification PR CI: **PASSED** — run `36766481730`.
- Final develop CI including actual Render staging verification: **PASSED** — run `36766551199`.
- Render staging deploy: **LIVE** — `dep-daum8dm7bikc73cunnlg`.
- Staging commit: `1ff54e54e55a20ef6ee0d5db1fc0d17b18090d1c`.
- Actual deployed staging smoke test verified:
  - Health/version endpoint
  - Admin navigation and all Administration pages
  - Dashboard and all primary accounting routes
  - Authenticated access to the deployed Render application

### Production Gate
Production promotion is allowed only after the release pull request passes CI. After merge, the main-branch workflow waits for Render production to report version 0.4.0 and then executes the authenticated remote smoke test against the real production URL.

### Known Infrastructure Item
- The application remains compatible with PostgreSQL via `DATABASE_URL`, but the Render web services are still using the local SQLite fallback until the managed PostgreSQL connection is attached.

## v0.3.1 — 2026-09-30

### Added
- Formal branch-based release process documentation.
- GitHub Actions CI for pull requests and pushes to `develop` and `main`.
- Automated application startup test.
- Automated authenticated smoke-test suite covering:
  - Health endpoint
  - Login page
  - Authentication
  - Dashboard
  - Transactions
  - Invoices
  - Expenses
  - Customers
  - Vendors
  - Chart of Accounts
  - Journal
  - Reports
  - User Management
- Persistent repository release notes.

### Verification
- Feature-branch CI run: **PASSED**.
- Workflow: `CI and Smoke Tests`.
- GitHub Actions run: `36763051178`.
- Develop-branch CI run: **PASSED**.
- Develop GitHub Actions run: `36763252335`.
- Syntax check: passed.
- Application startup: passed.
- Authenticated route smoke tests: passed.
- Render staging deploy: **LIVE**.
- Staging deploy ID: `dep-daulr9e7bikc73cteuag`.
- Staging commit: `e318746386f323a93ee35d20de83392467823523`.
- Release PR CI: **PASSED**.
- Release GitHub Actions run: `36763458185`.
- Main-branch CI after merge: **PASSED**.
- Main GitHub Actions run: `36763519520`.
- Production release commit: `bf672e920b993b4ad807362b85e4758cc47f5b97`.
- Production Render deploy: `dep-daulsis1nsns73eq8b1g`.
- Production deploy status: **LIVE**.
- Production root request returned the expected HTTP 303 redirect to login.
- Production login page returned HTTP 200 after deployment.
- Render reported the production service live at `https://accountant-b7hw.onrender.com`.

### Release Policy
A change is not promoted to `main` until:
1. Feature-branch CI passes.
2. It is merged into `develop`.
3. Render staging deploys successfully.
4. Staging startup/log verification passes.
5. Release PR to `main` passes CI.
6. Production deployment is live and production routes are verified.

## v0.3.0 — 2026-09-30

### Added
- Persistent Dark and Light themes.
- English and Arabic language switching with RTL/LTR support.
- Production-style dark/gold UI redesign.
- Admin user-management editing for name, email, role, and status.
- Password change from the user-management screen.
- Secure temporary password reset generation.
- Duplicate-email validation with a clean UI message.
- Staging environment on Render using the `develop` branch.
- Branch-based release workflow.

### Changed
- User role is no longer shown in the top-right header.
- Production changes are promoted through feature branch → develop → staging → main.
- User-management UI now supports Active / Disabled state.

### Deployment
- Staging: https://accountant-staging.onrender.com
- Production: https://accountant-b7hw.onrender.com
- Production release commit: `7160f7a3e97133e782ea46fb378e9f07f7eda83c`

### Verification
- Staging build completed successfully and application startup completed.
- Production build completed successfully and Render reported the service live.
- Production request logs returned HTTP 200 for:
  - Dashboard
  - Transactions
  - Invoices
  - Expenses
- Login route returned HTTP 200.
- Root unauthenticated access redirected to login as expected.

### Known Production Infrastructure Item
- The application is still using the local SQLite fallback until `DATABASE_URL` is connected to the managed Render PostgreSQL service.
