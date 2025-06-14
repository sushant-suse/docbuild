Fix problem in logging test

The test suite reported a ValueError with I/O operations on closed files.
The fix ensures that we clean all handlers before and after the respective test.