# PyRStarTree
A Python implementation of d-dimensional R*-trees for spatially indexing point
data.


## Background

The R-Tree is a data structure used to index spatial information. Objects that
are nearby in space are pointed to by a parent node, whose key holds their
minimum bounding rectangle. In turn, these leaf nodes are siblings of other
nearby leaf nodes and are pointed to by a parent, whose key is their MBR. Such
a structure allows one to skip over branches whose bounding rectangle does not
satisfy the conditions of some query.

The R*-tree was proposed in 1990 as a variant of the R-tree: its insertion
strategy involved re-inserting nodes, possibly reorganizing the entire tree [1].


## References

[1]: Beckmann, Norbert, et al.
["The R*-tree: an efficient and robust access method for points and rectangles."](https://infolab.usc.edu/csci599/Fall2001/paper/rstar-tree.pdf)
*Proceedings of the 1990 ACM SIGMOD international conference on Management of data.* 1990.
