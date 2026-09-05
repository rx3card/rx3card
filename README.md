<p align="center">
  <img src="./assets/terminal.svg" width="100%" alt="Oscar Rojas — Full-Stack Developer, Ibagué, Colombia">
</p>

<p align="center">
  <a href="https://rx3card.vercel.app/en/">Portfolio</a> ·
  <a href="https://rx3card.vercel.app/cv/CV-Oscar-Rojas-EN.pdf">CV (EN)</a> ·
  <a href="https://rx3card.vercel.app/cv/CV-Oscar-Rojas.pdf">CV (ES)</a> ·
  <a href="https://www.linkedin.com/in/rx3card/">LinkedIn</a> ·
  <a href="mailto:rx3card@gmail.com">rx3card@gmail.com</a>
</p>

<p align="center">
  <sub><a href="https://rx3card.vercel.app">Leer en español</a> · Ibagué, Tolima, Colombia · Remote, hybrid or on-site · Open to work</sub>
</p>

---

I build web systems end to end — schema, backend, interface, and the Linux box
it all runs on — and then I stay to keep them running.

I taught myself to program three years ago from documentation, and enrolled at
SENA afterwards, already writing code. Since February 2026 I have been the only
developer at an insurance agency. Everything below is in production, with people
on the other side of it.

## The system I maintain

**[ricardoserranoasesores.com](https://www.ricardoserranoasesores.com)** ·
`Next.js 16` `React 19` `TypeScript` `SQLite` `Socket.IO` `WhatsApp Cloud API` `nginx` `PM2` `Linux`

The agency tracked policy renewals in spreadsheets. Someone had to open them and
read row by row to find what was about to expire, and when a date slipped past,
the client learned they had lost coverage after the fact. WhatsApp went to the
advisors' personal phones and was recorded nowhere.

It started as a commission for a website. It is now the website, an internal
panel where the team manages clients and policies, and a WhatsApp bot that
answers the routine questions and hands the conversation to a human the moment
it should. Renewal notices go out on their own every morning. Since then it has
grown policy reports delivered as PDFs over WhatsApp, a self-hosted email system
with templates and a newsletter, first-party analytics, and an assistant that
answers questions about the business in plain Spanish.

I own the whole cycle: analysis, database, code, the server, the deploys, the
backups, and the phone call when something breaks. Retiring an external licence
and the inherited hosting for a VPS cut the agency's annual tooling spend by
more than 75%.

### Decisions I would defend in an interview

- **SQLite on the server, not a managed database.** Hundreds of policies, not
  millions. A local file answers faster, costs no monthly fee, and a backup is a
  file copy. Postgres would have been paying for capacity nobody will use.
- **The natural-language assistant can only read.** It turns business questions
  into SQL with a language model. Models get things wrong, so every query passes
  a guard that blocks anything that is not a `SELECT`. If the model tries to
  delete something, it never reaches the database.
- **The bot's silence lives in the database, not in memory.** When an advisor
  steps into a chat, the bot goes quiet in that conversation. Had that lived in
  memory, a restart would wake it mid-sentence and it would start replying over
  a human. In the database, the silence survives restarts and deploys.
- **Link previews resolve DNS before they fetch anything.** The panel unfurls
  any link pasted into a chat, which means the server opens an address a
  stranger wrote. I resolve the name, refuse private IPs, and re-check on every
  redirect — otherwise it is an invitation to read the cloud metadata endpoint.

### What broke, and what I left behind so it would not happen again

Nobody's system is clean. Mine has been down twice, and both times taught me
more than the features did.

- **The site served without styles, twice, hours apart.** Not a code bug — the
  order of my deploy commands. The server reads the build manifest once, at
  boot, and keeps it in memory; I was rebuilding with the app still running, so
  it served filenames that no longer existed. The disorienting part is that it
  does not look like an error: the HTML returns 200, and the only symptom is a
  404 on a stylesheet nobody watches. *Fix:* a deploy script that stops the app
  before building, keeps the previous build, and rolls back to it if the new one
  fails — so a bad deploy restores itself instead of waiting to be noticed.
- **The panel stopped updating live and nobody noticed for days.** I had an
  endpoint under the same path as the socket server. Its attach step claims
  every request whose URL starts with that path and detaches listeners already
  registered, so my endpoint existed, answered 400, and never ran. No exception,
  no log line — new messages simply stopped appearing on their own. *Fix:* one
  line, moving my endpoint to its own path. Finding it meant reading the
  library's source.

## Other things I have built

| Project | What it is | Built with |
|---|---|---|
| **[click-to-source](https://github.com/rx3card/click-to-source)** | Click any element in a running app inside VS Code and land on the line that rendered it. React/Next, plain HTML, server-rendered templates. | `TypeScript` |
| **[cfetch](https://github.com/rx3card/cfetch)** | `neofetch` was slow because it spawns external processes for everything. Rewritten in C, reading what the OS already exposes: ~3 ms against ~220 ms on the same machine, no dependencies beyond libc, one source tree for Linux, Windows and macOS. | `C` `Make` |
| **[test_daltonismo](https://test-daltonismo.vercel.app)** | Colour vision test built on the Ishihara plates, with the result explained in plain language and the history of the originals. Indicative, not a diagnosis, and the site says so. | `JS` `a11y` |
| **[This portfolio](https://rx3card.vercel.app)** | Bilingual, hand-written in Astro. One `content.ts` is the single source: the site in both languages and both CVs are generated from it, so a fact is only ever edited in one place. | `Astro` `TS` |

## What I work with

- **Languages** — TypeScript · JavaScript · Python · C · SQL · Bash
- **Frontend** — React · Next.js · Astro · Tailwind CSS · HTML · CSS
- **Backend & data** — Node.js · SQLite · REST APIs · Socket.IO · JWT · Cron
- **Integrations** — WhatsApp Cloud API · Gemini · Groq · OpenAI SDK · Nodemailer · pdfmake
- **Infrastructure** — Linux · nginx · PM2 · Git · Vercel

Whatever is not on that list, I learn.

## Elsewhere

Technologist in Software Analysis and Development at SENA (in progress);
Technician in Software Development (completed). Spanish native; English at A2 —
I read technical documentation all day, and I am still working on speaking it.

If you have a role or a project, write to me at
**[rx3card@gmail.com](mailto:rx3card@gmail.com)**. I answer within 24 hours.

---

> There is only one good, knowledge. <br>
> There is only one evil, ignorance. <br>
> — Socrates
