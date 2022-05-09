from pyrstar import rectangle as rct


# maximum number of children
M = 32

# minimum number of children. try m = floor(0.4*M)
m = 12

# Dimension of data
# d = 2

# Parameter controlling how overflow is treated. try p = floor(0.3*M)
p = 9


class RStarTree:
    def __init__(self, children, point_data={}):
        """
        Spatially index point data
        ---------------------------------
        Parameters:
        -----------
        children: The subtrees which determine the key rectangle

        point_data: a dictionary where keys are point ids, values are lists of
        point coordinates.
        """

        if point_data:
            if children:
                raise ValueError
            else:
                self.is_leaf = True
        else:
            if not children:
                raise ValueError
            else:
                self.is_leaf = False

        self.children = children
        self.points = point_data

        self.update_bounding_rectangle()


    def __eq__(self, other):
        return self.key == other.key and self.is_leaf == other.is_leaf


    def __str__(self):
        return str(self.key)


    def get_child_count(self):
        return len(self.children)


    def get_child_rectangles(self):
        return [child.key for child in self.children]


    def get_point_count(self):
        return len(self.points)


    def get_points(self):
        return list(self.points.values())


    def does_point_to_leaves(self):
        blist = [child.is_leaf for child in self.children]
        return all(blist)


    def update_bounding_rectangle(self):
        if self.is_leaf:
            P = self.get_points()
            new_key = rct.bounding_box_points(P)
        else:
            R = self.get_child_rectangles()
            if R:
                new_key = rct.bounding_box(R)
            else:
                new_key = rct.EmptyRectangle(1)
        self.key = new_key


    def add_point_data(self,point_key,point_value):
        if self.is_leaf:
            self.points[point_key]=point_value
            self.update_bounding_rectangle()
        else:
            pass

    def delete_point_data(self,point_key):
        if self.is_leaf:
            del self.points[point_key]
            self.update_bounding_rectangle()
        else:
            pass


    def add_child(self,rt):
        self.children.append(rt)
        self.update_bounding_rectangle()


    def delete_child(self,rt):
        self.children.remove(rt)
        self.update_bounding_rectangle()


NullRT = RStarTree(children=[],is_leaf=False)



def overlap_enlargement_required(rt, candidate, entry):
    """

    """
    rects = rt.get_child_rectangles()
    rects.remove(candidate.key)
    enlarged_rect = candidate.key.union(entry)

    result = 0.0
    for r in rects:
        result += enlarged_rect.intersection_volume(r)
    return result


def volume_enlargement_required(candidate, entry):
    """
    """
    rect = candidate.key
    vol0 = rect.volume()
    rect = rect.union(entry)
    vol1 = rect.volume()
    return vol1 - vol0


def path_to_subtree(rt, t, path=[]):
    """
    Get path from root rt to subtree t:
    -----------------------------------
    Parameters:
    -----------
    rt: the root of the R*-tree
    t: the subtree of interest
    path: the path traversed thus far

    Returns:
    --------
    path: [rt, ..., t]. If rt is t, then path is [t]
    """
    updated_path = path + [rt]

    t_rectangle = t.key
    rt_rectangle = rt.key

    if t_rectangle == rt_rectangle:
        return [t]

    N = NullRT

    for ch in rt.children:
        if ch.key.is_proper_superset(t_rectangle):
            # What do we do if t is in the overlap of two nodes, one of which
            # has t as a descendant, the other of which does not have t as a
            # descendant?
            N = ch
            break

    if N == NullRT:
        return []

    if N == t:
        return updated_path + [N]

    return path_to_subtree(N, t, updated_path)



def choose_subtree(rt, lvl, entry, path=[]):
    """
    Chooses subtree in rt for inserting entry
    -----------------------------------------
    Parameters:
    -----------
    rt: R*-tree in which entry will be inserted
    lvl: level of node rt. 0 means root level.
    entry: rectangle to be inserted. may be a point rectangle.
    path: the path traverse thus far in the call

    Returns:
    --------
    rt: the chosen subtree
    lvl: the level of the chosen subtree
    path: the path traversed to the subtree
    """
    updated_path = path + [rt]
    if rt.is_leaf:
        return rt, lvl, updated_path
    if rt.does_point_to_leaves():
        keyfunc = lambda child: (overlap_enlargement_required(rt, child, entry),
        volume_enlargement_required(child,entry), child.key.volume())

        t = min(rt.children, key = keyfunc)
        # should resolve ties by choosing candidate whose volume needs to be
        # enlarged the least. resolve those ties by choosing the rectangle of
        # smallest volume.
        # there may be multiple candidates whose accomodating the entry would
        # not cause any overlap enlargement
    else:
        keyfunc = lambda child: (volume_enlargement_required(child,entry),
        child.key.volume())

        t = min(rt.children, key = keyfunc)
    return choose_subtree(t, lvl + 1, entry, updated_path)


