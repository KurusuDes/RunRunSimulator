import sys, random, statistics as st

MINERITA_PER_MATERIAL = 5
HATCH_COST = 10
BREEDING_ROOM = 20
START_MINERITA = 30
EGGS = 5
TO_EVOLVE = 3
BUFF_EVERY = 3
TEAM = 3

RULES = {
    'V0 actual': dict(keep_on_loss=0.0, banked=False, credit_on_loss=False),
    'V1 pisos asegurados': dict(keep_on_loss=0.0, banked=True, credit_on_loss=False),
    'V2 cuenta al volver': dict(keep_on_loss=0.0, banked=False, credit_on_loss=True),
    'V3 mitad + cuenta': dict(keep_on_loss=0.5, banked=True, credit_on_loss=True),
}


def floor_result(rng, mu, sd, buff, buff_mu):
    if buff:
        return 'win', max(0, round(rng.gauss(buff_mu, buff_mu * 0.25)))
    me = max(0, round(rng.gauss(mu, sd)))
    them = max(0, round(rng.gauss(mu, sd)))
    if me > them:
        return 'win', me
    if me == them:
        return 'tie', me
    return 'loss', me


def run(rng, floors, rule, mu, sd, buff_mu):
    banked, current, lost = 0, 0, False
    for n in range(1, floors + 1):
        res, mat = floor_result(rng, mu, sd, n % BUFF_EVERY == 0, buff_mu)
        if res == 'loss':
            lost = True
            kept = banked if rule['banked'] else 0
            lost_part = (banked + mat) - kept
            return lost, kept + int(lost_part * rule['keep_on_loss'])
        banked += mat
    return lost, banked


def campaign(seed, rule, floors, mu, sd, buff_mu, max_nights=60):
    rng = random.Random(seed)
    genders = [rng.random() < 0.5 for _ in range(EGGS)]
    if all(genders) or not any(genders):
        genders[0] = not genders[0]
    eggs = list(range(EGGS))
    slimes, adults = {}, set()
    minerita = START_MINERITA
    room = False
    zero_nights, streak, worst = 0, 0, 0
    for i in eggs[:]:
        if minerita >= HATCH_COST:
            minerita -= HATCH_COST
            slimes[i] = 0
            eggs.remove(i)
    for night in range(1, max_nights + 1):
        team = sorted(slimes, key=lambda k: -slimes[k])[:TEAM]
        if len(team) < TEAM:
            team += [a for a in adults][:TEAM - len(team)]
        lost, mat = run(rng, floors, rule, mu, sd, buff_mu)
        gain = mat * MINERITA_PER_MATERIAL
        minerita += gain
        if gain == 0:
            zero_nights += 1
            streak += 1
            worst = max(worst, streak)
        else:
            streak = 0
        if not lost or rule['credit_on_loss']:
            for k in team:
                if k in slimes:
                    slimes[k] += 1
                    if slimes[k] >= TO_EVOLVE:
                        del slimes[k]
                        adults.add(k)
        while eggs and minerita >= HATCH_COST:
            minerita -= HATCH_COST
            slimes[eggs.pop(0)] = 0
        if not room and minerita >= BREEDING_ROOM and not eggs:
            minerita -= BREEDING_ROOM
            room = True
        pair = any(genders[a] for a in adults) and any(not genders[a] for a in adults)
        if pair and room and minerita >= HATCH_COST:
            return dict(nights=night, minerita=minerita - HATCH_COST, zero=zero_nights, worst=worst)
    return dict(nights=max_nights, minerita=minerita, zero=zero_nights, worst=worst)


def ev_per_night(rule, floors, mu, sd, buff_mu, n=40000):
    rng = random.Random(1)
    tot, lost = 0, 0
    for _ in range(n):
        l, m = run(rng, floors, rule, mu, sd, buff_mu)
        tot += m * MINERITA_PER_MATERIAL
        lost += l
    return tot / n, lost / n


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def main():
    mu = float(sys.argv[1]) if len(sys.argv) > 1 else 14
    sd = float(sys.argv[2]) if len(sys.argv) > 2 else 6
    buff_mu = float(sys.argv[3]) if len(sys.argv) > 3 else 27
    print(f'material por piso ~N({mu},{sd}) jugador y rival; piso de buffo ~{buff_mu}')
    print()
    print('Minerita esperada por noche y % de bajadas perdidas')
    print(f'{"regla":22s}' + ''.join(f'{"hasta piso " + str(f):>22s}' for f in (1, 2, 3, 4, 6)))
    for name, rule in RULES.items():
        row = ''
        for f in (1, 2, 3, 4, 6):
            ev, lo = ev_per_night(rule, f, mu, sd, buff_mu)
            row += f'{ev:12.0f} ({lo * 100:3.0f} %)    '
        print(f'{name:22s}' + row)
    print()
    print('Noches hasta la primera cria (pareja adulta + breeding room + 10 para eclosionar), 4000 partidas')
    print(f'{"regla / estrategia":34s}{"mediana":>8s}{"p90":>6s}{"max":>6s}{"noches en 0":>13s}{"peor racha":>12s}{"Minerita sobrante":>19s}')
    for name, rule in RULES.items():
        for floors in (1, 3):
            res = [campaign(s, rule, floors, mu, sd, buff_mu) for s in range(4000)]
            nights = [r['nights'] for r in res]
            print(f'{name + " · piso " + str(floors):34s}{st.median(nights):8.0f}{pct(nights, 0.9):6d}{max(nights):6d}'
                  f'{st.mean(r["zero"] for r in res):13.1f}{st.mean(r["worst"] for r in res):12.1f}{st.median(r["minerita"] for r in res):19.0f}')


if __name__ == '__main__':
    main()
