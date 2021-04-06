from copy import copy


class Graph:
    def __init__(self):
        self.connections = []
        self.involved = set()

    def connect(self, x, y):
        if [x, y] not in self.connections and [y, x] not in self.connections:
            self.connections.append([x, y])
            self.involved.add(x)
            self.involved.add(y)
        else:
            print('connection already in graph')

    def __repr__(self):
        return str(self.connections)

    @property
    def involvedObjects(self):
        return sorted(self.involved, key=lambda x: x.name)

    def isConnect(self, x, y):
        if [x, y] in self.connections or [y, x] in self.connections:
            return True

    def allConnected(self, x):
        temp = [i for i in self.connections if x in i]
        result = []
        for i in temp:
            result.append(i[1] if i[0] is x else i[0])
        return result

    def disconnect(self, x, y):
        if [x, y] in self.connections:
            self.connections.remove([x, y])
        elif [y, x] in self.connections:
            self.connections.remove([y, x])

    def groups(self):
        result = []
        temp = copy(self.involved)

        while len(temp) != 0:
            first = list(temp)[0]
            newGroup = [first]

            toBeContinued = True
            while toBeContinued:
                toBeContinued = False
                for i in newGroup:
                    for ii in self.allConnected(i):
                        if ii not in newGroup:
                            newGroup.append(ii)
                            toBeContinued = True
            result.append(newGroup)
            for i in newGroup:
                temp.remove(i)

        return result
