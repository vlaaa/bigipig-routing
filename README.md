# Bigipig Routing

Кастомные routing-правила для HApp клиентов сервиса [Bigipig VPN](https://bigipig.com).

## Что это и зачем

`HAPP/default.json` — это конфиг для HApp app, описывающий какой трафик идёт **напрямую** с устройства юзера в обход VPN-туннеля, а какой — через VPN. После импорта подписки HApp применяет эти правила на стороне клиента.

Ключевая цель: **российские сервисы видят реальный IP юзера (не VPN), а заблокированные в РФ сервисы — идут через VPN**. Это решает проблемы типа «Yandex Go не работает с включённым VPN» и одновременно даёт доступ к YouTube/Telegram/Discord.

## Структура

```
HAPP/
  default.json       — человекочитаемая конфигурация
  default.deeplink   — base64-кодированный deeplink для HApp (генерируется автоматически)
scripts/
  build_deeplink.py  — конвертирует default.json в default.deeplink
.github/workflows/
  build.yml          — auto-rebuild при изменении default.json + commit обратно
```

## Категории

### 🟢 Direct (мимо VPN, реальный IP юзера)
- **RU**: `geosite:category-ru` + `geosite:whitelist` (Yandex, VK, Mail.ru, Sberbank, Tinkoff, и т.д.)
- **Системное**: Apple (iCloud, App Store, Push), Microsoft (Windows Update, Office), Google Play
- **Игры с серверами в РФ/EU без блокировок**: Steam, Epic Games, Escape from Tarkov, Battle.net, EA/Origin, Ubisoft, Minecraft, Roblox

### 🔴 Proxy (через VPN-туннель)
- **Заблокированные в РФ**: YouTube, Telegram, Twitch, GitHub, Discord, Twitter/X, Reddit, ChatGPT
- **Игры с проблемным login**: Riot Games (Valorant/LoL), Faceit, Rockstar (GTA Online/Social Club)

### 🛡️ Block
- Реклама (`geosite:category-ads`, Google Ads, Doubleclick, Yandex.Metrika, Mail.ru analytics)
- Торренты (`geosite:torrent`)
- Microsoft Windows телеметрия (`geosite:win-spy`)
- Twitch ads (`geosite:twitch-ads`)
- Cryptominers (CoinHive, monerominer, и т.д.)

## DNS

- **Remote DNS** (через VPN): `1.1.1.1` (Cloudflare DoH)
- **Domestic DNS** (для direct): `77.88.8.8` (Yandex DoH)

Hardcoded host fix для `lkfl2.nalog.ru` и `lknpd.nalog.ru` — Налоговая иногда не отдаёт правильный IP через публичный DNS.

## Geo-файлы

Используются из [hydraponique/roscomvpn-geosite](https://github.com/hydraponique/roscomvpn-geosite) и [hydraponique/roscomvpn-geoip](https://github.com/hydraponique/roscomvpn-geoip) — спасибо им за поддержку списков. CDN: jsDelivr `@latest`, обновления автоматически.

## Как применяется на проде

В Remnawave panel есть поле `subscription-settings.happRouting`. Контейнер [Remnawave-Routing-update](https://github.com/lifeindarkside/Remnawave-Routing-update) на сервере Bigipig раз в 5 минут синхронизирует это поле с содержимым `default.deeplink` из этого репо. При импорте подписки HApp получает routing вместе с нодами.

## Юзеры: как получить обновления

1. Открыть Mini App / Web Cabinet
2. Раздел «Моя подписка» → «Перевыпустить ссылку» (revoke)
3. Импортировать новую подписку в HApp

После реимпорта HApp применит свежий routing. До этого момента действует тот routing, который был на момент предыдущего импорта.

## Изменение конфигурации

1. Отредактировать `HAPP/default.json` (через GitHub web UI или локально + push)
2. GitHub Action автоматически пересоберёт `default.deeplink` и закоммитит обратно
3. Через ~5 минут routing-updater подсосёт новый файл в Remnawave
4. Новые импорты юзеров получат свежий routing
