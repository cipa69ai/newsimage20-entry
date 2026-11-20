# newsimage20-entry

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/cipa69ai/newsimage20-entry/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/cipa69ai/newsimage20-entry/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A newspaper front page summing up Friday 20 November 2026 in one image.
The historic Trump–Xi–Putin summit in Shenzhen leads, with the ICJ ruling
that Myanmar committed genocide against the Rohingya, Voyager 1 passing
one light-day from Earth, GTA 6's launch-week sales passing $1.8 billion,
Cyclone Akvan's evacuation in Odisha, and Anthropic's record $81.3B IPO.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is pure Python 3 stdlib: a hand-written PNG encoder and a 5x7
bitmap font draw the whole 1024x1024 front page — masthead, hero story
with a globe and the three leaders' flags, three supporting stories with
icons, a news strip, and a ticker. No network, no clock, no randomness:
every run writes byte-identical output (sha256
`f01be50653797e4b7169f4efe148900625b4e6a89ab2dd9561a5da314140af17`,
19,566 bytes).

## Stories in the image

- **Hero:** Trump, Xi and Putin meet in Shenzhen — first-ever three-way
  summit, a "peace declaration" signed; Trump says the Iran decision can
  wait until 2027.
- **World Court:** the ICJ rules Myanmar committed genocide against the
  Rohingya in the 2017 crackdown.
- **Voyager 1:** NASA confirms the farthest human-made object is now one
  light-day from Earth.
- **Game business:** GTA 6 launch-week sales pass $1.8 billion, topping
  The Odyssey's global box-office run.
- **Strip:** Cyclone Akvan — 300,000 evacuated in Odisha; Anthropic's
  $81.3B IPO, the largest on record.
- **Ticker:** Houthi attack on a Riyadh tower, Van Gogh selling for a
  record $190.4M, Hayabusa2's engine trouble ending its asteroid landing,
  Taiwan steadying its stocks, South Korea's exports topping $1 trillion,
  Genoa airport halted by drones.

---

<sub>Entered on [make.fun](https://make.fun/?ref=jm7qvfrf&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
