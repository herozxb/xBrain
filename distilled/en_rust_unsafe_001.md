# Rust Unsafe Code Patterns

## Problem

Explain and demonstrate safe wrappers around unsafe Rust code, including raw pointer manipulation, FFI boundaries, and mutable statics.

## Implementation

```rust
use std::ptr;
use std::cell::UnsafeCell;

// Safe wrapper around unsafe raw pointer operations
pub struct RawBuffer<T> {
    ptr: *mut T,
    len: usize,
    capacity: usize,
}

impl<T> RawBuffer<T> {
    pub fn new(capacity: usize) -> Self {
        let ptr = if capacity == 0 {
            ptr::null_mut()
        } else {
            // SAFETY: We check capacity > 0 and allocate with proper layout
            unsafe {
                let layout = std::alloc::Layout::array::<T>(capacity)
                    .expect("Layout calculation failed");
                let ptr = std::alloc::alloc(layout) as *mut T;
                if ptr.is_null() {
                    std::alloc::handle_alloc_error(layout);
                }
                ptr
            }
        };
        Self { ptr, len: 0, capacity }
    }

    pub fn push(&mut self, value: T) -> Result<(), &'static str> {
        if self.len >= self.capacity {
            return Err("Buffer full");
        }
        
        // SAFETY: We verified len < capacity and ptr is valid
        unsafe {
            ptr::write(self.ptr.add(self.len), value);
        }
        self.len += 1;
        Ok(())
    }

    pub fn get(&self, index: usize) -> Option<&T> {
        if index >= self.len {
            return None;
        }
        // SAFETY: index < len ensures valid access
        unsafe {
            Some(&*self.ptr.add(index))
        }
    }

    pub fn len(&self) -> usize {
        self.len
    }
}

impl<T> Drop for RawBuffer<T> {
    fn drop(&mut self) {
        if self.capacity > 0 {
            // SAFETY: ptr was allocated with this layout
            unsafe {
                // Drop all elements
                for i in 0..self.len {
                    ptr::drop_in_place(self.ptr.add(i));
                }
                let layout = std::alloc::Layout::array::<T>(self.capacity)
                    .expect("Layout calculation failed");
                std::alloc::dealloc(self.ptr as *mut u8, layout);
            }
        }
    }
}

// Interior mutability with unsafe
pub struct VolatileCell<T> {
    value: UnsafeCell<T>,
}

impl<T> VolatileCell<T> {
    pub fn new(value: T) -> Self {
        Self {
            value: UnsafeCell::new(value),
        }
    }

    pub fn get(&self) -> T 
    where 
        T: Copy 
    {
        // SAFETY: We only read, no concurrent writes in single-threaded context
        unsafe { ptr::read_volatile(self.value.get()) }
    }

    pub fn set(&self, value: T) {
        // SAFETY: Volatile write for hardware register simulation
        unsafe {
            ptr::write_volatile(self.value.get(), value);
        }
    }
}

// Safe FFI wrapper
mod ffi {
    use std::ffi::{CStr, CString};
    use std::os::raw::c_char;

    extern "C" {
        fn strlen(s: *const c_char) -> usize;
        fn strcpy(dest: *mut c_char, src: *const c_char) -> *mut c_char;
    }

    pub fn safe_strlen(s: &str) -> Result<usize, std::ffi::NulError> {
        let c_string = CString::new(s)?;
        // SAFETY: CString guarantees null-terminated string
        Ok(unsafe { strlen(c_string.as_ptr()) })
    }

    pub fn safe_strcpy(dest: &mut [u8], src: &str) -> Result<(), &'static str> {
        if src.len() + 1 > dest.len() {
            return Err("Destination too small");
        }
        let c_string = CString::new(src).map_err(|_| "Invalid string")?;
        // SAFETY: We verified buffer size, CString is null-terminated
        unsafe {
            strcpy(dest.as_mut_ptr() as *mut c_char, c_string.as_ptr());
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_raw_buffer() {
        let mut buf: RawBuffer<i32> = RawBuffer::new(5);
        assert_eq!(buf.len(), 0);
        
        buf.push(10).unwrap();
        buf.push(20).unwrap();
        buf.push(30).unwrap();
        
        assert_eq!(buf.len(), 3);
        assert_eq!(buf.get(0), Some(&10));
        assert_eq!(buf.get(1), Some(&20));
        assert_eq!(buf.get(2), Some(&30));
        assert_eq!(buf.get(3), None);
    }

    #[test]
    fn test_buffer_full() {
        let mut buf: RawBuffer<i32> = RawBuffer::new(2);
        buf.push(1).unwrap();
        buf.push(2).unwrap();
        assert!(buf.push(3).is_err());
    }

    #[test]
    fn test_volatile_cell() {
        let cell = VolatileCell::new(42u32);
        assert_eq!(cell.get(), 42);
        cell.set(100);
        assert_eq!(cell.get(), 100);
    }

    #[test]
    fn test_ffi_strlen() {
        let result = ffi::safe_strlen("hello").unwrap();
        assert_eq!(result, 5);
    }
}
```

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| RawBuffer::new | O(1) | O(capacity) |
| RawBuffer::push | O(1) | O(1) |
| RawBuffer::get | O(1) | O(1) |
| RawBuffer::drop | O(n) | O(1) |
| VolatileCell::get/set | O(1) | O(1) |

## Key Points

1. **Safety Invariants**: Document all safety requirements with `// SAFETY:` comments
2. **Minimal Unsafe Scope**: Keep unsafe blocks as small as possible
3. **Safe Wrappers**: Expose only safe APIs to users
4. **FFI Boundaries**: Validate all inputs crossing FFI boundaries
5. **Memory Leaks**: Ensure Drop implementations handle cleanup
