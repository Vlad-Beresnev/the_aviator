---
phase: quick-1
plan: 1
type: execute
wave: 1
depends_on: []
files_modified:
  - db/populatedb.py
  - db/lp_project_base.sql
  - .planning/PROJECT.md
autonomous: true
requirements: []

must_haves:
  truths:
    - "db/ folder exists with both import files"
    - "PROJECT.md references the Finnish open data API and the Metropolia example project"
  artifacts:
    - path: "db/populatedb.py"
      provides: "Python script to populate database from SQL file"
    - path: "db/lp_project_base.sql"
      provides: "SQL dump with ~6,899 airport rows"
    - path: ".planning/PROJECT.md"
      provides: "Updated with external references"
  key_links:
    - from: "db/populatedb.py"
      to: "db/lp_project_base.sql"
      via: "script runs the SQL file against mysql.metropolia.fi"
---

<objective>
Add the database import files to the project and update PROJECT.md with two external references.

Purpose: The db/ folder gives any contributor a one-step way to populate the MariaDB database. The PROJECT.md additions surface the Finnish open data portal and the Metropolia assignment example so they are not lost.
Output: db/ folder with two files, updated PROJECT.md.
</objective>

<execution_context>
@/Users/vlad/.claude/get-shit-done/workflows/execute-plan.md
@/Users/vlad/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Copy db import files into db/</name>
  <files>db/populatedb.py, db/lp_project_base.sql</files>
  <action>
    Create the `db/` directory at the project root (/Users/vlad/dev/the_aviator/db/).

    Copy both source files from /Users/vlad/Downloads/import-db-python/ into it:
    - populatedb.py  →  db/populatedb.py
    - lp_project_base.sql  →  db/lp_project_base.sql

    Do not modify either file's content. Use the Bash tool to run:
      mkdir -p /Users/vlad/dev/the_aviator/db
      cp /Users/vlad/Downloads/import-db-python/populatedb.py /Users/vlad/dev/the_aviator/db/
      cp /Users/vlad/Downloads/import-db-python/lp_project_base.sql /Users/vlad/dev/the_aviator/db/
  </action>
  <verify>
    <automated>ls /Users/vlad/dev/the_aviator/db/ && wc -l /Users/vlad/dev/the_aviator/db/lp_project_base.sql</automated>
  </verify>
  <done>Both files exist in db/; lp_project_base.sql is ~71,000 lines.</done>
</task>

<task type="auto">
  <name>Task 2: Update PROJECT.md with external references</name>
  <files>.planning/PROJECT.md</files>
  <action>
    Read .planning/PROJECT.md in full, then append a new section titled "## External References" before the final horizontal rule and "Last updated" line. The section must contain exactly:

    ```
    ## External References

    - **Finnish open data portal**: https://avoindata.suomi.fi/fi — national open data catalogue; potential source for additional aviation or geographic datasets
    - **Metropolia assignment example**: https://github.com/ilkkamtk/software-1-project-example — reference implementation showing expected structure and scope for Ohjelmisto 1 coursework
    ```

    Also update the "Last updated" timestamp to 2026-03-09 (already correct) or today's date if it differs.

    Use the Write tool to save the updated file. Preserve all existing content exactly.
  </action>
  <verify>
    <automated>grep -c "avoindata.suomi.fi" /Users/vlad/dev/the_aviator/.planning/PROJECT.md && grep -c "ilkkamtk" /Users/vlad/dev/the_aviator/.planning/PROJECT.md</automated>
  </verify>
  <done>PROJECT.md contains both URLs under an "External References" heading.</done>
</task>

</tasks>

<verification>
- `ls /Users/vlad/dev/the_aviator/db/` shows populatedb.py and lp_project_base.sql
- `grep "avoindata" /Users/vlad/dev/the_aviator/.planning/PROJECT.md` returns a match
- `grep "ilkkamtk" /Users/vlad/dev/the_aviator/.planning/PROJECT.md` returns a match
</verification>

<success_criteria>
- db/ folder exists with both import files, content unmodified from source
- PROJECT.md has an "External References" section with both URLs, all prior content intact
</success_criteria>

<output>
After completion, create `.planning/quick/1-update-plan-with-db-files-finnish-open-a/1-SUMMARY.md` with what was done, files created/modified, and any notes.
</output>
