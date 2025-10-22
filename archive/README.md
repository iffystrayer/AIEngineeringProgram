# Archive Directory

This directory contains archived files that are not required to run the application. These files include:

## Contents

### Status & Report Documents (100+ files)
- Phase completion reports
- Audit reports and summaries
- Implementation status documents
- Test reports and assessments
- Progress summaries
- Planning documents
- Architecture documentation
- Integration reports

### Test & Development Files
- Test output logs
- Coverage reports (htmlcov/)
- Temporary test scripts
- Demo workflow files
- E2E test output files

### Logs
- Application logs
- Build logs
- Test execution logs

## Why These Files Are Archived

These files were created during development and testing phases to:
- Track progress and status
- Document decisions and findings
- Report on test results
- Plan implementation phases
- Verify compliance with specifications

They are not required for:
- Running the application
- Building the project
- Deploying to production
- Core functionality

## Accessing Archived Files

If you need to reference any archived files:

```bash
# List all archived files
ls -la archive/

# Search for a specific file
find archive -name "*filename*"

# View a specific file
cat archive/FILENAME.md
```

## Restoring Files

To restore a file from the archive:

```bash
# Move file back to root
mv archive/FILENAME.md ./

# Or copy if you want to keep the archive version
cp archive/FILENAME.md ./
```

## Archive Statistics

- **Total Files:** 178
- **Total Size:** ~3.7 MB
- **Categories:** Status reports, test files, logs, coverage reports

## Essential Files (Not Archived)

The following files are kept in the root directory as they are essential:

### Configuration
- `pyproject.toml` - Project dependencies and configuration
- `uv.lock` - Dependency lock file
- `.env` - Environment variables
- `.env.example` - Example environment configuration

### Deployment
- `Dockerfile` - Container image definition
- `docker-compose.yml` - Multi-container setup
- `Makefile` - Build automation

### Documentation
- `README.md` - Main project documentation
- `DOCKER.md` - Docker setup guide
- `install.sh` - Installation script

### Source Code
- `src/` - Application source code
- `tests/` - Test suite
- `frontend/` - Frontend application
- `config/` - Configuration files
- `database/` - Database setup
- `scripts/` - Utility scripts
- `docs/` - Documentation
- `templates/` - Application templates
- `examples/` - Usage examples
- `security/` - Security configurations
- `charters/` - Generated project charters

## Cleanup Date

**Date:** October 22, 2025  
**Files Archived:** 178  
**Space Freed:** ~3.7 MB

---

For questions about archived files, refer to the git history or contact the development team.

