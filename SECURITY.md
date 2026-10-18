# Security Policy

## Threat Model

This is a static website. It is HTML, CSS, and a guy's opinions about walking across Shikoku.

There is no database. There are no user accounts. There is no login page, no payment form, no admin panel, and no backend for you to pop a shell on. The most sensitive data stored here is my taste in books.

That said, I take security about as seriously as someone who runs a static blog can, which is to say: sincerely, and with low expectations of ever needing to.

## Supported Versions

| Version | Supported |
| ------- | --------- |
| Whatever is live at gusguidry.com right now | ✅ |
| Anything older | ❌ It's a blog. Just refresh. |

## What Counts as a Vulnerability

Things I genuinely want to hear about:

- Arbitrary code execution, somehow. If you manage it on a pile of static files, I'd like to know how, mostly out of curiosity.
- Cross-site scripting via anything that renders untrusted input
- A compromised or malicious dependency in the build
- Leaked secrets, keys, or tokens accidentally committed to this repo
- Anything that lets someone deface the site or serve content that isn't mine

Things that are probably not vulnerabilities:

- "Your site is missing header X" (fair, but not an emergency)
- Typos (please still tell me, just not here)
- Disagreeing with a post
- My writing style

## Reporting a Vulnerability

Please report it privately through GitHub's **Report a vulnerability** button on this repository's **Security** tab, rather than opening a public issue.

I'll take a look as soon as I'm not on a job site or halfway up a mountain. Expect a response within a reasonable number of days. If it's real, I'll fix it and credit you here, if you'd like.

## Hall of Fame

Nobody yet. Be the first.