class RTCursor:
    def __init__(self,rt):
        # level: overflow_was_treated
        self.level_actions = {0:False}
        self.root = rt


    def insert(self, point_data):
        """
        We will only be indexing points.
        """
        self._insert_point(self.root, 0, point_data)
        self.level_actions = {0:False}


    def _insert_point(self, rt, rt_lvl, point_data):
        P_id, P = point_data
        E = rct.Rectangle(P,P)

        st, lvl, path = choose_subtree(rt, rt_lvl, E)

        complete_path=[]
        point_count = st.get_point_count()
        if point_count < M:
            st.add_point_data(P_id, P)
        elif lvl != 0 and len(path) >= 2:
            # overflow not at root

            # set predecessor to next to last element of path
            st_pred = path[-2]

            # add the point and then treat the overflow
            st.add_point_data(P_id, P)
            caused_split = self.overflow_treatment(st,lvl,st_pred)
            if caused_split and st_pred.get_child_count() > M:
                # Propagate overflow treatment up the insertion path
                complete_path = path_to_subtree(self.root, path[0])[0:-1] + path[0:-1]
                _ = self.propagate_overflow_treatment(lvl - 1, complete_path)
        elif lvl != 0 and len(path) == 1:
            # overflow not at root

            if lvl == 1:
                assert path[0] in self.root.children
                complete_path = [self.root, path[0]]
            else:
                complete_path = path_to_subtree(self.root, path[0])

            # set predecessor to next to last element of complete path
            st_pred = complete_path[-2]

            # add point and treat overflow
            st.add_point_data(P_id, P)
            caused_split = self.overflow_treatment(st, lvl, st_pred)
            if caused_split and st_pred.get_child_count() > M:
                _ = self.propagate_overflow_treatment(lvl - 1, complete_path[0:-1])
        else:
            # overflow at root
            st.add_point_data(P_id, P)
            _ = self.overflow_treatment(st, lvl, NullRT)


        # Make sure all covering rectangles in insertion path are adjusted
        # to be minimum bounding rectangles


    def _insert_node(self, rt, rt_lvl, t):
        E = t.key
        st, lvl, path = choose_subtree(rt, rt_lvl, E)

        complete_path = []
        child_count = st.get_child_count()
        if child_count < M:
            st.add_child(t)
        elif lvl != 0 and len(path) >= 2:
            # overflow not at root

            # set predecessor to next to last element of path
            st_pred = path[-2]

            # add node and then treat overflow
            st.add_child(t)
            caused_split = self.overflow_treatment(st, lvl, st_pred)
            if caused_split and st_pred.get_child_count() > M:
                # Propagate overflow_treatment up the insertion path
                complete_path = path_to_subtree(self.root, path[0])[0:-1] + path[0:-1]
                # output would indicate whether a root split was performed
                _ = self.propagate_overflow_treatment(lvl - 1, complete_path)
        elif lvl != 0 and len(path) == 1:
            # overflow not at root

            if lvl == 1:
                assert path[0] in self.root.children
                complete_path = [self.root, path[0]]
            else:
                complete_path = path_to_subtree(self.root, path[0])

            # set predecessor to next to last element of complete path
            st_pred = complete_path[-2]

            # add node and then treat overflow
            st.add_child(t)
            caused_split = self.overflow_treatment(st, lvl, st_pred)
            if caused_split and st_pred.get_child_count() > M:
                # Propagate overflow treatment upward
                _ = self.propagate_overflow_treatment(lvl - 1, complete_path[0:-1])
        else:
            # overflow at root
            # add node to root and treat overflow
            st.add_child(t)
            _ = self.overflow_treatment(st, lvl, NullRT)

        # Adjust all covering rectangles in the insertion path


    def split_leaf(self, t, pred):
        count = t.get_point_count()
        assert count == M + 1
        ax = choose_split_axis_leaf(t)
        idx = choose_split_index_leaf(t, ax)

        kf = lambda k: (t.points[k])[ax]
        sorted_along_axis = sorted(list(t.points), key = kf)

        # point data for the two new leaves
        group_1 = {x: t.points[x] for x in sorted_along_axis[0:idx]}
        group_2 = {x: t.points[x] for x in sorted_along_axis[idx:]}

        # instantiate the new leaves
        new_leaf_1 = RStarTree(children=[],is_leaf=True,point_data=group_1)
        new_leaf_2 = RStarTree(children=[],is_leaf=True,point_data=group_2)

        if pred == NullRT:
            new_root = RStarTree(children = [new_leaf_1, new_leaf_2], is_leaf=False)
            self.root = new_root
        else:
            # delete original leaf
            pred.delete_child(t)

            # add the new leaves to the predecessor
            pred.add_child(new_leaf_1)
            pred.add_child(new_leaf_2)



    def split_node(self, t, pred):
        count = t.get_child_count()
        assert count == M + 1
        ax = choose_split_axis(t)
        idx, islower = choose_split_index(t, ax)

        kf = lambda ch: ch.key.minima[ax]
        sorted_along_axis = sorted(t.children, key = kf)

        # children for two new nodes
        group_1 = sorted_along_axis[0:idx]
        group_2 = sorted_along_axis[idx:]

        # instantiate new nodes
        node_1 = RStarTree(children=group_1, is_leaf=False)
        node_2 = RStarTree(children=group_2, is_leaf=False)

        if pred == NullRT:
            # make new root?
            new_root = RStarTree(children = [node_1, node_2], is_leaf=False)
            self.root = new_root
        else:
            # delete original node
            pred.delete_child(t)

            # add back nodes
            pred.add_child(node_1)
            pred.add_child(node_2)


    def overflow_treatment(self, rt, lvl, pred):
        split_performed = False

        if lvl not in self.level_actions:
            self.level_actions[lvl] = False

        # if not the root and not already called at this level
        if (lvl != 0) and (not self.level_actions[lvl]):
            self.level_actions[lvl] = True
            split_performed = False
            if rt.is_leaf:
                self.leaf_re_insert(rt, lvl)
            else:
                self.node_re_insert(rt, lvl)
        else:
            split_performed = True
            if rt.is_leaf:
                self.split_leaf(rt, pred)
            else:
                self.split_node(rt, pred)
        return split_performed



    def leaf_re_insert(self, rt, lvl):
        """
        Called on overflowing (M+1 entries) leaf
        """
        # Get a list of points' keys ordered by points' distances from the center
        # of leaf's rectangle, descending
        keyfunc = lambda k: rct.point_to_center_distance_squared(rt.points[k], rt.key)
        pts_by_dist = sorted(list(rt.points), key=keyfunc, reverse=True)

        # Slate the p points most distant from the center to be removed from rt
        to_remove = pts_by_dist[0:p]

        # Prepare (key, value) pairs to be reinserted
        to_re_insert = [(k, rt.points[k]) for k in to_remove]

        # Remove the chosen points, updating leaf's bounding rectangle
        for pk in to_remove:
            rt.delete_point_data(pk)

        # close reinsert: because the tree depends on the order of insert
        # inserting pts closer to the center first performs differently
        to_re_insert.reverse()

        # Iteratively reinsert entries
        for pt in to_re_insert:
            self._insert_point(rt, lvl, pt)


    def node_re_insert(self, rt, lvl):
        """
        Called on overflowing (M+1 entries) non-leaf node
        """
        # Get a list of children sorted by their centers' distances from the
        # center of the node's rectangle, descending.
        node_rect = rt.key
        keyfunc = lambda cr: node_rect.center_distance_squared(cr)
        children_by_dist = sorted(children, key=keyfunc, reverse=True)

        # Slate first p points to be removed and reinserted
        to_remove = children_by_dist[0:p]
        # close reinsert
        to_re_insert = to_remove.reverse()

        # Remove them, updating node's bounding rectangle
        for c in to_remove:
            rt.delete_child(c)

        # Iteratively reinsert, passing level of rt as a parameter
        for c in to_re_insert:
            self._insert_node(rt,lvl,c)


    def propagate_overflow_treatment(self, lvl, node_list):
        was_root_split = False
        for i,t in reversed(list(enumerate(node_list))):
            count = t.get_child_count()
            if count > M:
                if i >= 1:
                    pred = node_list[i-1]
                    _ = self.overflow_treatment(t, lvl, pred)
                else:
                    pred = NullRT
                    was_root_split = self.overflow_treatment(t, lvl, pred)
            lvl -= 1
        return was_root_split


