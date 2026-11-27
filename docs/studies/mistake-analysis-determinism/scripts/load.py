import json,glob,os,re
def load():
    rows=[]; bad=[]
    for f in sorted(glob.glob(os.path.dirname(__file__)+"/out/*.json")):
        k=os.path.basename(f)[:-5]; cfg,rep,b=k.rsplit("_",2)
        try: d=json.load(open(f))
        except Exception as e: bad.append(k); continue
        for g in d["games"]:
            for bot in ("jug_fix","rival_mimic"):
                for i,m in enumerate(g.get(bot,[])[:3]):
                    rows.append(dict(cfg=cfg,rep=int(rep[1:]),batch=b,game=g["game"],bot=bot,rank=m.get("rank",i+1),title=m.get("title",""),turns=str(m.get("turns","")),castles=m.get("castles",[]),desc=m.get("description","")))
    return rows,bad
