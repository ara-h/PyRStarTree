


class Rectangle:
    def __init__(self, minarray, maxarray):
        self.dimension = len(minarray)
        self.minima = minarray
        if len(maxarray) != self.dimension:
            raise ValueError
        self.maxima = maxarray
        self._update_pointness()
        if not self.is_point and not are_bounds_rectangular(minarray, maxarray):
            raise ValueError



    def __eq__(self, other):
        return self.minima == other.minima and self.maxima == other.maxima


    def __str__(self):
        L = ' '.join(["%.2f" % x for x in self.minima])
        U = ' '.join(["%.2f" % x for x in self.maxima])
        return f"Rectangle \n|minima: {L} \n|maxima: {U}"


    def _update_pointness(self):
        if self.minima == self.maxima:
            self.is_point = True
        else:
            self.is_point = False


    def volume(self):
        if self.is_point:
            return 0.0

        vol = self.maxima[0] - self.minima[0]
        for i in range(1,self.dimension):
            vol *= self.maxima[i] - self.minima[i]

        return vol


    def intersect(self, other):
        intersection_minima = []
        intersection_maxima = []
        for i in range(0,self.dimension):
            intersection_minima.append(max(self.minima[i],other.minima[i]))
            intersection_maxima.append(min(self.maxima[i],other.maxima[i]))

        if not are_bounds_rectangular(intersection_minima, intersection_maxima):
            return EmptyRectangle(1)

        return Rectangle(intersection_minima,intersection_maxima)


    def intersection_volume(self, other):
        return (self.intersect(other)).volume()


    def is_element(self, point):
        blist = [(self.minima[i] <= point[i] and point[i] <= self.maxima[i])
        for i in range(0,self.dimension)]
        return all(blist)


    def is_proper_superset(self, other):
        # returns truth value of (self \subset other)
        return self.is_element(other.minima) and self.is_element(other.maxima)


    def union(self, other):
        lower = []
        upper = []
        for i in range(0, self.dimension):
            li = min(self.minima[i],other.minima[i])
            ui = max(self.maxima[i],other.maxima[i])
            lower.append(li)
            upper.append(ui)

        return Rectangle(lower,upper)


    def union_with_point(self, point):
        lower = []
        upper = []
        for i in range(0, self.dimension):
            li = min(self.minima[i], point[i])
            ui = max(self.maxima[i], point[i])
            lower.append(li)
            upper.append(ui)

        return Rectangle(lower,upper)


    def center(self):
        if self.is_point:
            return self.minima

        result = []
        for i in range(0, self.dimension):
            mi = (self.maxima[i] + self.minima[i])/2
            result.append(mi)
        return result


    def center_distance_squared(self,other):
        c1 = self.center()
        c2 = other.center()

        s = 0.0
        for i in range(0, self.dimension):
            s += (c1[i]-c2[i])**2
        return s


def point_to_center_distance_squared(p, rect):
    c = rect.center()
    s = 0.0
    for i in range(0,len(p)):
        s += (c[i]-p[i])**2
    return s


def bounding_box(rects):
    u = rects[0]
    for i in range(1, len(rects)):
        u = u.union(rects[i])
    return u


def bounding_box_points(points):
    r_bound = points[0]
    rect = Rectangle(r_bound, r_bound)
    for i in range(1, len(points)):
        rect = rect.union_with_point(points[i])
    return rect


def are_bounds_rectangular(lowerbounds,upperbounds):
    d = len(lowerbounds)
    if len(upperbounds) != d:
        return False

    blist = [(lowerbounds[i] < upperbounds[i]) for i in range(0,d)]
    return all(blist)


def EmptyRectangle(d):
    bounds = [0] * d
    return Rectangle(bounds,bounds)


def rectangle_perimeter(rect):
    d = rect.dimension
    L = rect.minima
    U = rect.maxima
    ext = [U[i]-L[i] for i in range(0,d)]
    return (2**(d-1))*sum(ext)
