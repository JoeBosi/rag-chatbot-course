# Privacy {#privacy}

A short page, because there is little to say.

## This site {#questo-sito}

These are static pages: text, images and style sheets, all hosted
here. The site **collects nothing**.

- **No cookies**, no ads, no analytics (no Google Analytics or
  similar).
- **No requests to third-party servers**: the theme's fonts, style
  sheets and scripts live on this site, so opening a page contacts no
  other service. The only external addresses are the **links** in the
  texts: they count only if you choose to click them.
- **No forms to fill in**: nothing to sign up for, no email to leave.
  The site search runs inside your browser, without sending out what
  you search for.
- **No access log**: the server that serves these pages keeps no log
  of visits. It records only its own technical events (certificate
  renewals, errors), which stay on the server.

## When you take the course, though {#quando-fai-il-corso-invece}

The course has you use the free tiers of model providers (Groq,
Google AI Studio, OpenRouter). Their privacy policy applies there, not
this one: the texts you send leave your computer, and **almost all free
tiers reserve the right to use them to improve their models**.

The practical consequence, the same one you find on the home page and
in the final project: in your knowledge base put your toaster manuals
and your workshop notes, **not** customer data, other people's personal
data, confidential documents or passwords.

If your material is sensitive, the course keeps the **local path** open
from the first module with [Ollama](SETUP.md#strada-locale-ollama):
models that run on your computer, no data leaves. It is slower and
needs more memory, but it is complete: every module works this way too.

Embeddings, the part that turns texts into numbers, are **always
computed locally**, even when the rest goes through the providers: that
part of your material never leaves, by the way the course is built.

## Your keys {#le-tue-chiavi}

Your provider keys live in the `.env` file on your computer, and the
course teaches you never to write them in code, configurations or
repositories. That is exactly why the module 2 gateway listens only on
`127.0.0.1`: nobody on your network can use your keys.
