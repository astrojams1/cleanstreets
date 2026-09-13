---
name: field-updates
description: "Turn the crew's cleanup photos into updates people see: pull new photos from Travis's shared iCloud album, write a short block-named post, publish it to Patreon through the browser (Patreon's API cannot post), keep the website's photo gallery current, and log every post with a tracked link. Use whenever the user mentions posting to Patreon, the photo album, Travis's photos, before-and-after pictures, a field update, a patron update, 'post the photos', 'what did the crew do this week', social media content from the crew, or on the scheduled field-updates run, even if they don't name the skill."
metadata:
  version: "1.0"
---

# Field Updates

The crew's photos are the most convincing thing Clean Streets has. This
skill gets them in front of patrons, prospects, and site visitors with no
work from James: album to post to gallery, on a schedule. Conventions
shared with every skill are in `.claude/skills/README.md`.

Ref code for this skill: `FU`. It sends no email. Posts per run: at most
one to Patreon. Patreon links in posts carry `?ref=post-<yyyymmdd>`.

## Step 0: Preflight

1. Note the start time in Pacific time and read the last three entries:
   ```bash
   python3 scripts/ledger.py show --skill field-updates --last 3
   ```
2. Read `references/post-style.md`.
3. Check what this run can do:
   ```bash
   python3 scripts/cs_secrets.py check patreon_session
   ```
   Exit 1 means no Patreon session cookie is resolvable: the run still
   syncs photos and the gallery, writes the post text into the ledger as
   `drafted`, and reports that the cookie is missing or expired (James
   refreshes it in 1Password; see the README's Secrets section).

## Step 1: Sync the album

```bash
python3 scripts/shared_album.py sync --keep 48
python3 scripts/update_photos.py --count 12
```

The first pulls new photos from the album into `images/album/` and updates
`data/photos.json`; the second renders the newest 12 into the website's
`#photos` section. Both are idempotent. Then list what is new since the
last post: every photo in `data/photos.json` whose `date` is later than
the `posted_through` value on the last `post:` ledger line (or the last 7
days if there is none). No new photos and no post due: write a `noop`
entry and stop after Step 4.

## Step 2: Write the post

One post per run, from the new photos, per `references/post-style.md`:
a title with the block or the week, three to five sentences in James's
voice about what the crew did (where, roughly how much, anything visible
in the photos), the running totals from `data/impact.csv` only if they
changed this month, and one line with the tracked link
`https://www.patreon.com/cleanstreets?ref=post-<yyyymmdd>`. Pick two to
four photos, before-and-after pairs first. Look at the photos you pick
(Read the files) so the text matches them; never describe a photo you
have not looked at, and never name a person in a photo.

Write the body to `tmp-build/post.html` (plain paragraphs, no signature,
no ref-code line; this is a post, not an email).

## Step 3: Publish

```bash
node scripts/patreon_post.mjs --title "<title>" --body-file tmp-build/post.html \
  --image <photo> --image <photo> --audience public --dry-run
```

Read `tmp-build/patreon-post.png` and check three things: the title is
in the title field, the body is in the editor, the images are attached.
If all three are right, run the same command without `--dry-run`. Exit 0
prints `PUBLISHED: <url>`; ledger it. Exit 2 means the session cookie has
expired: ledger the post as `drafted` with the full text and report the
cookie for James. Exit 3 means Patreon's editor changed: read the
screenshot, fix the selectors in `scripts/patreon_post.mjs` if the fix is
obvious, otherwise ledger `drafted` and describe what the screenshot shows
so the next run (or skill-improver) can fix it. Exit 1 with
`ERR_CONNECTION_RESET` means the sandbox is not letting the browser reach
Patreon at all (seen 2026-09-12 in the Claude Code sandbox: curl passes
through the proxy, Chromium does not); ledger `drafted` with the full
text, say so in the report, and do not retry in the same run.

Once a month, the growth skill's impact post is also published this way;
if `.claude/skills/patreon-growth/references/posts/` has a draft newer
than the last `post:` line, publish it here and ledger it for both skills.

## Step 4: Ledger and commit

```bash
python3 scripts/ledger.py add --skill field-updates \
  --started "<start time>" \
  --outcome success \
  --actions <photos synced + posts published> \
  --summary "<n> new photos; posted '<title>' to Patreon (or drafted: reason); gallery updated" \
  --metric new_photos=<n> --metric posts=<0|1> --metric photos_in_post=<n> \
  --metric gallery_count=<n> --metric album_total=<n> \
  --detail "post:<yyyymmdd> | published|drafted | <url or reason> | posted_through=<newest photo date used>" \
  --detail "photos | <file>, <file> ..." \
  --next "<next post date or the cookie to refresh>"

bash scripts/run_tests.sh
python3 scripts/ledger.py check
git add images/album data/photos.json index.html .claude/skills/field-updates/
git commit -m "ledger(field-updates): <summary>"
git push origin HEAD
```

A push to master deploys the gallery. Delete `tmp-build/` at the end.

## Run report

```
Photos: <n> new since last post (<album_total> in album), gallery shows newest 12
Post: <title> | published <url> | drafted (<reason>)
Photos used: <files>
For James: <only a cookie refresh, or nothing>
Ledger: run NNNN appended and committed
```

## What this skill does not do

- Does not email anyone; patron and prospect email belongs to
  patreon-growth and inbox-processor.
- Does not post to Facebook or Instagram yet; when a Meta page token is
  in 1Password, that becomes a second publish step here.
- Does not edit any part of the site outside the `#photos` markers.
- Does not identify or name people in photos.
