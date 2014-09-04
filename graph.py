#!/usr/bin/python3.4
import argparse
from subprocess import check_output


class Node:
    def __init__(self, hash):
        self.hash = hash
        self.children = []
        self.width = 1
        self.parent = None
        self.height = 0
        self.branches = []


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
        child.height = parent.height + 1

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
        for curr, next in zip(hashes, hashes[1:]):
            builder.add(curr, next)

        for h in hashes:
            builder.get(h).branches.append(b)

    heights = []
    max_height = max(n.height for n in builder.nodes)
    for r in range(max_height + 1):
        heights.append([node for node in builder.nodes if node.height == r])

    print("""
    <html>
    <body>
    <style>
    td {
        border: solid 1px #AAA;
    }
    </style>
    """)
    print("<table>")
    for nodes in heights:
        print("<tr>")
        for node in sorted(nodes, key=lambda n: tuple(sorted(n.branches))):
            print("<td>" + node.hash[:8] + "</td>")
            print("<td></td>" * (node.width - 1))
        print("</tr>")

    print("<tr>")
    for b in args.branch:
        print("<td>" + b + "</td>")
    print("</tr>")

    print("</table>")


if __name__ == '__main__':
    main()
