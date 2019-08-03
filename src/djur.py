# coding: utf-8
import json
import pathlib


DBPATH = 'djur.json'


def save(db):
    try:
        pathlib.Path(DBPATH).write_text(json.dumps(db, indent=2))
    except:
        print(f"Kunde inte spara filen {DBPATH} :(")


def djur(db, _input=None, _print=None, _save_db=None):
    prn = _print or print
    _inp = _input or input
    save_db = _save_db or save

    def inp():
        print(">>> ", end='')
        ans = _inp().lower()
        return ans[0] if len(ans) > 0 else ' '

    def full_inp():
        print(">>> ", end='')
        return _inp()

    prn("Välkommen till GISSA DJUR!")
    prn("--------------------------")
    while True:
        antal = count(db)
        prn(f"Jag känner till {antal} djur.")
        prn("(S)pela eller (A)vsluta? Tryck S eller A och sedan Enter.")
        ans = inp()
        if ans == 'a':
            prn("Tack för att du spelade!")
            return
        elif ans == 's':
            prn("Tänk på ett djur, så ska jag gissa vilket du tänker på!")
            prn("När du tänkt klart, skriv (K)lart.")
            while inp() != 'k':
                prn("Va? Skriv k när du är klar!")
            prn("OK då kör vi...")
            pos = db
            # Questions are 4 length tuples!
            while len(pos) == 4:
                question = format_question(pos[0])
                prn(f"{question} Svara med (J)a eller (N)ej.")
                go_left = confirm(full_inp, prn)
                go_left = go_left if pos[1] else not go_left
                if go_left:
                    pos = pos[2]
                else:
                    pos = pos[3]
            djur = format_animal(pos[0])
            prn(f"Jag gissar att du tänkte på {djur}!")
            prn("Hade jag rätt? (J)a eller (N)ej?")
            if confirm(full_inp, prn):
                prn("Vad kul! :D :D :D")
            else:
                prn("OK, men vilket djur tänkte du på då?")
                new_djur = format_animal(full_inp())
                prn(f"Kom på en fråga som innehåller ordet 'djuret',")
                prn(f"som skiljer {new_djur} och {djur} åt.")
                prn("T.ex. 'Kan djuret simma?'")
                while True:
                    new_question = format_question(full_inp())
                    if 'djuret' not in new_question:
                        prn("Snälla ta med ordet 'djuret' i frågan!")
                        prn("Försök igen:")
                    else:
                        break
                readable_question = new_question.replace("djuret", new_djur)
                prn(f"OK, och för {new_djur} är svaret på frågan '{readable_question}' (J)a eller (N)ej?")
                ans = confirm(full_inp, prn)
                while True:
                    prn("Denna fråga lär jag mig då:")
                    prn(f"  {readable_question}")
                    prn(f"  Rätt svar: {swedish_bool(ans)}")
                    prn("Ser det rätt ut?")
                    yes = confirm(full_inp, prn)
                    if yes:
                        break
                    else:
                        prn("Hmm, tvärtom alltså?")
                        ans = not ans

                prn(f"Tack för att du lärt mig något om djuret {new_djur}!")
                pos[:] = [new_question, ans, [new_djur], [djur]]

                save_db(db)
        else:
            prn(f"Jag förstår inte '{ans}'!")


def confirm(_input=input, _print=print):
    while True:
        ans = _input().lower()
        if len(ans) > 0 and ans[0] in 'jn':
            return ans[0] == 'j'
        else:
            _print("Jag förstår bara svenska; (J)a eller (N)ej?")


def find_leaves(db):
    if len(db) == 1:
        yield db[0]
    else:
        for leaf in find_leaves(db[2]):
            yield leaf
        for leaf in find_leaves(db[3]):
            yield leaf


def find_nodes(db):
    if len(db) == 4:
        yield db[0]
        for node in find_nodes(db[2]):
            yield node
        for node in find_nodes(db[3]):
            yield node


def format_animal(a):
    return a.lower().strip()


def format_question(q):
    words = q.split()
    q = words[0].title() + ' ' + ' '.join(words[1:])
    if not q.endswith('?'):
        q = q + '?'
    return q


def count(db):
    return len(list(find_leaves(db)))


def swedish_bool(b):
    return 'ja' if b else 'nej'


def dfs(db, cb):
    cb(db)
    if len(db) == 4:
        dfs(db[2], cb)
        dfs(db[3], cb)


def dotgraph(db):
    """Return a DOT compatible string representation of db"""
    labels = []
    dfs(db, lambda node: labels.append(node[0]))
    lbls = [f'n{num} [label="{s}"];\n' for (num, s) in enumerate(labels)]
    print(labels)
    edges = []
    def visit_node(node):
        if len(node) == 4:
            parent_ix = labels.index(node[0])
            lchild_ix = labels.index(node[2][0])
            rchild_ix = labels.index(node[3][0])
            edges.append((parent_ix, lchild_ix))
            edges.append((parent_ix, rchild_ix))
    dfs(db, visit_node)
    edges = [f'n{parent} -> n{child};\n' for (parent, child) in edges]
    print(edges)
    return "digraph djur {\n" + ''.join(lbls) + ''.join(edges) + "}"


if __name__ == '__main__':
    print("\n" * 100)
    try:
        db = json.loads(pathlib.Path(DBPATH).read_text())
    except:
        db = [
            'Kan djuret simma', True,
            ['gädda'],
            ['Krälar djuret', False, ['örn'], ['orm']]
        ]
    print(dotgraph(db))
    djur(db)
