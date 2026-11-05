import json,sys
def fmt(v):
    if isinstance(v,(dict,list)): return json.dumps(v,ensure_ascii=False)
    return str(v)
def walk(n,depth=0):
    ind='  '*depth
    props=[]
    for k in ['type','width','height','x','y','layout','alignItems','justifyContent','gap','padding','cornerRadius','fills','fontSize','fontFamily','lineHeight','fontFill','textAlign','textAlignVertical','stroke','effects','clip']:
        if k in n and n[k] not in (None,''): props.append(f'{k}={fmt(n[k])}')
    if 'content' in n: props.append(f'content={fmt(n["content"])}')
    print(f'{ind}{n.get("name","?")} [{", ".join(props)}]')
    for c in n.get('children',[]): walk(c,depth+1)
f=sys.argv[1]
d=json.load(open(f))
inner=json.loads(d['content'][0]['text'])
for r in inner['result']:
    walk(r.get('layer_data',r))