def choose_split_axis_leaf(t):
    d = t.key.dimension
    margins = []
    for i in range(0,d):
        kf = lambda k: (t.points[k])[i]
        sorted_by_i = sorted(list(t.points), key = kf)

        S_i = 0.0
        for j in range(1, M - 2*m + 2):
            # does this range capture all possible distributions into two groups?
            first_split_group = sorted_by_i[0:(m - 1 + j)]
            bb_1 = rct.bounding_box_points([t.points[k] for k in first_split_group])

            second_split_group = sorted_by_i[(m - 1 + j):]
            bb_2 = rct.bounding_box_points([t.points[k] for k in second_split_group])

            S_i += rct.rectangle_perimeter(bb_1) + rct.rectangle_perimeter(bb_2)
        margins.append((S_i,i))

    return (min(margins))[1]


def choose_split_index_leaf(t,axis):
    d = t.key.dimension

    kf = lambda k: (t.points[k])[axis]
    sorted_along_axis = sorted(list(t.points), key = kf)

    scores = []
    for j in range(1, M - 2*m + 2):
        first_split_group = sorted_along_axis[0:(m - 1 + j)]
        bb_1 = rct.bounding_box_points([t.points[k] for k in first_split_group])

        second_split_group = sorted_along_axis[(m - 1 + j):]
        bb_2 = rct.bounding_box_points([t.points[k] for k in second_split_group])

        overlap_j = bb_1.intersection_volume(bb_2)
        vol_score_j = bb_1.volume() + bb_2.volume()

        scores.append((overlap_j,vol_score_j, m - 1 + j))

    return (min(scores))[2]


