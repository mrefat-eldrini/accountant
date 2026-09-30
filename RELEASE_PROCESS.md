# Release Process

All production changes follow this path:

1. Create a dedicated branch from `main` using `feature/*`, `fix/*`, or `chore/*`.
2. Commit changes only to that branch.
3. Update `RELEASE_NOTES.md` for user-visible or production-impacting changes.
4. Open a pull request from the working branch to `develop`.
5. Run automated CI and smoke tests.
6. Merge into `develop` only after tests pass.
7. Render staging automatically deploys `develop`.
8. Verify staging deployment status, startup logs, and smoke-test results.
9. Open a release pull request from `develop` to `main`.
10. Merge to `main` only after staging verification is complete.
11. Render production deploys `main`.
12. Verify production deployment status, startup logs, health endpoint, authentication behavior, and key application routes.
13. Record production verification in `RELEASE_NOTES.md`.

Production URL: https://accountant-b7hw.onrender.com  
Staging URL: https://accountant-staging.onrender.com
