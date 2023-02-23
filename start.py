from display import *

seeds = 20
times = 1
method = 2
cut = 5

if method == 1:
    if os.path.isdir("results/naive/"):
        shutil.rmtree("results/naive/")
    os.makedirs("results/naive/")
elif method == 2:
    if os.path.isdir("results/globalNaive/"):
        shutil.rmtree("results/globalNaive/")
    os.makedirs("results/globalNaive/")

note = {}
wins = {i: 0 for i in range(seeds)}
loss = {i: 0 for i in range(seeds)}
for i in range(seeds):
    for j in range(times):
        d = Display(i, method, cut)
        note[i] = d.mainLoop()
        if note[i][-1]["state"] == "gamewin":
            wins[i] += 1
        else:
            loss[i] += 1

# print(wins)
# print(loss)
print(sum(wins.values()) / (sum(wins.values()) + sum(loss.values())))


from render import *

render = render()


def rend(note):
    for s in note.keys():
        for i in range(len(note[s])):
            render.gameStageDrawAuto(note[s][i], s, i, method)


rend(note)
