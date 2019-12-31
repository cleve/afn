from utils.stream import Reader

reader = Reader('app/samples/dj38.tsp')
distance_matrix = reader.read_tsp()
print (distance_matrix)