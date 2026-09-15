import json, sys, glob, os
d = os.path.expanduser('~/.claude/projects/-tmp-orchflows-e2e-firstmate')
f = sorted(glob.glob(d + '/*.jsonl'), key=os.path.getmtime)[-1]
out = ["# Captain transcript (extracted)", "", f"Source: `{f}` (Claude Code session transcript of the FirstMate primary; tool results omitted, tool inputs truncated).", ""]
n = 0; first_model = None
for line in open(f, encoding='utf-8', errors='replace'):
    try: r = json.loads(line)
    except Exception: continue
    t = r.get('type'); m = r.get('message') or {}
    ts = (r.get('timestamp') or '')[11:19]
    if t == 'assistant':
        if not first_model and m.get('model'): first_model = m['model']
        for c in m.get('content', []):
            if not isinstance(c, dict): continue
            if c.get('type') == 'tool_use':
                n += 1; inp = c.get('input', {}); name = c.get('name')
                if name == 'Bash': s = (inp.get('command') or '')
                elif name in ('Read', 'Write', 'Edit'): s = inp.get('file_path', '')
                else: s = json.dumps(inp)
                s = s.replace('\n', ' ⏎ ')
                if len(s) > 700: s = s[:700] + ' …'
                out.append(f"- **{n}** `{ts}` {name}: `{s}`")
            elif c.get('type') == 'text' and c.get('text', '').strip():
                out.append(""); out.append(f"> **Primary to captain** (`{ts}`):"); 
                for ln in c['text'].strip().splitlines(): out.append("> " + ln)
                out.append("")
    elif t == 'user':
        cont = m.get('content')
        if isinstance(cont, str) and cont.strip():
            if cont.startswith('Base directory for this skill:'):
                out.append(f"- *skill loaded from* `{cont.splitlines()[0].split(':',1)[1].strip()}`")
            else:
                out.append(""); out.append(f"**Captain** (`{ts}`): {cont.strip()[:600]}"); out.append("")
        elif isinstance(cont, list):
            for c in cont:
                if isinstance(c, dict) and c.get('type') == 'text':
                    txt = c.get('text', '')
                    if 'Stop hook' in txt or 'wake' in txt.lower()[:200]:
                        out.append(f"- *wake* `{ts}`: {txt[:240].replace(chr(10), ' | ')}")
                    elif txt.strip() and not txt.startswith('<'):
                        out.append(""); out.append(f"**Captain** (`{ts}`): {txt.strip()[:600]}"); out.append("")
out.insert(3, f"Model: `{first_model}`. Tool calls: {n}.")
print("\n".join(out))
