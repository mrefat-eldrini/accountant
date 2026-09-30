# Release Notes

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
