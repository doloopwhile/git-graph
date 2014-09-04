#!/usr/bin/python3.4
import argparse
from subprocess import check_output
import itertools


class Node:
    def __init__(self, hash):
        self.hash = hash
        self.children = []
        self.width = 1
        self.parent = None
        self.rank = 0


class GraphBuilder:
    def __init__(self):
        self.nodes = []

    def root_nodes(self):
        return [n for n in self.nodes if n.parent is None]

    def get(self, hash):
        for node in self.nodes:
            if hash == node.hash:
                break
        else:
            node = Node(hash)
            self.nodes.append(node)
        return node

    def add(self, parentHash, childHash):
        parent = self.get(parentHash)
        child = self.get(childHash)

        child.parent = parent
        child.rank = parent.rank + 1

        parent.children.append(child)
        parent.width += child.width


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("branch", nargs='+')

    args = parser.parse_args()

    builder = GraphBuilder()
    for b in args.branch:
        output = check_output(['git', 'log', '--reverse', '--pretty=%H', b])
        hashes = output.decode('ascii').split()
        for curr, next in itertools.zip_longest(hashes, hashes[1:]):
            builder.add(curr, next)

    ranks = []
    max_rank = max(n.rank for n in builder.nodes)
    for r in range(max_rank + 1):
        ranks.append([node for node in builder.nodes if node.rank == r])

    print("""
    <html>
    <body>
    <style>
    table {
        border-collapse: collapse;
    }
    td {
        border: solid 1 #AAA;
    }
    </style>
    """)
    print("<table>")
    for nodes in ranks:
        print("<tr>")
        for node in nodes:
            print("<td>" + node.hash + "</td>")
            print("<td></td>" * (node.width - 1))
        print("</tr>")
    print("</table>")


if __name__ == '__main__':
    main()
