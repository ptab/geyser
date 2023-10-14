class Graph:

    def __init__(self):
        self._edges = {}

    def add(self, from_vertex, to_vertex):
        if from_vertex == to_vertex:
            # ignore subprojects in multimodule libraries that depend on themselves
            pass
        else:
            if from_vertex in self._edges:
                if to_vertex:
                    self._edges[from_vertex].add(to_vertex)
                else:
                    pass
            elif to_vertex:
                self._edges[from_vertex] = {to_vertex}
            else:
                self._edges[from_vertex] = set()

            if to_vertex and to_vertex not in self._edges:
                self._edges[to_vertex] = set()

    def __str__(self):
        return str(self._edges)

    def __repr__(self):
        return str(self)

    def empty(self):
        return len(self._edges) == 0

    # implementation of https://en.wikipedia.org/wiki/Topological_sorting
    def next_round(self):
        ret = set()

        # process every key that has no value (i.e. a project without any direct dependency left to be updated)
        for (key, value) in self._edges.items():
            if not value:
                ret.add(key)

        # remove the projects to be returned from the map of _edges (shrink the map)
        for key in ret:
            self._edges.pop(key, None)
            for s in list(self._edges.values()):
                s.discard(key)

        if len(ret) == 0 and not self.empty():
            raise ValueError(
                f'Cyclic dependency detected! This should have been caught earlier, something\'s wrong. Here\'s the current state of the graph, good luck debugging it: {self._edges}')
        else:
            return ret

    # implementation of https://en.wikipedia.org/wiki/Depth-first_search
    def find_cycles(self):
        visited = set()
        cycles = []

        def _find_cycle(vertex, path):
            visited.add(vertex)
            path.append(vertex)

            for to_vertex in self._edges[vertex]:
                if to_vertex not in visited:
                    cycle = _find_cycle(to_vertex, path)
                    if len(cycle) > 0:
                        return cycle
                elif to_vertex in path:
                    return path[path.index(to_vertex):] + [to_vertex]

            path.remove(vertex)
            return set()

        for from_vertex in self._edges:
            if from_vertex not in visited:
                cycle = _find_cycle(from_vertex, [])
                if len(cycle) > 0:
                    cycles.append(cycle)

        return cycles
