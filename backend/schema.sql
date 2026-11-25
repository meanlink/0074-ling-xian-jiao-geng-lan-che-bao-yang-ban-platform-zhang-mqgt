CREATE TABLE IF NOT EXISTS cabin_shifts(
 code text PRIMARY KEY, roster_day date NOT NULL, station text NOT NULL, team text NOT NULL,
 lo integer NOT NULL CHECK(lo>=0),hi integer NOT NULL CHECK(hi>lo AND hi<=2880), UNIQUE(roster_day,station,lo)
);
CREATE TABLE IF NOT EXISTS work_orders(
 code text PRIMARY KEY, title text NOT NULL, station text NOT NULL,
 family text NOT NULL CHECK(family IN ('retained','inspection','documentation'))
);
CREATE TABLE IF NOT EXISTS shift_slices(
 code text PRIMARY KEY, shift text NOT NULL REFERENCES cabin_shifts(code),
 work text NOT NULL REFERENCES work_orders(code), lo integer NOT NULL CHECK(lo>=0),
 hi integer NOT NULL CHECK(hi>lo AND hi<=2880), staff text NOT NULL,
 weight smallint NOT NULL CHECK(weight IN (25,50,75,100))
);
-- A followup is raised on its origin shift and is currently held by "shift".
-- Signing it off names the same-station shift that will receive it; the move
-- only happens when the holder's handoff is actually delivered.  Lifecycle:
--   open  - raised, waiting for the reviewer to sign it off to a later shift
--   ack   - signed off to next_shift, still held here until this shift's
--           handoff is delivered
--   held  - delivered into this shift; it can be closed or handed on again
--   done  - closed by the shift that held it
CREATE TABLE IF NOT EXISTS followups(
 id text PRIMARY KEY, origin text NOT NULL REFERENCES cabin_shifts(code),
 shift text NOT NULL REFERENCES cabin_shifts(code),
 next_shift text REFERENCES cabin_shifts(code), delivered_to text REFERENCES cabin_shifts(code),
 work text NOT NULL REFERENCES work_orders(code), matter text NOT NULL,
 status text NOT NULL DEFAULT 'open' CHECK(status IN ('open','ack','held','done')),
 receiver text REFERENCES app_users(email), initials text,
 signed_at timestamptz, delivered_at timestamptz,
 closed_by text REFERENCES app_users(email), closed_initials text, closed_at timestamptz,
 CONSTRAINT followups_ack_target CHECK(status<>'ack' OR next_shift IS NOT NULL),
 CONSTRAINT followups_signature_check CHECK((receiver IS NULL)=(initials IS NULL))
);
CREATE TABLE IF NOT EXISTS handoffs(
 shift text PRIMARY KEY REFERENCES cabin_shifts(code),
 destination text NOT NULL CHECK(destination IN ('lead','desk')),
 delivery text NOT NULL DEFAULT 'pending' CHECK(delivery IN ('pending','sent')),
 data jsonb NOT NULL, job_id bigint UNIQUE NOT NULL REFERENCES app_jobs(id),
 sent_at timestamptz, CHECK ((delivery='sent')=(sent_at IS NOT NULL))
);

-- Roll an existing database forward without losing old followup rows.
ALTER TABLE followups ADD COLUMN IF NOT EXISTS origin text REFERENCES cabin_shifts(code);
ALTER TABLE followups ADD COLUMN IF NOT EXISTS next_shift text REFERENCES cabin_shifts(code);
ALTER TABLE followups ADD COLUMN IF NOT EXISTS delivered_to text REFERENCES cabin_shifts(code);
ALTER TABLE followups ADD COLUMN IF NOT EXISTS signed_at timestamptz;
ALTER TABLE followups ADD COLUMN IF NOT EXISTS delivered_at timestamptz;
ALTER TABLE followups ADD COLUMN IF NOT EXISTS closed_by text REFERENCES app_users(email);
ALTER TABLE followups ADD COLUMN IF NOT EXISTS closed_initials text;
ALTER TABLE followups ADD COLUMN IF NOT EXISTS closed_at timestamptz;

-- Old inline checks only knew open/ack and tied every signature to ack.
ALTER TABLE followups DROP CONSTRAINT IF EXISTS followups_check;
ALTER TABLE followups DROP CONSTRAINT IF EXISTS followups_check1;
ALTER TABLE followups DROP CONSTRAINT IF EXISTS followups_check2;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname='followups_status_check'
             AND conrelid='followups'::regclass AND pg_get_constraintdef(oid) NOT LIKE '%held%') THEN
    ALTER TABLE followups DROP CONSTRAINT followups_status_check;
  END IF;
END $$;

UPDATE followups SET origin=shift WHERE origin IS NULL;
ALTER TABLE followups ALTER COLUMN origin SET NOT NULL;

-- Old sign-offs had no destination and therefore never left the shift.  Keep
-- them there as held work so that shift can close or hand them on.
UPDATE followups SET status='held', delivered_to=shift,
  delivered_at=COALESCE(delivered_at,signed_at,now()), signed_at=COALESCE(signed_at,now())
WHERE status='ack' AND next_shift IS NULL;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='followups_status_check'
                 AND conrelid='followups'::regclass) THEN
    ALTER TABLE followups ADD CONSTRAINT followups_status_check
      CHECK(status IN ('open','ack','held','done'));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='followups_ack_target'
                 AND conrelid='followups'::regclass) THEN
    ALTER TABLE followups ADD CONSTRAINT followups_ack_target
      CHECK(status<>'ack' OR next_shift IS NOT NULL) NOT VALID;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='followups_signature_check'
                 AND conrelid='followups'::regclass) THEN
    ALTER TABLE followups ADD CONSTRAINT followups_signature_check
      CHECK((receiver IS NULL)=(initials IS NULL)) NOT VALID;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS followups_holder ON followups(shift,status);
CREATE INDEX IF NOT EXISTS followups_target ON followups(next_shift,status);

ALTER TABLE app_jobs ADD COLUMN IF NOT EXISTS attempts integer NOT NULL DEFAULT 0;
