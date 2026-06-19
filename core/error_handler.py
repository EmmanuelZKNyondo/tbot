# core/error_handler.py
import traceback

class ErrorHandler:
  
  def __init__(self, show_traceback=True):
    self.show_traceback = show_traceback
    
  
  def handle(self, exception: Exception, context: str, file: str = None, function: str = None):
    print("\n============================================== TBot ERROR ==============================================")
    
    if context:
      print(f"Context   : {context}")
      
    print(f"Error    : {type(exception).__name__}")
    print(f"Message   : {exception}")
    
    if file:
      print(f"File   : {file}")
    
    if function:
      print(f"Function   : {function}")
    
    if self.show_traceback:
      print("\n------------------------------------------- Stack Trace ----------------------------------------------")
      traceback.print_exc()
      
    print("\n============================================= END OF ERROR =============================================")