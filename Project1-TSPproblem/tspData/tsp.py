import numpy as np
import math
import gurobipy as gp
from gurobipy import GRB
from itertools import combinations
from tsp80_0 import points


def distance(city1, city2):
    diff = (points[city1][0] - points[city2][0], points[city1][1] - points[city2][1])
    return math.sqrt(diff[0] * diff[0] + diff[1] * diff[1])


# def mycallback1(model, where):
#     if where == GRB.Callback.MIPSOL:
#         sol = model.cbGetSolution([model._vars[0],
#             model._vars[1]])
#         if sol[0] + sol[1] > 1.1:
#             model.cbLazy(model._vars[0] + model._vars[1] <= 1)
#
#
# def mycallback2(model, where):
#     if where == GRB.Callback.MIPNODE:
#         status = model.cbGet(GRB.Callback.Optimization.MIPNODE_STATUS)
#         if status == GRB.OPTIMAL:
#             rel = model.cbGetNodeRel([model._vars[0],
#                 model._vars[1]])
#             if rel[0] + rel[1] > 1.1:
#                 model.cbCut(model._vars[0] + model._vars[1] <= 1)
# m._vars = m.getVars()
# m.Params.PreCrush = 1
# m.optimize(mycallback2)


def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
                                if vals[i, j] > 0.5)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < len(points):
            # add subtour elimination constr. for every pair of cities in subtour
            model.cbLazy(gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
                         <= len(tour) - 1)


def subtourelim_user(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
                                if vals[i, j] > 0.5)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < len(points):
            # add subtour elimination constr. for every pair of cities in subtour
            model.cbCut(gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
                         <= len(tour) - 1)


# Given a tuplelist of edges, find the shortest subtour

def subtour(edges):
    unvisited = list(range(0, len(points)))
    cycle = list(range(0, len(points)))  # Dummy - guaranteed to be replaced
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(thiscycle) <= len(cycle):
            cycle = thiscycle  # New shortest subtour
    return cycle


dist = {(c1, c2): distance(c1, c2) for c1 in range(len(points)) for c2 in range(len(points)) if c1 < c2}

m = gp.Model()
vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='x')

# Symmetric direction: Copy the object
for i, j in vars.keys():
    vars[j, i] = vars[i, j]  # edge in opposite direction

# Constraints: two edges incident to each city
cons = m.addConstrs(vars.sum(c, '*') == 2 for c in range(len(points)))

# m._vars = vars
# m.Params.lazyConstraints = 1
# m.optimize(subtourelim)

m._vars = vars
m.Params.lazyConstraints = 1
m.update()
# m.Params.PreCrush = 1
m.optimize(subtourelim)

vals = m.getAttr('x', vars)
selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

tour = subtour(selected)
# assert len(tour) == len(points)


print(tour)
print(len(tour))
