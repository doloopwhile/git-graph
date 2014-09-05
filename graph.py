#!/usr/bin/python3.4
import argparse
from subprocess import check_output


class Node:
    def __init__(self, hash):
        self.hash = hash
        self.children = []
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

    branches = list(args.branch)
    # def compare_branch(b1, b2):
    #     last_common_node = None
    #     for

    def branch_key(b):
        hashes = []
        for nodes in heights:
            for n in nodes:
                if b in n.branches:
                    hashes.append(b)
                    break
        return tuple(hashes)

    branches.sort(key=branch_key)

    for nodes in heights:
        print("<tr>")

        cells = []
        for b in branches:
            for node in nodes:
                if b in node.branches:
                    if cells[-1:] != [node]:
                        cells.append(node)
                    break
            else:
                cells.append(None)

        for c in cells:
            if c is None:
                print("<td>&nbsp;</td>")
            else:
                print("<td colspan={0}>{1}</td>".format(len(c.branches), c.hash[:8]))

        print("</tr>")
        print("<tr>")
        for _ in branches:
            print("<td>&nbsp;</td>")
        print("</tr>")

    print("<tr>")
    for b in branches:
        print("<td>" + b + "</td>")
    print("</tr>")

    print("</table>")


if __name__ == '__main__':
    main()
