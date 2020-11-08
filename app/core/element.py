class Element:
    '''Element creation

        params:
            - node_id: int
    '''

    def __init__(self, node_id, x, y, element_type=None):
        self.nodes = []
        self.x = x
        self.y = y
        self.node_id = node_id
        self.type = element_type

    def get_coordinates(self):
        '''Get a tuple (x, y)
        '''
        return (self.x, self.y)

    def __repr__(self):
        return self.__class__.__name__ + '-' + str(self.type)
