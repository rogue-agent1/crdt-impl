#!/usr/bin/env python3
"""crdt_impl - Conflict-free Replicated Data Types."""
import argparse, time, sys

class GCounter:
    """Grow-only counter."""
    def __init__(self, node_id, n_nodes):
        self.id = node_id; self.counts = [0] * n_nodes
    def increment(self, n=1): self.counts[self.id] += n
    def value(self): return sum(self.counts)
    def merge(self, other):
        for i in range(len(self.counts)):
            self.counts[i] = max(self.counts[i], other.counts[i])

class PNCounter:
    """Positive-Negative counter."""
    def __init__(self, node_id, n_nodes):
        self.p = GCounter(node_id, n_nodes)
        self.n = GCounter(node_id, n_nodes)
    def increment(self, n=1): self.p.increment(n)
    def decrement(self, n=1): self.n.increment(n)
    def value(self): return self.p.value() - self.n.value()
    def merge(self, other): self.p.merge(other.p); self.n.merge(other.n)

class LWWRegister:
    """Last-Writer-Wins Register."""
    def __init__(self): self.value_ = None; self.timestamp = 0
    def set(self, value): self.value_ = value; self.timestamp = time.time()
    def get(self): return self.value_
    def merge(self, other):
        if other.timestamp > self.timestamp:
            self.value_ = other.value_; self.timestamp = other.timestamp

class ORSet:
    """Observed-Remove Set."""
    def __init__(self): self.elements = {}; self.tombstones = set(); self._tag = 0
    def add(self, elem):
        self._tag += 1; tag = f"{id(self)}:{self._tag}"
        self.elements[tag] = elem
    def remove(self, elem):
        for tag, val in list(self.elements.items()):
            if val == elem: self.tombstones.add(tag)
    def value(self):
        return set(v for t, v in self.elements.items() if t not in self.tombstones)
    def merge(self, other):
        self.elements.update(other.elements)
        self.tombstones |= other.tombstones

def main():
    p = argparse.ArgumentParser(description="CRDTs")
    p.add_argument("--demo", action="store_true", default=True)
    a = p.parse_args()
    print("=== G-Counter ===")
    c1 = GCounter(0, 3); c2 = GCounter(1, 3)
    c1.increment(5); c2.increment(3)
    c1.merge(c2)
    print(f"Node 0: +5, Node 1: +3 -> {c1.value()}")
    print("\n=== PN-Counter ===")
    pn1 = PNCounter(0, 2); pn2 = PNCounter(1, 2)
    pn1.increment(10); pn2.decrement(3)
    pn1.merge(pn2)
    print(f"+10, -3 -> {pn1.value()}")
    print("\n=== LWW-Register ===")
    r1 = LWWRegister(); r2 = LWWRegister()
    r1.set("hello"); time.sleep(0.01); r2.set("world")
    r1.merge(r2)
    print(f"r1='hello', r2='world' (later) -> {r1.get()}")
    print("\n=== OR-Set ===")
    s1 = ORSet(); s2 = ORSet()
    s1.add("a"); s1.add("b"); s2.add("b"); s2.add("c")
    s1.remove("b")
    s1.merge(s2)
    print(f"s1={{a,b}}-b, s2={{b,c}} merged -> {s1.value()}")

if __name__ == "__main__": main()
