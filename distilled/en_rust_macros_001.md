# Rust Macros

## Problem

Implement declarative and procedural macros in Rust to reduce code duplication, create domain-specific languages (DSLs), and generate boilerplate code automatically.

### Requirements
- Declarative macros with pattern matching
- Procedural macros (derive, attribute, function-like)
- Hygiene and macro safety
- Recursive macro expansion
- Code generation and metaprogramming
- Error reporting in macros

## Implementation

### Declarative Macros

```rust
/// Create a hash map with initial values
macro_rules! hashmap {
    () => {
        std::collections::HashMap::new()
    };
    
    ($($key:expr => $value:expr),+ $(,)?) => {
        {
            let mut map = std::collections::HashMap::new();
            $(
                map.insert($key, $value);
            )*
            map
        }
    };
}

/// Create a vector with type checking
macro_rules! typed_vec {
    ($type:ty; $($elem:expr),+ $(,)?) => {
        {
            let mut v: Vec<$type> = Vec::new();
            $(
                v.push($elem as $type);
            )*
            v
        }
    };
    
    ($($elem:expr),+ $(,)?) => {
        vec![$($elem),*]
    };
}

/// Implement a trait with boilerplate methods
macro_rules! impl_display {
    ($type:ty) => {
        impl std::fmt::Display for $type {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", stringify!($type))
            }
        }
    };
}

/// Chain method calls safely
macro_rules! chain {
    ($obj:expr; $($method:ident($($arg:expr),*)),+ $(,)?) => {
        {
            let mut obj = $obj;
            $(
                obj = obj.$method($($arg),*);
            )*
            obj
        }
    };
}

// Usage examples
fn example_usage() {
    let map = hashmap! {
        "key1" => 1,
        "key2" => 2,
    };
    
    let numbers = typed_vec!(i32; 1, 2, 3, 4, 5);
    
    struct MyStruct;
    impl_display!(MyStruct);
    
    let result = chain! {
        String::new();
        push_str("Hello"),
        push_str(", "),
        push_str("World")
    };
}
```

### Procedural Macros

```rust
use proc_macro::TokenStream;
use quote::{quote, format_ident};
use syn::{parse_macro_input, DeriveInput, Data, Fields, Ident};

/// Derive macro for automatic builder pattern
#[proc_macro_derive(Builder)]
pub fn derive_builder(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    
    let name = &input.ident;
    let builder_name = format_ident!("{}Builder", name);
    
    let fields = match &input.data {
        Data::Struct(data) => match &data.fields {
            Fields::Named(fields) => &fields.named,
            _ => panic!("Only named fields are supported"),
        },
        _ => panic!("Only structs are supported"),
    };
    
    let field_names: Vec<_> = fields.iter().map(|f| &f.ident).collect();
    let field_types: Vec<_> = fields.iter().map(|f| &f.ty).collect();
    
    let expanded = quote! {
        pub struct #builder_name {
            #(
                #field_names: Option<#field_types>,
            )*
        }
        
        impl #builder_name {
            #(
                pub fn #field_names(mut self, value: #field_types) -> Self {
                    self.#field_names = Some(value);
                    self
                }
            )*
            
            pub fn build(self) -> Result<#name, String> {
                #(
                    let #field_names = self.#field_names.ok_or_else(|| {
                        format!("Missing field: {}", stringify!(#field_names))
                    })?;
                )*
                
                Ok(#name {
                    #(
                        #field_names,
                    )*
                })
            }
        }
        
        impl #name {
            pub fn builder() -> #builder_name {
                #builder_name {
                    #(
                        #field_names: None,
                    )*
                }
            }
        }
    };
    
    TokenStream::from(expanded)
}

/// Attribute macro for logging function calls
#[proc_macro_attribute]
pub fn log_calls(attr: TokenStream, item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as syn::ItemFn);
    
    let syn::ItemFn {
        attrs,
        vis,
        sig,
        block,
    } = input;
    
    let fn_name = &sig.ident;
    
    let expanded = quote! {
        #(#attrs)*
        #vis #sig {
            println!("Calling function: {}", stringify!(#fn_name));
            let result = #block;
            println!("Function {} returned", stringify!(#fn_name));
            result
        }
    };
    
    TokenStream::from(expanded)
}

/// Function-like macro for SQL-like queries
#[proc_macro]
pub fn query(input: TokenStream) -> TokenStream {
    let query_string = input.to_string();
    
    let expanded = quote! {
        {
            let query = #query_string;
            println!("Executing query: {}", query);
            query
        }
    };
    
    TokenStream::from(expanded)
}
```

### Advanced Macro Patterns

