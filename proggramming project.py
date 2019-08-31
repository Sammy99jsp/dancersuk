import json
import random

def coupleById(i):
    d = getDataFile()
    a = list(filter(lambda c: c['id'] == i, d['couples']))[0]
    return a

def tieBreakerCore(a, x, name="Tiebreaker"):
    d = getDataFile()
    gone = []
    acquitted = []
    temp = list(filter(lambda c: c['total'] == x, a))
    r = {"name": name, "scores": [], "tiebreaker": 1}
    #Find Duplicates
    if len(temp) > 1:
        #Shuffle Randomly for Tournament
        while len(temp) > 1:
            random.shuffle(temp)
            c1 = temp.pop(0)
            c2 = temp.pop(0)
            t_1 = 0
            t_2 = 0

            print("━"*32)
            print("Tiebreaker!")
            print("━"*32)
            
            print(coupleById(c1['id'])['name'] + " vs " + coupleById(c2['id'])['name'] + "!")
            print("═"*20)
            print("Enter Judges Scores for", coupleById(c1['id'])['name'])
            r['scores'].append({"couple": c1['id'], "scores": []})
            for jI, jE in enumerate(d['judges']):
                sc = valScore(jE['name'])
                t_1 += sc
                r['scores'][0]['scores'].append({"judge": jE['id'], "score": sc})

            print("═"*20)
            r['scores'].append({"couple": c2['id'], "scores": []})            
            print("Enter Judges Scores for", coupleById(c2['id'])['name'])
            for jI, jE in enumerate(d['judges']):
                sc = valScore(jE['name'])
                t_2 += sc
                r['scores'][1]['scores'].append({"judge": jE['id'], "score": sc})
            
            print("═"*20)
            
            if t_1 > t_2:
                print(coupleById(c1['id'])['name'], "wins!")
                acquitted.append(c1)
                temp.append(c2)
            elif t_1 < t_2:
                print(coupleById(c2['id'])['name'], "wins!")
                acquitted.append(c2)
                temp.append(c1)
            else:
                print("Another f***ing tie...\nYou B******s can't do anything right...")
                temp.append(c1)
                temp.append(c2)
            d['rounds'].append(r)
    saveDataFile(d)
    gone.append(temp[0])
    
    return {"gone": gone, "acquitted": acquitted}
        
                

#Doesn't remove other tie participant if only one wins
def tieBreaker(a, OUT=2, name="Tiebreaker",):
    d = getDataFile()
    t = []
    r = []
    for x in list(dict.fromkeys(list(map(lambda c: c['total'], sorted(a, key=lambda c: c['total'])))))[:OUT]:
        r = []
        if len(t) >= OUT:
            break
        
        _ = tieBreakerCore(a, x, name)
        t.append(_['gone'][0])
        r.append(_['gone'] + _['acquitted'])
        i = 1
        while OUT > len(t) and len(_['acquitted']) > 0:
            _ = tieBreakerCore(_['acquitted'], x, name + " #" + str(i))
            t.append(_['gone'][0])
            r.append(_['gone'] + _['acquitted'])
            i += 1
    
    return t
def getDataFile():
    try:
        f = open("data.json")
        c = f.read()
        j = json.loads(c)
        f.close()
        return j
    except FileNotFoundError:
        print("Data file not found!")
        print("Entering setup!")
        setup()
    except json.decoder.JSONDecodeError:
        print("Data file corrupted!")
        print("Entering setup!")
        setup()
         
def saveDataFile(data):
    c = json.dumps(data)
    f = open("data.json", 'w')
    f.write(c)
    f.close()

def setup():
    print("━"*32)
    print("SETUP MODE")

    d = {"rounds": [], "judges": [], "couples": []}
    
    print("Enter Judges:")
    
    for i in range(5):
        d['judges'].append({"id" : i, "name": input("Judge #" + str(i + 1) + ": "), "scoring": []})

    couples = []
    print("Enter Couples")

    for i in range(6):
        d['couples'].append({"name": input("Couple #" + str(i + 1) + ": "), "id": i, "scores": [], "out": -1})

    saveDataFile(d)
    menu()

def options(o, p=False, n="Option"):
    # ["Name", "Name2"]
    for i, x in enumerate(list(map(lambda c: c[0], o))):
        print(n, "#" + str(i + 1) + ":", x)

    l = 0
    sel = -1
    while  sel < 0 or sel > len(o):
        try:
            if l == 0:
                sel = int(input("Selection: "))
            else:
                sel = int(input("Try Again: "))
                
        except ValueError:
            print("Not a number!")

        l += 1
    if p:
        return sel -1
    else:
        o[sel -1][1]()

def eScores():
    d = getDataFile()
    print("━"*32)
    print("Enter Scores")
    if(len(list(filter(lambda c: c['out'] == -1, d['couples']))) > 1):
        print(list(filter(lambda c: c['out'] == -1, d['couples']))[0]['name'], "has won Dancers UK!")
        return
    
    r = len(list(filter(lambda c: c['tiebreaker'] == 0, d['rounds'])))
    print("Round", "#" + str(r + 1))
    hel = 0
    t = []
    for jI, jE in enumerate(d['judges']):
            d['judges'][jI]['scoring'].append({"round": r, "scoring": []})
            hel = len(d['judges'][jI]['scoring']) -1
    for cI, cE in enumerate(list(filter(lambda c: c['out'] == -1, d['couples']))):
        score = []
        print("═"*20)
        print(cE['name'] + "'s scores:")
        for jI, jE in enumerate(d['judges']):
            sc = valScore(jE['name'])
            score.append({"score": sc, "judge": jE['id']})
            d['judges'][jI]['scoring'][hel]['scoring'].append({"score": sc, "couple": cE['id']})
            
        print("Total Score:", sum(list(map(lambda x: x['score'], score))))
        
        d['couples'][cE['id']]['scores'].append({"round": r, "scores": score})
        t.append({"couple": cE['id'], "scores": score})
    d['rounds'].append({"name": "Round" + " #" + str(r + 1), "scores": t, "tiebreaker": 0})
    saveDataFile(d)
    print("━"*32)
    print()
    print("[Adjudication Process]")
    print()
    specal = list(map(lambda c: {"id": c['couple'], "total": sum(list(map(lambda c1: c1['score'], c['scores'])))}, t))
    if len(list(map(lambda c: {"id": c['couple'], "total": sum(list(map(lambda c1: c1['score'], c['scores'])))}, t))) > 2:
        to_remove = tieBreaker(specal, 2,"Round #" + str(r + 1) + " Tiebreaker")
    else:
        to_remove = tieBreaker(specal, 1,"Round #" + str(r + 1) + " Tiebreaker")

    print("━"*32)
    print(" and ".join(list(map(lambda c: coupleById(c['id'])['name'], to_remove))), "have been eliminated!")
    
    for ss in to_remove:
        d['couples'][ss['id']]['out'] = r
    saveDataFile(d)
    menu()
def valScore(j):
    s = -1
    l = 0
    while not (s > 0 and s < 11):
        try:
            if l == 0:
                s = int(input("Score from " + j + ": "))
            else:
                s = int(input("Try Again: "))
        except ValueError:
            s = -1
        l += 1
    return s
def vScores():
    #
    return

def jPer():
    #
    return

def menu():
    print("━"*32)
    print("Main Menu")
    
    getDataFile()
    f = [["Setup", setup], ["Enter Scores", eScores], ["View Scores", vScores], ["Judge Performance", jPer], ["Quit", quit]]
    options(f)

    
    
print("━"*32)
print("Welcome to Dancers UK!")
menu()

