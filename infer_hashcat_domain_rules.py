#!/usr/bin/env python3
"""
Infer domain-squatting transformations and express them as Hashcat-style rules.

Input JSON format:
{
  "original.com": {
     "transformed1.com": <int>,
     "transformed2.com": <int>,
     ...
  },
  ...
}

We compare SLDs (second-level domains, excluding .com), infer a minimal
Damerau-Levenshtein edit script, then map edits to hashcat rules:

Mapping:
- delete first char            ->  [
- delete last char             ->  ]
- delete at position N         ->  D N
- prepend char X               ->  ^ X   (multi-char prefix becomes multiple ^ rules,
                                         applied in reverse order to preserve prefix)
- append char X                ->  $ X   (multi-char suffix becomes multiple $ rules)
- insert char X at position N  ->  i N X
- overwrite position N with X  ->  o N X
- swap positions i and i+1     ->  * i (i+1)      (for adjacent transposition)

Rules are emitted as space-separated tokens like best64.rule.
Multiple ops are combined in order into ONE composite rule string.

Outputs:
- Prints top N rules with counts
- Optionally writes a .rule file with rules sorted by freq
- Optionally writes counts as JSON

NOTE: Domain names are lowercased; case rules are not generated.
"""

from __future__ import annotations
import json
import argparse
from dataclasses import dataclass
from collections import Counter
from typing import List, Tuple

# base36 encoding for positions in hashcat rules
_BASE36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def enc_pos(n: int) -> str:
    if n < 0 or n >= len(_BASE36):
        raise ValueError(f"Position {n} out of encodable range 0-35")
    return _BASE36[n]

@dataclass
class Op:
    kind: str   # 'ins', 'del', 'sub', 'trans', 'keep'
    i: int      # index in original (for ins, position before which inserted)
    j: int      # index in transformed
    a: str = '' # original char(s)
    b: str = '' # transformed char(s)

def sld(domain: str) -> str:
    return domain.split('.', 1)[0].lower()

def damerau_levenshtein_ops(a: str, b: str) -> List[Op]:
    """Minimal edit script with adjacent transpositions."""
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    back = [[None]*(m+1) for _ in range(n+1)]

    for i in range(1, n+1):
        dp[i][0] = i
        back[i][0] = Op('del', i-1, 0, a[i-1], '')
    for j in range(1, m+1):
        dp[0][j] = j
        back[0][j] = Op('ins', 0, j-1, '', b[j-1])

    for i in range(1, n+1):
        for j in range(1, m+1):
            cost_sub = 0 if a[i-1] == b[j-1] else 1

            best_cost = dp[i-1][j] + 1
            best_op = Op('del', i-1, j, a[i-1], '')

            c_ins = dp[i][j-1] + 1
            if c_ins < best_cost:
                best_cost = c_ins
                best_op = Op('ins', i, j-1, '', b[j-1])

            c_sub = dp[i-1][j-1] + cost_sub
            if c_sub < best_cost:
                best_cost = c_sub
                best_op = Op('keep' if cost_sub==0 else 'sub', i-1, j-1, a[i-1], b[j-1])

            if i >= 2 and j >= 2 and a[i-2] == b[j-1] and a[i-1] == b[j-2]:
                c_trans = dp[i-2][j-2] + 1
                if c_trans < best_cost:
                    best_cost = c_trans
                    best_op = Op('trans', i-2, j-2, a[i-2:i], b[j-2:j])

            dp[i][j] = best_cost
            back[i][j] = best_op

    # backtrace
    ops: List[Op] = []
    i, j = n, m
    while i > 0 or j > 0:
        op = back[i][j]
        if op is None:
            break
        ops.append(op)
        if op.kind == 'del':
            i -= 1
        elif op.kind == 'ins':
            j -= 1
        elif op.kind in ('sub','keep'):
            i -= 1
            j -= 1
        elif op.kind == 'trans':
            i -= 2
            j -= 2
    ops.reverse()
    return [o for o in ops if o.kind != 'keep']

def ops_to_hashcat_tokens(orig: str, trans: str, ops: List[Op]) -> List[str]:
    """Convert edit ops to hashcat rule tokens."""
    n = len(orig)
    tokens: List[str] = []

    # collect prefix/suffix insertions to coalesce into multiple ^/$ tokens
    prefix_chars: List[str] = []
    suffix_chars: List[str] = []
    mid_inserts: List[Op] = []

    for op in ops:
        if op.kind == 'ins':
            if op.i == 0:
                prefix_chars.append(op.b)
            elif op.i == n:
                suffix_chars.append(op.b)
            else:
                mid_inserts.append(op)
        elif op.kind == 'del':
            if op.i == 0:
                tokens.append('[')
            elif op.i == n-1:
                tokens.append(']')
            else:
                tokens.append(f"D{enc_pos(op.i)}")
        elif op.kind == 'sub':
            tokens.append(f"o{enc_pos(op.i)}{op.b}")
        elif op.kind == 'trans':
            i0 = op.i
            # adjacent swap in DL always length 2
            tokens.append(f"*{enc_pos(i0)}{enc_pos(i0+1)}")

    # apply prefix inserts: for prefix "ab", do ^b ^a (reverse) to get "ab"+word
    for ch in reversed(prefix_chars):
        tokens.insert(0, f"^{ch}")

    # apply suffix inserts in order
    for ch in suffix_chars:
        tokens.append(f"${ch}")

    # middle inserts by increasing position
    for op in sorted(mid_inserts, key=lambda x: x.i):
        tokens.append(f"i{enc_pos(op.i)}{op.b}")

    return tokens

def infer_rule(orig_domain: str, trans_domain: str) -> str:
    o = sld(orig_domain)
    t = sld(trans_domain)
    ops = damerau_levenshtein_ops(o, t)
    tokens = ops_to_hashcat_tokens(o, t, ops)
    return " ".join(tokens) if tokens else ":"

def main():
    ap = argparse.ArgumentParser(description="Infer hashcat-style rules for squatted domains.")
    ap.add_argument("input_json", help="Path to disputes-training.json")
    ap.add_argument("--out-rule", help="Write sorted rules to this .rule file")
    ap.add_argument("--out-counts", help="Write rule counts JSON here")
    ap.add_argument("--show", type=int, default=30, help="Show top N rules")
    args = ap.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    counts = Counter()
    for orig, trans_map in data.items():
        for trans in trans_map.keys():
            rule = infer_rule(orig, trans)
            counts[rule] += 1

    total = sum(counts.values())
    print(f"Total pairs processed: {total}")
    print(f"Unique rules: {len(counts)}")
    print(f"Top {args.show} rules:")
    for r, c in counts.most_common(args.show):
        print(f"{c:4d}  {r}")

    if args.out_counts:
        with open(args.out_counts, "w", encoding="utf-8") as f:
            json.dump(counts, f, indent=2, sort_keys=True)

    if args.out_rule:
        with open(args.out_rule, "w", encoding="utf-8") as f:
            for r, c in counts.most_common():
                f.write(r + "\n")

if __name__ == "__main__":
    main()