```rust
/// Recursive macro for tree traversal
macro_rules! tree {
    // Leaf node
    ($value:expr) => {
        TreeNode::Leaf($value)
    };
    
    // Branch with children
    ($value:expr => [$($child:tt),+ $(,)?]) => {
        {
            let mut children = Vec::new();
            $(
                children.push(tree!($child));
            )*
            TreeNode::Branch {
                value: $value,
                children,
            }
        }
    };
}

#[derive(Debug)]
enum TreeNode<T> {
    Leaf(T),
    Branch { value: T, children: Vec<TreeNode<T>> },
}

/// Macro for pattern matching with guards
macro_rules! match_all {
    ($value:expr, [$($pattern:pat $(if $guard:expr)? => $result:expr),+ $(,)?]) => {
        {
            let val = $value;
            $(
                if let $pattern = val $(if $guard)? {
                    $result
                } else
            )*
            {
                panic!("No pattern matched for {:?}", val);
            }
        }
    };
}

/// Macro for compile-time string concatenation
macro_rules! concat_strings {
    ($($s:expr),+ $(,)?) => {
        {
            const fn concat_length($($s: &str),+) -> usize {
                0 $(+ $s.len())*
            }
            
            const LEN: usize = concat_length($($s),+);
            const fn concat<const N: usize>($($s: &str),+) -> [u8; N] {
                let mut arr = [0u8; N];
                let mut i = 0;
                $(
                    let bytes = $s.as_bytes();
                    let mut j = 0;
                    while j < bytes.len() {
                        arr[i] = bytes[j];
                        i += 1;
                        j += 1;
                    }
                )*
                arr
            }
            
            const RESULT: &[u8] = &concat::<LEN>($($s),+);
            unsafe { std::str::from_utf8_unchecked(RESULT) }
        }
    };
}

/// DSL for defining state machines
macro_rules! state_machine {
    (
        $name:ident {
            $($state:ident),+ $(,)?
        }
        transitions {
            $($from:ident => $to:ident : $event:ident),+ $(,)?
        }
        initial $initial:ident
    ) => {
        #[derive(Debug, Clone, PartialEq)]
        enum $name {
            $($state),+
        }
        
        #[derive(Debug, Clone)]
        enum Event {
            $($event),+
        }
        
        impl $name {
            fn initial() -> Self {
                $name::$initial
            }
            
            fn transition(self, event: Event) -> Result<Self, String> {
                match (self, event) {
                    $(
                        ($name::$from, Event::$event) => Ok($name::$to),
                    )*
                    (state, event) => Err(format!(
                        "Invalid transition from {:?} with event {:?}",
                        state, event
                    )),
                }
            }
        }
    };
}

// Usage examples
state_machine! {
    TrafficLight {
        Red,
        Yellow,
        Green,
    }
    transitions {
        Red => Green : TimerExpired,
        Green => Yellow : TimerExpired,
        Yellow => Red : TimerExpired,
    }
    initial Red
}
```

## Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hashmap_macro() {
        let map = hashmap! {
            "a" => 1,
            "b" => 2,
        };
        
        assert_eq!(map.get("a"), Some(&1));
        assert_eq!(map.get("b"), Some(&2));
        assert_eq!(map.get("c"), None);
    }

    #[test]
    fn test_empty_hashmap() {
        let map: std::collections::HashMap<i32, i32> = hashmap![];
        assert!(map.is_empty());
    }

    #[test]
    fn test_chain_macro() {
        let result = chain! {
            vec![1, 2, 3];
            push(4),
            push(5),
            pop()
        };
        
        assert_eq!(result, vec![1, 2, 3, 4]);
    }

    #[test]
    fn test_tree_macro() {
        let tree = tree!(1 => [tree!(2), tree!(3 => [tree!(4)])]);
        
        match tree {
            TreeNode::Branch { value: 1, children } => {
                assert_eq!(children.len(), 2);
            }
            _ => panic!("Expected branch node"),
        }
    }

    #[test]
    fn test_state_machine() {
        let mut light = TrafficLight::initial();
        
        assert_eq!(light, TrafficLight::Red);
        
        light = light.transition(Event::TimerExpired).unwrap();
        assert_eq!(light, TrafficLight::Green);
        
        light = light.transition(Event::TimerExpired).unwrap();
        assert_eq!(light, TrafficLight::Yellow);
    }

    #[test]
    fn test_builder_derive() {
        #[derive(Builder, Debug)]
        struct Person {
            name: String,
            age: u32,
        }
        
        let person = Person::builder()
            .name("Alice".to_string())
            .age(30)
            .build()
            .unwrap();
        
        assert_eq!(person.name, "Alice");
        assert_eq!(person.age, 30);
    }

    #[test]
    fn test_builder_missing_field() {
        #[derive(Builder)]
        struct User {
            id: u32,
            name: String,
        }
        
        let result = User::builder()
            .id(1)
            .build();
        
        assert!(result.is_err());
    }

    #[test]
    fn test_concat_strings() {
        const s: &str = concat_strings!("Hello", ", ", "World");
        assert_eq!(s, "Hello, World");
    }
}
```

## Complexity Analysis

### Compile-Time Complexity

1. **Declarative Macros**: O(n) pattern matching
   - n = number of patterns to try
   - Simple text substitution
   - Hygiene checking

2. **Procedural Macros**: O(m * k)
   - m = size of input AST
   - k = complexity of macro code
   - Full Rust compiler available

3. **Recursive Macros**: O(depth)
   - Limited by recursion depth
   - Can hit compiler limits

### Runtime Complexity

1. **Generated Code**: Same as hand-written
   - No runtime overhead
   - Code executes at full speed

2. **Macro Hygiene**: Zero runtime cost
   - All hygiene checked at compile time
   - No runtime checks needed

### Space Complexity

1. **Code Size**: O(generated code)
   - Macros can increase binary size
   - Generic code duplication possible

2. **Compile Time Memory**: O(AST size)
   - Procedural macros hold AST in memory
   - Large inputs can slow compilation

### Best Practices

1. **Documentation**: Always document macro usage and generated code
2. **Error Messages**: Provide clear error messages in procedural macros
3. **Testing**: Test macro expansion with various inputs
4. **Readability**: Prefer simple patterns over complex ones
5. **Hygiene**: Be aware of variable capture and hygiene issues
6. **Recursion**: Use recursion carefully, provide base cases
