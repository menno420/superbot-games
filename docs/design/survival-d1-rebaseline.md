# Survival overlay — D1 re-baseline against shipped per-game energy

> **Status:** `reference` — resolves a factual contradiction in the survival plan's D1
> row created by energy shipping after the plan was written. Presents both options and
> recommends one (⚑ decide-and-flag). Verified against superbot@shipped and
> superbot-next@main.

## 1. Why this doc exists

The survival difficulty plan
(superbot `docs/planning/rpg-survival-difficulty-design-2026-06-10.md`) pins **D1**:

> **"Easy ≡ the base game, byte-identical"** — the whole overlay is a pure addition
> behind the player's choice, and Easy has **no energy at all**.

That premise was true when D1 was written. It is now **self-contradictory**, because
energy has since shipped as part of the base game.

## 2. The facts (verified)

### superbot shipped TWO SEPARATE per-game energy bars on 2026-06-22 — not a universal one

- **Mining energy** — `mining_player_state.energy` / `energy_updated_at` (migration
  086). Cap **60**, cost **1/dig**, regen **+1 / 10s** (360/hr). **Lazy-clock**
  (value + timestamp, no background ticker; the current value is derived from the
  timestamp on read). Refilled by food / boosters.
- **Fishing energy** — a **new** `fishing_energy` table (migration 088). Cap **60**,
  cost **2/cast**, regen **+1 / 30s** (120/hr). Same lazy-clock math, **its own
  tunables**.
- **Campfire cooking** — requires a built Campfire (`!build campfire`); converts caught
  fish → a `cooked fish` item; eating restores **+30 MINING energy**. This **already
  implements the survival plan's D3 "cook at the campfire" row.**
- The owner **explicitly DECOUPLED the two bars**: *"a separate bar from mining… rule of
  three: if a third energy system appears, extract a shared settle/spend core."* There
  is **no universal energy bar** — there are two per-game bars with independent tunables.

### superbot-next has NOT ported energy

- Energy is **deferred in the rebuild** (tracked in superbot-next's own decision ledger;
  recorded locally as [D-0004]). The rebuilt bot currently
  runs mining/fishing at the **pre-energy STARTER baseline** (no energy consumed) and
  has **no survival / difficulty contract at all** yet.

## 3. The contradiction

D1 said *"Easy = no energy, byte-identical to the base game."* Since energy now ships
for **both** mining and fishing, **"byte-identical to today's game" now INCLUDES
energy.** So the two halves of the D1 premise fight each other:

- "byte-identical to the base game" now **requires** the shipped per-game energy bars, but
- "Easy = no energy at all" **removes** them.

Both cannot hold. D1 must be re-baselined.

## 4. Options

### (a) Byte-identical wins — **RECOMMENDED**

- **Easy = today's shipped per-game bars**, unchanged: mining **60 / 1 per dig / +1 per
  10s**; fishing **60 / 2 per cast / +1 per 30s**.
- The survival **Energy axis only MODIFIES those existing bars** for **Medium / Hard**
  (tighter caps, higher costs, slower regen) — it does **not** introduce a separate
  global bar.
- **Rationale:** preserves the byte-identical pin (Easy is provably the shipped game),
  avoids a **third** energy system (honors the owner's rule-of-three), and the shipped
  campfire loop already satisfies D3. Difficulty then differentiates on the *other* axes
  (health / hunger / encounters / death / loot), with energy as a per-game modifier.

### (b) Unlimited wins

- **Easy explicitly disables** the shipped bars (no energy consumed on Easy).
- **Cost:** Easy is then **NOT byte-identical** to the shipped game, so **the pin test
  must be dropped.** This reopens a settled property and diverges Easy from what players
  already run today.

## 5. Two structural notes

- **D2 incompatibility.** The plan's **D2 "global cap-10 survival energy"** is
  **incompatible** with two cap-**60** per-game bars — a single cap-10 global bar cannot
  wrap two independent cap-60 bars without either breaking byte-identical Easy or
  silently retuning both games. **Recommend** the survival overlay **retunes / wraps the
  EXISTING per-game bars** (via the owner's rule-of-three: *extract a shared settle/spend
  core* the two bars share, then let difficulty scale each game's tunables through it)
  rather than adding a third global bar.
- **Clean insertion point in superbot-next.** Because superbot-next **still defers the
  energy port**, the cheapest correct path is to **bake the difficulty-aware energy
  contract INTO that deferred energy port** — port energy *once*, already difficulty-aware,
  rather than porting flat 60-cap bars and then re-porting them to add difficulty. The
  shared settle/spend core (rule-of-three) is the natural home for the difficulty
  multiplier.

## 6. Recommendation

**⚑ decide-and-flag — recommend option (a).** Re-baseline D1 to:

> **"Easy ≡ today's shipped per-game energy bars (mining 60/1/10s, fishing 60/2/30s);
> the survival Energy axis only modifies those existing bars for Medium/Hard. No third
> global energy bar — extract a shared settle/spend core (rule-of-three) and scale each
> game's tunables through it. In superbot-next, bake this difficulty-aware contract into
> the rebuild's deferred energy port rather than re-porting flat bars."**

This keeps the byte-identical pin meaningful, honors the owner's explicit decoupling +
rule-of-three, reuses the shipped campfire (D3), and gives the rebuild a single clean
energy port instead of two.
