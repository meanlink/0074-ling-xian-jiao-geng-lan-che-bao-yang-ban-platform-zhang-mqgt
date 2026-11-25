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
CREATE TABLE IF NOT EXISTS followups(
 id text PRIMARY KEY, shift text NOT NULL REFERENCES cabin_shifts(code),
 work text NOT NULL REFERENCES work_orders(code), matter text NOT NULL,
 status text NOT NULL DEFAULT 'open' CHECK(status IN ('open','ack')),
 receiver text REFERENCES app_users(email), initials text,
 CHECK ((status='ack')=(receiver IS NOT NULL)),
 CHECK ((status='ack')=(initials IS NOT NULL))
);
CREATE TABLE IF NOT EXISTS handoffs(
 shift text PRIMARY KEY REFERENCES cabin_shifts(code),
 destination text NOT NULL CHECK(destination IN ('lead','desk')),
 delivery text NOT NULL DEFAULT 'pending' CHECK(delivery IN ('pending','sent')),
 data jsonb NOT NULL, job_id bigint UNIQUE NOT NULL REFERENCES app_jobs(id),
 sent_at timestamptz, CHECK ((delivery='sent')=(sent_at IS NOT NULL))
);
