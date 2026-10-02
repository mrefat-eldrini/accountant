# Release Notes

## v0.7.0 — Sales Workspace

Inspired by the supplied Arabic accounting workflow video.

### Added
- Sales workspace with searchable quotations, cash sales, credit sales, and returns.
- Itemized documents with quantity, unit price, discount, tax, and server-calculated totals.
- Quote-to-invoice conversion with duplicate-conversion protection.
- Payment collection and partial returns with remaining-quantity checks.
- Pending refunds require explicit confirmation after payment.
- Customer statements, date-filtered sales reports, CSV export, and print/save-to-PDF.
- Arabic/English, dark/light themes, and mobile sales navigation.
- Sales records included in full backups.

### Fixed
- Restore preserves original record IDs so linked documents remain connected.
- PostgreSQL sequences reset after restoration.
- Restore logs use the current username model.
- Corrected the existing analytics smoke check to inspect the dashboard.

### Verification
- 12 automated sales tests passed locally.
- Existing admin, backup/restore, and permissions smoke tests passed.
- Deployed verification recorded in the release pull request.

### Scope
- This release provides an accounting demonstration, not Saudi e-invoicing certification or integration.
- Inventory quantities and cost-of-goods accounting are outside this release.
- The existing Render service currently uses SQLite; this release does not migrate its database.


## v0.6.0 — Local User Profiles

### Added
- Local username-based authentication for on-prem/local deployments.
- First Name and Last Name fields for every user.
- My Profile page for each signed-in user.
- Users can update their own first name, last name, and password.
- Admin can manage username, first name, last name, role, status, and password.
- Username uniqueness validation.
- Existing users are migrated automatically from legacy account data.

### Changed
- Email address is no longer required or shown for application users.
- Login now uses Username + Password.
- Default local accounts are now:
  - `admin`
  - `accountant`
- User header displays First Name + Last Name.
- Audit entries use local username as the actor identity.
- Application version updated to `0.6.0`.

### Backward-safe migration
The old database columns are retained internally for migration compatibility, but email is no longer part of the user-facing account model or authentication flow. Existing `admin@accountant.local` and `accountant@accountant.local` records are migrated to usernames `admin` and `accountant`.

### Verification
- Feature CI: **PASSED** — GitHub Actions run `36769788258`.
- Staging deploy: **LIVE** — `dep-daumlrfpn0mc7389m6lg`.
- Deployed staging authenticated smoke test: **PASSED** — GitHub Actions run `36769860713`.
- Release PR CI: **PASSED** — GitHub Actions run `36770074207`.
- Production release commit: `f2e27a3fbeb83f688b525f599af45aac9b283b7b`.
- Render production deploy: **LIVE** — `dep-daummtojo6nc73dpgp30`.
- Authenticated production smoke test: **PASSED** — GitHub Actions run `36770138460`.
- Local username login.
- Profile page availability.
- First/last name display.
- Admin user creation using username only.
- Viewer access restrictions.
- Backup/restore including migrated user profile fields.
- Existing accounting, analytics, Administration and audit tests remain in the release gate.

## v0.5.0 — 2026-09-30

### Added
- Executive Business Summary on the main dashboard.
- 6-month Revenue vs Expenses chart.
- 6-month Net Profit trend.
- Invoice collection analysis with collection rate, invoiced, collected, outstanding, and overdue value.
- Top Expense Categories analysis.
- Top Customers by Invoice Value analysis.
- Executive Insights section for profitability, collections, and cost concentration.
- Executive KPI cards for revenue, expenses, net profit, receivables, payables, and collection rate.
- Arabic translations for the new executive analytics labels.
- Dark and Light theme compatibility for all new analytics components.

### Executive Purpose
The dashboard is designed for business owners, General Managers, CFOs, and executives who need a concise view of overall business performance without reading detailed accounting tables.

The executive view answers:
1. Are we making money?
2. Are revenue and expenses moving in the right direction?
3. Are customers paying us?
4. Where is the business spending money?
5. Which customers represent the highest invoice value?

### Testing
- Application version updated to `0.5.0`.
- Smoke tests verify all executive analytics sections are rendered.
- Existing accounting, role, administration, backup/restore, and audit tests remain in the release gate.

### PostgreSQL Status
- The application already supports PostgreSQL through the `DATABASE_URL` environment variable.
- The managed Render PostgreSQL instance `accountant-db` exists and is available.
- The Render connector exposes the database name/user but does not expose its generated password/Internal Database URL and does not currently provide a database-to-service secret-link action.
- For that reason, the service cannot be safely switched from SQLite to PostgreSQL programmatically without the Render Internal Database URL.
- No database credential has been guessed or embedded in source code.

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

### Production Verification
- Release pull request CI: **PASSED** — GitHub Actions run `36766766069`.
- Production release commit: `de9c13063ab1f79bed8b0bf583d8f3abd2258ed9`.
- Render production deploy: **LIVE** — `dep-daum9fe7bikc73cuqv8g`.
- Main-branch CI: **PASSED** — GitHub Actions run `36766828412`.
- The main-branch workflow waited for the real Render production service to report version `0.4.0`.
- Authenticated smoke test against the actual production URL: **PASSED**.
- Production verification checked the Admin navigation and the deployed Dashboard, Transactions, Invoices, Expenses, Customers, Vendors, Chart of Accounts, Journal, Reports, Users, Audit Log, Backup & Restore, System Status, and Settings routes.

### Issues Encountered and Resolved During Testing
- The first v0.4.0 behavioral test run failed on the role-navigation test.
- Root cause: the test searched for the text `ADMINISTRATION`, which also existed in the client-side Arabic translation dictionary even when the Viewer menu was correctly hidden.
- Resolution: the test was corrected to verify actual rendered Administration links instead of translation text.
- The corrected permission, backup/restore, staging, and production tests all passed before this release was marked verified.

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
