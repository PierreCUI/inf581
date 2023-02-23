import time
import numpy as np
from scipy.special import comb


class globalNaive:
    def __init__(self, info, cut):
        self.info = info

        self.height = info["StageConfig"].height
        self.width = info["StageConfig"].width
        self.mineNumber = info["StageConfig"].mineNumber
        self.doFirstFlip = info["StageConfig"].doFirstFlip

        self.mineField = info["mineField"]
        self.state = "start"
        self.infoState = info["state"]
        self.restMine = info["restMine"]

        self.possibleMineField = np.copy(self.mineField)
        self.unknown = np.ones(shape=(self.height, self.width))
        self.allUnknown = np.ones(shape=(self.height, self.width))
        self.possibility = np.zeros(shape=(self.height, self.width))

        self.cut = cut

    def decision(self, info):
        np.random.seed(int(time.time()))
        self.mineField = info["mineField"]
        self.possibility = np.zeros(shape=(self.height, self.width))
        self.restMine = info["restMine"]

        if not self.doFirstFlip and self.state == "start":
            self.state = self.infoState
            return [[1, np.random.randint(low=0, high=self.height), np.random.randint(low=0, high=self.width)]]
        self.state = self.infoState

        if not self.restMine:
            allRestPosition = []
            for i in range(self.height):
                for j in range(self.width):
                    if self.mineField[i][j] == '':
                        allRestPosition.append([1, i, j])
            return allRestPosition

        restAction = []
        for i in range(self.height):
            for j in range(self.width):
                if '1' <= self.mineField[i][j] <= '9':
                    closeBlocks = self.getAllCloseBlock(i, j)
                    contentBlocks = [self.mineField[i][j] for i, j in closeBlocks]
                    if '' in contentBlocks:
                        if contentBlocks.count('*') == int(self.mineField[i][j]):
                            restAction.append([3, i, j])
                            for i0, j0 in closeBlocks:
                                if self.mineField[i0][j0] == '':
                                    restAction.append([1, i0, j0])
        if restAction:
            return restAction

        allUncertainNumber = []
        for i in range(self.height):
            for j in range(self.width):
                if '1' <= self.mineField[i][j] <= '9':
                    availablePosition, lack = self.checkNumber(i, j)
                    if lack:
                        if len(availablePosition) == lack:
                            allDecision = []
                            for l in range(lack):
                                if self.mineField[availablePosition[l][0]][availablePosition[l][1]] == '':
                                    allDecision.append([2, availablePosition[l][0], availablePosition[l][1]])
                                    self.restMine -= 1
                            for l in range(lack):
                                for b in self.getAllCloseBlock(availablePosition[l][0], availablePosition[l][1]):
                                    if '1' <= self.mineField[b[0]][b[1]] <= '9':
                                        allDecision.append([3, b[0], b[1]])
                            return allDecision
                        else:
                            if availablePosition:
                                allUncertainNumber.append([i, j])

        for i0 in range(self.height):
            for j0 in range(self.width):
                if self.mineField[i0][j0] != '':
                    self.allUnknown[i0][j0] = False
        for i0 in allUncertainNumber:
            for j0 in self.getAllCloseBlock(i0[0], i0[1]):
                self.allUnknown[j0[0]][j0[1]] = False

        if not allUncertainNumber:
            if self.restMine:
                while True:
                    i, j = np.random.randint(low=0, high=self.height), np.random.randint(low=0, high=self.width)
                    if self.mineField[i][j] == '':
                        return [[2, i, j]]
            else:
                while True:
                    i, j = np.random.randint(low=0, high=self.height), np.random.randint(low=0, high=self.width)
                    if self.mineField[i][j] == '':
                        return [[1, i, j]]

        allUncertainDecision = []
        allUncertainPossibility = []
        for i, j in allUncertainNumber:
            decisionPossibility = self.globalDecision(i, j)
            allUncertainDecision.append(decisionPossibility[0])
            allUncertainPossibility.append(decisionPossibility[1])
            if decisionPossibility[1] > 1 - 1.0e-15:
                break
        return allUncertainDecision[allUncertainPossibility.index(np.max(allUncertainPossibility))]

    def globalDecision(self, i, j):
        self.possibility = np.zeros(shape=(self.height, self.width))
        self.possibleMineField = np.copy(self.mineField)
        self.unknown = np.ones(shape=(self.height, self.width))

        allRelativeNumber = [[i, j]]
        relativeNumber = [[i, j]]
        allRelativeEmpty = []
        relativeEmpty = []
        allPossibleSolution = []

        while relativeEmpty or relativeNumber:
            for k in relativeNumber:
                for m in self.getAllCloseEmpty(k[0], k[1]):
                    if m not in allRelativeEmpty:
                        relativeEmpty.append(m)
                        allRelativeEmpty.append(m)
            relativeNumber = []
            if len(allRelativeNumber) >= self.cut:
                break
            for k in relativeEmpty:
                for m in self.getAllCloseNumber(k[0], k[1]):
                    if len(allRelativeNumber) < self.cut:
                        if self.getAllCloseEmpty(m[0], m[1]):
                            if m not in allRelativeNumber:
                                relativeNumber.append(m)
                                allRelativeNumber.append(m)
                    else:
                        break
                if len(allRelativeNumber) >= self.cut:
                    break
            relativeEmpty = []

        mineList = [0 for _ in allRelativeEmpty]
        for k in range(1, min(len(allRelativeEmpty) + 1, self.restMine + 1)):
            for m in range(k):
                mineList[m] = 1
            while mineList != -1:
                possibleMinePosition = [allRelativeEmpty[m] for m in range(len(mineList)) if mineList[m]]
                self.possibleMineField = np.copy(self.mineField)
                for p in possibleMinePosition:
                    self.possibleMineField[p[0]][p[1]] = '?'
                possibleResult = True
                for p in allRelativeNumber:
                    if int(self.possibleMineField[p[0]][p[1]]) != len(self.getAllClosePossibleMine(p[0], p[1])):
                        possibleResult = False
                        break
                if possibleResult:
                    allPossibleSolution.append(possibleMinePosition)
                mineList = self.getNextList(mineList)
            mineList = [0 for _ in allRelativeEmpty]

        self.unknown = np.ones(shape=(self.height, self.width))
        for i0 in range(self.height):
            for j0 in range(self.width):
                if self.mineField[i0][j0] != '':
                    self.unknown[i0][j0] = False
        for p0 in allRelativeEmpty:
            self.unknown[p0[0]][p0[1]] = False

        amountPossible = {}
        amountLen = {}
        Couts = {}
        for p in allPossibleSolution:
            if len(p) not in amountPossible:
                Cout, amountPossible[len(p)] = self.getAmountPossible(len(allRelativeEmpty), int(np.round(np.sum(self.unknown))), len(p), self.restMine - len(p))
                Couts[len(p)] = Cout
                amountLen[len(p)] = 0
            amountLen[len(p)] += 1
        sumValue = np.sum(list(amountPossible.values()))
        for p in amountPossible:
            if sumValue:
                amountPossible[p] /= sumValue
        Cout = 0
        for p in Couts:
            Cout += Couts[p] * amountPossible[p]
        for p in amountPossible:
            amountPossible[p] /= amountLen[p]
        for p in allPossibleSolution:
            for q in p:
                self.possibility[q[0]][q[1]] += amountPossible[len(p)]

        for k in allRelativeEmpty:
            if self.possibility[k[0]][k[1]] < 1.0e-15:
                return [[1, k[0], k[1]]], 1.0
        ij_min, minPossibility = [-1, -1], 1.0
        for k in allRelativeEmpty:
            if self.possibility[k[0]][k[1]] < minPossibility:
                ij_min = k
                minPossibility = self.possibility[ij_min[0]][ij_min[1]]

        i_maxp, j_maxp = np.where(self.possibility == np.max(self.possibility))
        minDistance = self.height + self.width
        i0, j0 = -1, -1
        for l in range(len(i_maxp)):
            dist = abs(i_maxp[l] - i) + abs(j_maxp[l] - j)
            if dist < minDistance:
                minDistance = dist
                i0, j0 = i_maxp[l], j_maxp[l]
        i, j = i0, j0

        if np.sum(self.allUnknown) < 1:
            if np.max(self.possibility) >= 1 - minPossibility:
                self.restMine -= 1
                allDecision = [[2, i, j]]
                allDecision += [[3, b[0], b[1]] for b in self.getAllCloseNumber(i, j)]
                return allDecision, np.max(self.possibility)
            else:
                return [[1, ij_min[0], ij_min[1]]], 1 - minPossibility

        allPossibleAction = [np.max(self.possibility), 1 - minPossibility, Cout, 1 - Cout]
        if np.max(self.possibility) == np.max(allPossibleAction):
            self.restMine -= 1
            allDecision = [[2, i, j]]
            allDecision += [[3, b[0], b[1]] for b in self.getAllCloseNumber(i, j)]
            return allDecision, np.max(self.possibility)
        elif 1 - minPossibility == np.max(allPossibleAction):
            return [[1, ij_min[0], ij_min[1]]], 1 - minPossibility
        elif Cout == np.max(allPossibleAction):
            while True:
                i, j = np.random.randint(low=0, high=self.height), np.random.randint(low=0, high=self.width)
                if self.allUnknown[i][j]:
                    return [[1, i, j]], Cout
        elif 1 - Cout == np.max(allPossibleAction):
            while True:
                i, j = np.random.randint(low=0, high=self.height), np.random.randint(low=0, high=self.width)
                if self.allUnknown[i][j]:
                    return [[2, i, j]], 1 - Cout

    def checkNumber(self, i, j):
        lack = int(self.mineField[i][j])
        availablePosition = []
        for b in self.getAllCloseBlock(i, j):
            if self.mineField[b[0]][b[1]] == '':
                availablePosition.append(b)
            elif self.mineField[b[0]][b[1]] == '*':
                lack -= 1
        return availablePosition, lack

    def getAllCloseBlock(self, i, j):
        blockList = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if not di and not dj:
                    continue
                if i + di < 0 or i + di >= self.height:
                    continue
                if j + dj < 0 or j + dj >= self.width:
                    continue
                blockList.append([i + di, j + dj])
        return blockList

    def getAllCloseNumber(self, i, j):
        blockList = self.getAllCloseBlock(i, j)
        numberList = []
        for b in blockList:
            if '1' <= self.mineField[b[0]][b[1]] <= '9':
                numberList.append(b)
        return numberList

    def getAllCloseEmpty(self, i, j):
        blockList = self.getAllCloseBlock(i, j)
        emptyList = []
        for b in blockList:
            if self.mineField[b[0]][b[1]] == '':
                emptyList.append(b)
        return emptyList

    def getAllCloseMine(self, i, j):
        blockList = self.getAllCloseBlock(i, j)
        closeMineList = []
        for b in blockList:
            if self.mineField[b[0]][b[1]] == '*':
                closeMineList.append(b)
        return closeMineList

    def getAllClosePossibleMine(self, i, j):
        blockList = self.getAllCloseBlock(i, j)
        possibleMineList = []
        for b in blockList:
            if self.possibleMineField[b[0]][b[1]] == '*' or self.possibleMineField[b[0]][b[1]] == '?':
                possibleMineList.append(b)
        return possibleMineList

    def getNextList(self, prelist):
        back = 0
        position = len(prelist) - 1
        while position != -1 and prelist[position] != 0:
            back += 1
            position -= 1
        while position != -1 and prelist[position] == 0:
            position -= 1

        if position == -1:
            return -1

        prelist[position] = 0
        prelist[position + 1] = 1
        for k in range(position + 2, position + back + 2):
            prelist[k] = 1
        for k in range(position + back + 2, len(prelist)):
            prelist[k] = 0

        return prelist

    def getAmountPossible(self, insideEmpty, outsideEmpty, insideMine, outsideMine):
        if outsideEmpty < outsideMine:
            return 1, 0
        if outsideEmpty == 0:
            return 1, 1
        if outsideMine < 0:
            return 0, 0

        Cin = comb(insideEmpty, insideMine)
        Cout = comb(outsideEmpty, outsideMine)
        Call = comb(insideEmpty + outsideEmpty, insideMine + outsideMine)

        return max(0, 1 - outsideMine / outsideEmpty), Cin * Cout / Call
