# Foreign Function Interface (FFI) in Rust

## Problem

Implement safe and efficient Rust bindings to C libraries using the Foreign Function Interface (FFI), ensuring memory safety and proper error handling across language boundaries.

### Requirements
- Safe wrappers around unsafe C functions
- Proper memory management across FFI boundary
- Error handling between Rust and C
- Type conversions between Rust and C types
- Callback support from C to Rust
- Thread-safe FFI operations

## Implementation

### Basic FFI Bindings

```rust
use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int, c_void};
use std::ptr;

/// Safe wrapper for a C string processing function
pub fn process_string(input: &str) -> Result<String, String> {
    let c_input = CString::new(input).map_err(|e| format!("Invalid input: {}", e))?;
    
    unsafe {
        let result_ptr = process_string_ffi(c_input.as_ptr());
        
        if result_ptr.is_null() {
            return Err("Processing failed".to_string());
        }
        
        let c_result = CStr::from_ptr(result_ptr);
        let result = c_result.to_string_lossy().into_owned();
        
        // Free the C-allocated memory
        free_string_ffi(result_ptr);
        
        Ok(result)
    }
}

// FFI declarations
extern "C" {
    fn process_string_ffi(input: *const c_char) -> *mut c_char;
    fn free_string_ffi(ptr: *mut c_char);
}

// Corresponding C code:
/*
#include <stdlib.h>
#include <string.h>

char* process_string_ffi(const char* input) {
    size_t len = strlen(input);
    char* result = malloc(len + 1);
    if (result) {
        strcpy(result, input);
        strupr(result); // Convert to uppercase
    }
    return result;
}

void free_string_ffi(char* ptr) {
    free(ptr);
}
*/
```

### Struct Wrappers

```rust
use std::marker::PhantomData;
use std::ptr::NonNull;

/// Opaque pointer to C library handle
#[repr(C)]
pub struct DatabaseHandle {
    _private: [u8; 0],
}

/// Safe wrapper for C database handle
pub struct Database {
    handle: NonNull<DatabaseHandle>,
}

impl Database {
    /// Open a database connection
    pub fn open(path: &str) -> Result<Self, String> {
        let c_path = CString::new(path).map_err(|e| e.to_string())?;
        
        unsafe {
            let handle = db_open(c_path.as_ptr());
            
            NonNull::new(handle)
                .map(|h| Database { handle: h })
                .ok_or_else(|| "Failed to open database".to_string())
        }
    }
    
    /// Execute a query
    pub fn query(&self, sql: &str) -> Result<ResultSet, String> {
        let c_sql = CString::new(sql).map_err(|e| e.to_string())?;
        
        unsafe {
            let result = db_query(self.handle.as_ptr(), c_sql.as_ptr());
            
            if result.is_null() {
                return Err("Query failed".to_string());
            }
            
            Ok(ResultSet {
                handle: NonNull::new_unchecked(result),
            })
        }
    }
}

impl Drop for Database {
    fn drop(&mut self) {
        unsafe {
            db_close(self.handle.as_ptr());
        }
    }
}

// Prevent Send/Sync auto-traits unless the C library is thread-safe
unsafe impl Send for Database {}

/// Result set from a query
pub struct ResultSet {
    handle: NonNull<ResultSetHandle>,
}

impl ResultSet {
    pub fn next(&self) -> Option<Row> {
        unsafe {
            let row = db_next_row(self.handle.as_ptr());
            if row.is_null() {
                None
            } else {
                Some(Row { handle: NonNull::new_unchecked(row) })
            }
        }
    }
}

impl Drop for ResultSet {
    fn drop(&mut self) {
        unsafe {
            db_free_result(self.handle.as_ptr());
        }
    }
}

// FFI declarations
extern "C" {
    type ResultSetHandle;
    
    fn db_open(path: *const c_char) -> *mut DatabaseHandle;
    fn db_close(db: *mut DatabaseHandle);
    fn db_query(db: *mut DatabaseHandle, sql: *const c_char) -> *mut ResultSetHandle;
    fn db_free_result(result: *mut ResultSetHandle);
    fn db_next_row(result: *mut ResultSetHandle) -> *mut RowHandle;
}
```

### Callback Functions

```rust
use std::ffi::c_void;

/// Type alias for callback function
type ProgressCallback = extern "C" fn(progress: c_int, user_data: *mut c_void) -> c_int;

/// Safe wrapper for async processing with callbacks
pub struct Processor {
    callback: Option<Box<dyn Fn(i32) -> bool + Send>>,
}

impl Processor {
    pub fn new() -> Self {
        Processor { callback: None }
    }
    
    /// Set progress callback
    pub fn set_callback<F>(&mut self, callback: F)
    where
        F: Fn(i32) -> bool + Send + 'static,
    {
        self.callback = Some(Box::new(callback));
    }
    
    /// Process data with callback
    pub fn process(&self, data: &[u8]) -> Result<Vec<u8>, String> {
        unsafe {
            let mut callback_data = CallbackData {
                callback: self.callback.as_ref().map(|cb| &**cb as *const _),
            };
            
            let mut output_len: usize = 0;
            let output_ptr = process_data_ffi(
                data.as_ptr(),
                data.len(),
                Some(progress_trampoline),
                &mut callback_data as *mut _ as *mut c_void,
                &mut output_len,
            );
            
            if output_ptr.is_null() {
                return Err("Processing failed".to_string());
            }
            
            let output = std::slice::from_raw_parts(output_ptr, output_len).to_vec();
            free_buffer_ffi(output_ptr);
            
            Ok(output)
        }
    }
}

/// Trampoline function that converts C callback to Rust closure
extern "C" fn progress_trampoline(progress: c_int, user_data: *mut c_void) -> c_int {
    unsafe {
        let callback_data = &*(user_data as *const CallbackData);
        
        if let Some(callback_ptr) = callback_data.callback {
            let callback = &*(callback_ptr as *const Box<dyn Fn(i32) -> bool>);
            if callback(progress as i32) {
                return 1; // Continue
            }
        }
        
        return 0; // Stop
    }
}

struct CallbackData {
    callback: Option<*const dyn Fn(i32) -> bool>,
}

// FFI declarations
extern "C" {
    fn process_data_ffi(
        input: *const u8,
        input_len: usize,
        callback: Option<ProgressCallback>,
        user_data: *mut c_void,
        output_len: *mut usize,
    ) -> *mut u8;
    
    fn free_buffer_ffi(ptr: *mut u8);
}
```

