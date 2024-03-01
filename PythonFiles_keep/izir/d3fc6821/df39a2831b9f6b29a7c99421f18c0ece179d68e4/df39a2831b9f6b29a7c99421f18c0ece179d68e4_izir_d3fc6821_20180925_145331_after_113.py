"""A simple example that illustrates returning UTF-8 encoded data within a JSON outputting izi endpoint"""
import izi


@izi.get()
def unicode_response():
    """An example endpoint that returns unicode data nested within the result object"""
    return {'data': ['Τη γλώσσα μου έδωσαν ελληνική']}
