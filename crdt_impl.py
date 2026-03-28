#!/usr/bin/env python3
"""CRDTs (Conflict-free Replicated Data Types) — zero-dep."""

class GCounter:
    def __init__(self, node_id, n_nodes=3):
        self.id=node_id; self.counts={i:0 for i in range(n_nodes)}
    def increment(self, amount=1): self.counts[self.id]+=amount
    def value(self): return sum(self.counts.values())
    def merge(self, other):
        for k in self.counts: self.counts[k]=max(self.counts[k],other.counts.get(k,0))

class PNCounter:
    def __init__(self, node_id, n=3):
        self.p=GCounter(node_id,n); self.n=GCounter(node_id,n)
    def increment(self, amount=1): self.p.increment(amount)
    def decrement(self, amount=1): self.n.increment(amount)
    def value(self): return self.p.value()-self.n.value()
    def merge(self, other): self.p.merge(other.p); self.n.merge(other.n)

class LWWRegister:
    def __init__(self): self.value=None; self.ts=0
    def set(self, value, ts):
        if ts>self.ts: self.value=value; self.ts=ts
    def merge(self, other):
        if other.ts>self.ts: self.value=other.value; self.ts=other.ts

class GSet:
    def __init__(self): self.elements=set()
    def add(self, elem): self.elements.add(elem)
    def contains(self, elem): return elem in self.elements
    def merge(self, other): self.elements|=other.elements

class ORSet:
    def __init__(self): self.adds={}; self.removes=set(); self._tag=0
    def add(self, elem):
        self._tag+=1; tag=f"{id(self)}_{self._tag}"
        self.adds[tag]=elem
    def remove(self, elem):
        for tag,val in list(self.adds.items()):
            if val==elem: self.removes.add(tag)
    def elements(self): return {v for t,v in self.adds.items() if t not in self.removes}
    def merge(self, other):
        self.adds.update(other.adds); self.removes|=other.removes

if __name__=="__main__":
    # G-Counter
    a,b=GCounter(0),GCounter(1); a.increment(3); b.increment(5)
    a.merge(b); print(f"GCounter: {a.value()} (3+5=8)")
    # PN-Counter
    pn1,pn2=PNCounter(0),PNCounter(1); pn1.increment(10); pn2.decrement(3)
    pn1.merge(pn2); print(f"PNCounter: {pn1.value()} (10-3=7)")
    # LWW-Register
    r1,r2=LWWRegister(),LWWRegister(); r1.set("hello",1); r2.set("world",2)
    r1.merge(r2); print(f"LWWRegister: {r1.value} (latest wins)")
    # OR-Set
    s1,s2=ORSet(),ORSet(); s1.add("a"); s1.add("b"); s2.add("b"); s2.add("c")
    s1.remove("b"); s1.merge(s2)
    print(f"ORSet: {s1.elements()} (remove before merge, add-wins)")