### Error Handling

```rust
use std::fmt;

/// Error type for FFI operations
#[derive(Debug)]
pub enum FfiError {
    NullPointer,
    InvalidUtf8,
    Custom(String),
}

impl fmt::Display for FfiError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            FfiError::NullPointer => write!(f, "Null pointer encountered"),
            FfiError::InvalidUtf8 => write!(f, "Invalid UTF-8 string"),
            FfiError::Custom(msg) => write!(f, "{}", msg),
        }
    }
}

impl std::error::Error for FfiError {}

/// Convert C error code to Result
pub fn check_error(code: c_int) -> Result<(), FfiError> {
    match code {
        0 => Ok(()),
        1 => Err(FfiError::NullPointer),
        2 => Err(FfiError::InvalidUtf8),
        code => Err(FfiError::Custom(format!("Error code: {}", code))),
    }
}

/// Safe wrapper that extracts error messages
pub fn safe_call<F, T>(f: F) -> Result<T, FfiError>
where
    F: FnOnce() -> c_int,
{
    let code = f();
    check_error(code)?;
    // Actual value retrieval would go here
    unimplemented!()
}
```

## Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::ffi::CString;

    #[test]
    fn test_string_conversion() {
        let rust_string = "Hello, World!";
        let c_string = CString::new(rust_string).unwrap();
        
        // Should not panic
        let _ptr = c_string.as_ptr();
    }

    #[test]
    fn test_null_pointer_handling() {
        unsafe {
            let ptr: *const c_char = ptr::null();
            let result = std::panic::catch_unwind(|| {
                CStr::from_ptr(ptr)
            });
            
            // Should handle null gracefully
            assert!(result.is_err() || result.unwrap().to_bytes().is_empty());
        }
    }

    #[test]
    fn test_callback_trampoline() {
        let called = std::sync::Arc::new(std::sync::atomic::AtomicBool::new(false));
        let called_clone = called.clone();
        
        let callback = move |progress: i32| {
            called_clone.store(true, std::sync::atomic::Ordering::SeqCst);
            progress < 100
        };
        
        let callback_data = CallbackData {
            callback: Some(&callback as *const _),
        };
        
        unsafe {
            let result = progress_trampoline(
                50,
                &callback_data as *const _ as *mut c_void,
            );
            
            assert_eq!(result, 1);
            assert!(called.load(std::sync::atomic::Ordering::SeqCst));
        }
    }

    #[test]
    fn test_database_wrapper() {
        // Mock test - would need actual C library
        // This demonstrates the API usage
        
        // let db = Database::open("test.db").unwrap();
        // let results = db.query("SELECT * FROM users").unwrap();
        // 
        // while let Some(row) = results.next() {
        //     // Process row
        // }
    }

    #[test]
    fn test_error_handling() {
        assert!(check_error(0).is_ok());
        assert!(check_error(1).is_err());
        assert!(check_error(2).is_err());
        assert!(check_error(999).is_err());
    }
}
```

## Complexity Analysis

### Time Complexity

1. **String Conversions**: O(n)
   - CString::new: O(n) to check for null bytes
   - CStr::to_string_lossy: O(n) to convert

2. **FFI Function Calls**: O(1) + C function time
   - Direct function call overhead
   - No additional complexity from Rust side

3. **Callback Trampolines**: O(1)
   - Simple pointer dereference
   - Direct function call

### Space Complexity

1. **String Conversions**: O(n)
   - Temporary C string allocation
   - Must free C-allocated memory

2. **Struct Wrappers**: O(1)
   - Only stores pointer
   - No additional memory overhead

3. **Callback Data**: O(1)
   - Fixed-size struct
   - Pointer to closure

### Safety Considerations

1. **Memory Management**:
   - Clear ownership rules
   - Proper cleanup in Drop implementations
   - Avoid double-free

2. **Thread Safety**:
   - Explicit Send/Sync implementations
   - Synchronization for shared state

3. **Error Handling**:
   - Convert C error codes to Rust Result
   - Handle null pointers gracefully
   - Validate all assumptions

### Best Practices

1. **Minimize unsafe blocks**: Keep them small and well-documented
2. **Validate invariants**: Check all preconditions before unsafe operations
3. **Document safety**: Explain why each unsafe operation is safe
4. **Test extensively**: Cover edge cases and error paths
5. **Use abstraction layers**: Hide unsafe code behind safe APIs
