---
isCJKLanguage: true
draft: false
title: 連絡先
---

ここで読んだことについて何か言いたいことがあれば ― あるいは、ここで読んだこととは関係のない、連絡を取るちゃんとした理由があれば ― 私に連絡してください。以下がその方法です。嬉しさの度合いが高い順に並べてあります。

営業目的の方へ：お元気で。本気でそう思っています。メールはご遠慮ください。

## メール

[gus@gusguidry.com](mailto:gus@gusguidry.com)

これが一番好ましい方法です。すべて目を通しています。返信する価値があるものには返信します。

## VCard

連絡先アプリにそのまま保存できる形式が欲しい方のために、vCardを用意しました ― 1995年に生まれて、なぜか今でも完璧に機能しているこの形式に詰め込んであります。

[vCardをダウンロード](/gusguidry.vcf)するか、スマートフォンをお使いでダウンロードボタンすら面倒なら、QRコードをスキャンしてください。

{{< qr level="low" scale=2 alt="August GuidryのvCardのQRコード" >}}
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

暗号化したものを送りたい方は、その判断を無条件に支持します。

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
