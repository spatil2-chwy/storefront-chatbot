from typing import Generator, Callable, Any, Optional
import time

class StreamingResponseCapture:
    """Captures streaming responses and provides the complete response for evaluation"""
    
    def __init__(self, generator: Generator[str, None, None], 
                 on_complete: Optional[Callable[[str, float], None]] = None):
        self.generator = generator
        self.on_complete = on_complete
        self.complete_response = ""
        self.start_time = time.time()
        self.is_complete = False
    
    def __iter__(self):
        """Iterate through the generator while capturing the complete response"""
        try:
            for chunk in self.generator:
                self.complete_response += chunk
                yield chunk
        except Exception as e:
            # Handle any errors in the generator
            self.complete_response += f"\n[Error: {str(e)}]"
            yield f"\n[Error: {str(e)}]"
        finally:
            # Call the completion callback with the full response
            self.is_complete = True
            response_time = time.time() - self.start_time
            if self.on_complete:
                self.on_complete(self.complete_response, response_time)
    
    def get_complete_response(self) -> str:
        """Get the complete response (only available after iteration is complete)"""
        if not self.is_complete:
            raise RuntimeError("Response capture not complete. Iterate through the generator first.")
        return self.complete_response
    
    def get_response_time(self) -> float:
        """Get the total response time"""
        return time.time() - self.start_time

def capture_streaming_response(generator: Generator[str, None, None], 
                             on_complete: Optional[Callable[[str, float], None]] = None) -> StreamingResponseCapture:
    """Create a streaming response capture wrapper"""
    return StreamingResponseCapture(generator, on_complete) 