def choose_split_axis(t):
    d = t.key.dimension
    child_rects = t.get_child_rectangles()

    margins = []
    for i in range(0,d):
        lower_kf = lambda ch: ch.minima[i]
        by_lower_i = sorted(child_rects, key = lower_kf)

        upper_kf = lambda ch: ch.maxima[i]
        by_upper_i = sorted(child_rects, key = upper_kf)

        S_i = 0.0
        for j in range(1, M - 2*m + 2):
            g1 = by_lower_i[0:(m - 1 + j)]
            g2 = by_lower_i[(m - 1 + j):]
            g3 = by_upper_i[0:(m - 1 + j)]
            g4 = by_upper_i[(m - 1 + j):]
            margin_1 = rct.rectangle_perimeter(rct.bounding_box(g1))
            margin_2 = rct.rectangle_perimeter(rct.bounding_box(g2))
            margin_3 = rct.rectangle_perimeter(rct.bounding_box(g3))
            margin_4 = rct.rectangle_perimeter(rct.bounding_box(g4))
            S_i += margin_1 + margin_2 + margin_3 + margin_4

        margins.append((S_i, i))

    return (min(margins))[1]


def choose_split_index(t,axis):
    d = t.key.dimension

    child_rects = t.get_child_rectangles()

    lower_kf = lambda ch: ch.minima[axis]
    by_lower = sorted(child_rects, key = lower_kf)

    upper_kf = lambda ch: ch.maxima[axis]
    by_upper = sorted(child_rects, key = upper_kf)

    scores = [] # will hold tuples (overlap, volume, index, is_lower)
    for j in range(1, M - 2*m + 2):
        bb_1 = rct.bounding_box(by_lower[0:(m - 1 + j)])
        bb_2 = rct.bounding_box(by_lower[(m - 1 + j):])

        overlap_lower = bb_1.intersection_volume(bb_2)
        vol_score_lower = bb_1.volume() + bb_2.volume()

        scores.append((overlap_lower,vol_score_lower, m - 1 + j, True))

        bb_3 = rct.bounding_box(by_upper[0:(m - 1 + j)])
        bb_4 = rct.bounding_box(by_upper[(m - 1 + j):])

        overlap_upper = bb_3.intersection_volume(bb_4)
        vol_score_upper = bb_3.volume() + bb_4.volume()

        scores.append((overlap_upper, vol_score_upper, m - 1 + j, False))

    best = min(scores, key = lambda s: (s[0], s[1]))
    return best[2], best[3]


def create_tree_from_pts(pts_tuples):
    """
    Parameters
    ----------
    pts_tuples: list of pts as (key,value) tuples

    Returns
    -------
    retv: an RTCursor to the instantiated tree
    """
    pt_dict = {k : v for k,v in pts_tuples[0:M-1]}
    starting_node = RStarTree(children = [], is_leaf=True, point_data = pt_dict)

    retv = RTCursor(starting_node)

    for pt in pts_tuples[M-1:]:
        retv.insert(pt)

    return retv
