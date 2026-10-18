---
aliases:
  - email
draft: false
title: Contact
---

If you've read something here and want to say something about it — or you have a good reason to reach out that has nothing to do with anything you read here — I'm reachable. Below are the ways to do that, ranked roughly by how much I enjoy receiving them.

Solicitors: I wish you well. I mean that sincerely. Please do not email me.

## Email

[gus@gusguidry.com](mailto:gus@gusguidry.com)

This is the preferred method. I read everything. I reply to things worth replying to.

## VCard

If you want my contact info in a format your phone can save directly, here's my vCard — packaged into a format invented in 1995 that somehow still works perfectly.

[Download my vCard](/gusguidry.vcf) or scan the QR code if you're on a phone and the download button feels like too many steps:

{{< qr level="low" scale=2 alt="QR code of vCard for Gus Guidry" >}}
BEGIN:VCARD
VERSION:3.0
FN:August Guidry
N:Guidry;August;;;
NICKNAME:Gus
ORG:
EMAIL;TYPE=INTERNET,PREF:gus@gusguidry.com
URL:https://www.gusguidry.com
REV:2026-04-12T12:20:00Z
END:VCARD
{{< /qr >}}

## PGP

If you want to send me something encrypted, I support that decision unconditionally.

```sh
curl -sL https://gusguidry.com/gusguidry.gpg | gpg --import
gpg --fingerprint gus@gusguidry.com
```

```txt
pub   ed25519 2024-12-31 [SC]
      F3BF C18B 40FD 67F3 FCA2  B091 3CC1 1436 2B51 17F8
uid           [ultimate] August Guidry (Gus) <gus@gusguidry.com>
uid           [ultimate] August Guidry <august@augustguidry.com>
sub   cv25519 2024-12-31 [E]
```
