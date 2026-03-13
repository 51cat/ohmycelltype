import inspect

class Tool():
    def __init__(self, funcs) -> None:
        self.funcs = funcs
        self.get_all_func_doc()
    
    def get_all_func_doc(self):
        self.all_doc = []
        for f in self.funcs:
            
            doc = self._get_function_readme(f)
            
            if doc is not None:
                self.all_doc.append(doc)
            else:
                continue
    
    def _get_function_readme(self,func):
        if not callable(func):
            return None
        doc = func.__doc__

        if doc:
            return inspect.cleandoc(doc)
        else:
            return None
    
    @property
    def desc(self):
        return "\n\n".join(self.all_doc)