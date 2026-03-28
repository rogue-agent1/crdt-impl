#!/usr/bin/env python3
"""crdt_impl - CRDTs: G-Counter, PN-Counter, G-Set, OR-Set, LWW-Register."""
import sys, time
class GCounter:
    def __init__(self, node_id, n_nodes):
        self.id=node_id; self.counts=[0]*n_nodes
    def increment(self, n=1): self.counts[self.id]+=n
    def value(self): return sum(self.counts)
    def merge(self, other):
        for i in range(len(self.counts)): self.counts[i]=max(self.counts[i],other.counts[i])
    def __repr__(self): return f"GCounter({self.value()}, {self.counts})"
class PNCounter:
    def __init__(self, node_id, n_nodes):
        self.p=GCounter(node_id,n_nodes); self.n=GCounter(node_id,n_nodes)
    def increment(self, n=1): self.p.increment(n)
    def decrement(self, n=1): self.n.increment(n)
    def value(self): return self.p.value()-self.n.value()
    def merge(self, other): self.p.merge(other.p); self.n.merge(other.n)
    def __repr__(self): return f"PNCounter({self.value()})"
class GSet:
    def __init__(self): self.elements=set()
    def add(self, elem): self.elements.add(elem)
    def lookup(self, elem): return elem in self.elements
    def merge(self, other): self.elements|=other.elements
    def __repr__(self): return f"GSet({self.elements})"
class LWWRegister:
    def __init__(self): self.value=None; self.timestamp=0
    def set(self, val, ts=None):
        ts=ts or time.time()
        if ts>self.timestamp: self.value=val; self.timestamp=ts
    def get(self): return self.value
    def merge(self, other):
        if other.timestamp>self.timestamp: self.value=other.value; self.timestamp=other.timestamp
    def __repr__(self): return f"LWW({self.value})"
if __name__=="__main__":
    a=GCounter(0,3); b=GCounter(1,3)
    a.increment(3); b.increment(5); a.merge(b)
    print(f"G-Counter: A={a}, B={b}")
    pa=PNCounter(0,2); pb=PNCounter(1,2)
    pa.increment(10); pb.increment(3); pa.decrement(2); pa.merge(pb)
    print(f"PN-Counter: {pa}")
    sa=GSet(); sb=GSet()
    sa.add("x"); sb.add("y"); sa.merge(sb)
    print(f"G-Set: {sa}")
    ra=LWWRegister(); rb=LWWRegister()
    ra.set("hello",1); rb.set("world",2); ra.merge(rb)
    print(f"LWW-Register: {ra}")
