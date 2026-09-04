# Repository Policy

The design specification is authoritative for this repository.

- Keep all public content safe for public release.
- Implementation work may mutate only the scope the user has explicitly authorized.
- Review and verification work are read-only.
- Treat existing tracked and untracked work as user-owned; do not destructively clean up or absorb unrelated changes.
- Do not include credentials, authentication artifacts, customer data, private repository names, private operational details, private infrastructure topology, or local machine paths in repository content.
- Commit each skill independently; do not combine multiple skill implementations in one commit.
- Before publishing, run both required validation commands:

  ```bash
  python scripts/validate_skills.py
  python -m unittest discover -s tests -p 'test_*.py' -v
  ```

- Update both `README.md` and `README.zh-CN.md` whenever public behavior or installation instructions change.
