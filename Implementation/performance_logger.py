import time
import logging
from datetime import datetime
import functools

class PerformanceLogger:
    @staticmethod
    def measure_inference_speed(method):
        """
        Decorator to measure and log inference speed of methods
        
        Args:
            method (callable): Method to be measured
        
        Returns:
            Wrapped method with performance measurement
        """
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = method(*args, **kwargs)
            end_time = time.time()
            
            # Log performance metrics
            inference_time = end_time - start_time
            logging.info(f"""
            Performance Metrics for {method.__name__}:
            - Inference Time: {inference_time:.4f} seconds
            - Result Size: {len(str(result)) if result else 0} characters
            - Timestamp: {datetime.now()}
            """)
            
            return {
                'result': result,
                'inference_time': inference_time
            }
        return wrapper