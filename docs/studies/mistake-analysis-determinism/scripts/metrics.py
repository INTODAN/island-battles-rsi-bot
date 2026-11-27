import json,glob,re,itertools,collections,math,random
M=json.load(open('mistakes.json')); games={g['game']:g for g in json.load(open('games.json'))}
cat={}
for f in glob.glob('cls/*.json'): cat.update({int(k):v for k,v in json.load(open(f)).items()})
miss=[m['id'] for m in M if m['id'] not in cat]
print('unclassified',len(miss))
for m in M: m['cat']=cat.get(m['id'],'other')
CF=['opus-default','opus-medium','sonnet-high','fable-medium']
def span(t):
    n=[int(x) for x in re.findall(r'\d+',t)]
    return (min(n),max(n)) if n else None
runs=collections.defaultdict(list)  # (game,bot,cfg,rep) -> mistakes
for m in M: runs[(m['game'],m['bot'],m['cfg'],m['rep'])].append(m)
GB=sorted({(m['game'],m['bot']) for m in M})
def cats(g,b,c,r): return {m['cat'] for m in runs[(g,b,c,r)]}
def r1(g,b,c,r):
    L=sorted(runs[(g,b,c,r)],key=lambda m:m['rank']); return L[0]['cat'] if L else None
def jac(a,b): return len(a&b)/len(a|b) if a|b else 1
def spec(A,B):
    # fraction of mistakes in A that have a same-category, turn-overlapping (within 10) match in B
    hit=0
    for a in A:
        sa=span(a['turns'])
        for b in B:
            sb=span(b['turns'])
            if a['cat']==b['cat'] and sa and sb and sa[0]<=sb[1]+10 and sb[0]<=sa[1]+10: hit+=1;break
    return hit/len(A) if A else 0
def pair(c1,c2,gbs=GB,shuffle=False):
    J=[];R=[];P=[]
    for g,b in gbs:
        for r_1 in range(1,11):
            for r_2 in range(1,11):
                if c1==c2 and r_2<=r_1: continue
                g2=g
                if shuffle:
                    g2=random.choice([x for x,y in GB if y==b and x!=g])
                J.append(jac(cats(g,b,c1,r_1),cats(g2,b,c2,r_2)))
                R.append(r1(g,b,c1,r_1)==r1(g2,b,c2,r_2))
                if not shuffle: P.append(spec(runs[(g,b,c1,r_1)],runs[(g2,b,c2,r_2)]))
    av=lambda x:round(sum(x)/len(x),3) if x else None
    return av(J),av(R),av(P)
out={}
print('config pair | jaccard of top3 kinds | same #1 kind | specific-mistake match')
for c1,c2 in itertools.combinations_with_replacement(CF,2):
    out[(c1,c2)]=pair(c1,c2); print(c1,c2,out[(c1,c2)])
random.seed(0)
print('baseline (same config, different game):',pair('opus-default','opus-default',shuffle=True))
for bot in ('jug_fix','rival_mimic'):
    print(bot,'within-opus-default',pair('opus-default','opus-default',[x for x in GB if x[1]==bot]))
# variety
print()
for bot in ('jug_fix','rival_mimic'):
    c=collections.Counter(m['cat'] for m in M if m['bot']==bot); n=sum(c.values())
    H=-sum(v/n*math.log(v/n) for v in c.values())
    # consensus per game: category appearing in >=50% of the 40 runs
    cons=collections.Counter(); per_game=[]
    for g in games:
        k=collections.Counter()
        for cf in CF:
            for r in range(1,11): k.update(cats(g,bot,cf,r))
        cs=[x for x,v in k.items() if v>=20]; per_game.append(len(cs)); cons.update(cs)
    print(bot,'mistakes',n,'effective #kinds',round(math.exp(H),1),'kinds used',len(c))
    print('  share:',[(k,round(v/n,3)) for k,v in c.most_common(10)])
    print('  consensus kinds per game avg',round(sum(per_game)/len(per_game),2),'| games where kind is consensus:',cons.most_common(10))
    for o in ('win','draw','loss'):
        cc=collections.Counter(m['cat'] for m in M if m['bot']==bot and games[m['game']]['outcome_for_fix']==o); nn=sum(cc.values())
        print('   ',o,[(k,round(v/nn,2)) for k,v in cc.most_common(4)])
