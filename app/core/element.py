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
        if self.x == -1 or self.y == -1:
            raise ('position can not be -1')
        return (self.x, self.y)
