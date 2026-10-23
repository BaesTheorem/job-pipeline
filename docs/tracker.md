# The tracker

The tracker is the folder of listing notes (`paths.listings` in `profile.yaml`). Each note has `type: job-listing` frontmatter (schema in the skill). Any tool that reads markdown frontmatter can show it as a table.

## Obsidian

Put the listings folder in an Obsidian vault and copy `templates/Job Listings.base` next to it. The Bases file gives four views:

- **Active**: candidates you have not applied to, sorted by fit score
- **Applied**: by application date
- **Re-apply watchlist**: notes with `reapply: true`
- **All**

The filter matches on `type == "job-listing"`, not on a folder. Notes in subfolders (one folder per qualifying role) and in an archive folder still show.

Tick the **Applied** checkbox in the table to set `applied: true` on the note.

## Keep the frontmatter consistent

`tracker/reconcile.py` runs two rules, and changes nothing else:

1. `applied: true` with `status: candidate` sets `status: applied` and stamps `application_date` with today's date.
2. `status: rejected` with no `rejection_date` stamps it.

It is idempotent. Run it after you tick boxes, from cron, or from a file watcher on the listings folder (on macOS, a launchd `WatchPaths` key).

## Without Obsidian

`python3 pipeline/runlog.py yield` prints the funnel by `source`. `python3 pipeline/dedup-lookup.py --stats` prints counts by status. Any markdown-frontmatter tool (Logseq, Dataview, a short Python script) works.
