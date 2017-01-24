import numpy
import sys
from top_n_error_rate import top_n_error_rate


out = numpy.load(sys.argv[1])
print(top_n_error_rate(5, out, "../../ILSVRC2012.yaml", range(len(out))))

