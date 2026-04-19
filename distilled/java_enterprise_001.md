# Java Enterprise: Microservice REST API with Spring Boot

## Problem
Build a production-ready microservice REST API with proper error handling, validation, caching, and testing.

## Solution

### 1. Entity and DTO Classes

```java
// User.java - JPA Entity
package com.example.demo.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;
import org.hibernate.annotations.Cache;
import org.hibernate.annotations.CacheConcurrencyStrategy;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
@Builder
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100, message = "Name must be between 2 and 100 characters")
    @Column(nullable = false)
    private String name;
    
    @Email(message = "Invalid email format")
    @NotBlank(message = "Email is required")
    @Column(nullable = false, unique = true)
    private String email;
    
    @Column(nullable = false)
    private boolean active = true;
    
    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    private LocalDateTime updatedAt;
}

// UserDTO.java
package com.example.demo.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;

@Data
@NoArgsConstructor @AllArgsConstructor
@Builder
public class UserDTO {
    private Long id;
    
    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100)
    private String name;
    
    @Email @NotBlank
    private String email;
    
    private boolean active;
}

// UserCreateRequest.java
package com.example.demo.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;

@Data
@NoArgsConstructor @AllArgsConstructor
public class UserCreateRequest {
    @NotBlank @Size(min = 2, max = 100)
    private String name;
    
    @Email @NotBlank
    private String email;
}
```

### 2. Repository with Custom Queries

```java
// UserRepository.java
package com.example.demo.repository;

import com.example.demo.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByEmail(String email);
    
    List<User> findByActiveTrue();
    
    @Query("SELECT u FROM User u WHERE " +
           "LOWER(u.name) LIKE LOWER(CONCAT('%', :search, '%')) OR " +
           "LOWER(u.email) LIKE LOWER(CONCAT('%', :search, '%'))")
    Page<User> searchUsers(@Param("search") String search, Pageable pageable);
    
    @Query("SELECT COUNT(u) FROM User u WHERE u.active = true")
    long countActiveUsers();
    
    boolean existsByEmail(String email);
}
```

### 3. Service Layer with Caching

```java
// UserService.java
package com.example.demo.service;

import com.example.demo.dto.UserCreateRequest;
import com.example.demo.dto.UserDTO;
import com.example.demo.entity.User;
import com.example.demo.exception.UserNotFoundException;
import com.example.demo.exception.EmailAlreadyExistsException;
import com.example.demo.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.*;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
@CacheConfig(cacheNames = "users")
public class UserService {
    
    private final UserRepository userRepository;
    
    @Cacheable(key = "#id")
    @Transactional(readOnly = true)
    public UserDTO getUserById(Long id) {
        log.debug("Fetching user with id: {}", id);
        return userRepository.findById(id)
                .map(this::toDTO)
                .orElseThrow(() -> new UserNotFoundException(id));
    }
    
    @Cacheable(key = "'email:' + #email")
    @Transactional(readOnly = true)
    public UserDTO getUserByEmail(String email) {
        return userRepository.findByEmail(email)
                .map(this::toDTO)
                .orElseThrow(() -> new UserNotFoundException(email));
    }
    
    @Cacheable(key = "'search:' + #search + ':' + #pageable.pageNumber + ':' + #pageable.pageSize")
    @Transactional(readOnly = true)
    public Page<UserDTO> searchUsers(String search, Pageable pageable) {
        return userRepository.searchUsers(search, pageable)
                .map(this::toDTO);
    }
    
    @CacheEvict(allEntries = true)
    @Transactional
    public UserDTO createUser(UserCreateRequest request) {
        log.info("Creating user with email: {}", request.getEmail());
        
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new EmailAlreadyExistsException(request.getEmail());
        }
        
        User user = User.builder()
                .name(request.getName())
                .email(request.getEmail())
                .active(true)
                .build();
        
        return toDTO(userRepository.save(user));
    }
    
    @Caching(evict = {
        @CacheEvict(key = "#id"),
        @CacheEvict(key = "'email:' + #result.email")
    })
    @Transactional
    public UserDTO updateUser(Long id, UserDTO userDTO) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException(id));
        
        // Check email uniqueness if changed
        if (!user.getEmail().equals(userDTO.getEmail()) && 
            userRepository.existsByEmail(userDTO.getEmail())) {
            throw new EmailAlreadyExistsException(userDTO.getEmail());
        }
        
        user.setName(userDTO.getName());
        user.setEmail(userDTO.getEmail());
        user.setActive(userDTO.isActive());
        
        return toDTO(userRepository.save(user));
    }
    
    @CacheEvict(allEntries = true)
    @Transactional
    public void deleteUser(Long id) {
        if (!userRepository.existsById(id)) {
            throw new UserNotFoundException(id);
        }
        userRepository.deleteById(id);
        log.info("Deleted user with id: {}", id);
    }
    
    private UserDTO toDTO(User user) {
        return UserDTO.builder()
                .id(user.getId())
                .name(user.getName())
                .email(user.getEmail())
                .active(user.isActive())
                .build();
    }
}
```

### 4. Global Exception Handling

```java
// GlobalExceptionHandler.java
package com.example.demo.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException ex) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            ex.getMessage(),
            LocalDateTime.now()
        );
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    @ExceptionHandler(EmailAlreadyExistsException.class)
    public ResponseEntity<ErrorResponse> handleEmailExists(EmailAlreadyExistsException ex) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.CONFLICT.value(),
            ex.getMessage(),
            LocalDateTime.now()
        );
        return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationErrors(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error -> 
            errors.put(error.getField(), error.getDefaultMessage())
        );
        
        ErrorResponse error = new ErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            "Validation failed",
            LocalDateTime.now(),
            errors
        );
        return ResponseEntity.badRequest().body(error);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneric(Exception ex) {
        log.error("Unexpected error", ex);
        ErrorResponse error = new ErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "An unexpected error occurred",
            LocalDateTime.now()
        );
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}

// ErrorResponse.java
package com.example.demo.exception;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;

@Data
@NoArgsConstructor @AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ErrorResponse {
    private int status;
    private String message;
    private LocalDateTime timestamp;
    private Map<String, String> details;
    
    public ErrorResponse(int status, String message, LocalDateTime timestamp) {
        this(status, message, timestamp, null);
    }
}

// Custom Exceptions
package com.example.demo.exception;

public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(Long id) {
        super("User not found with id: " + id);
    }
    
    public UserNotFoundException(String email) {
        super("User not found with email: " + email);
    }
}

public class EmailAlreadyExistsException extends RuntimeException {
    public EmailAlreadyExistsException(String email) {
        super("Email already exists: " + email);
    }
}
```

### 5. REST Controller

```java
// UserController.java
package com.example.demo.controller;

import com.example.demo.dto.UserCreateRequest;
import com.example.demo.dto.UserDTO;
import com.example.demo.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Tag(name = "User Management", description = "User CRUD operations")
public class UserController {
    
    private final UserService userService;
    
    @GetMapping("/{id}")
    @Operation(summary = "Get user by ID")
    public ResponseEntity<UserDTO> getUserById(@PathVariable Long id) {
        return ResponseEntity.ok(userService.getUserById(id));
    }
    
    @GetMapping("/email/{email}")
    @Operation(summary = "Get user by email")
    public ResponseEntity<UserDTO> getUserByEmail(@PathVariable String email) {
        return ResponseEntity.ok(userService.getUserByEmail(email));
    }
    
    @GetMapping("/search")
    @Operation(summary = "Search users")
    public ResponseEntity<Page<UserDTO>> searchUsers(
            @RequestParam(required = false, defaultValue = "") String query,
            @PageableDefault(size = 20) Pageable pageable) {
        return ResponseEntity.ok(userService.searchUsers(query, pageable));
    }
    
    @PostMapping
    @Operation(summary = "Create a new user")
    public ResponseEntity<UserDTO> createUser(@Valid @RequestBody UserCreateRequest request) {
        UserDTO created = userService.createUser(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "Update an existing user")
    public ResponseEntity<UserDTO> updateUser(
            @PathVariable Long id, 
            @Valid @RequestBody UserDTO userDTO) {
        return ResponseEntity.ok(userService.updateUser(id, userDTO));
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete a user")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
    }
}
```

## Tests

```java
// UserServiceTest.java
package com.example.demo.service;

import com.example.demo.dto.UserCreateRequest;
import com.example.demo.dto.UserDTO;
import com.example.demo.entity.User;
import com.example.demo.exception.EmailAlreadyExistsException;
import com.example.demo.exception.UserNotFoundException;
import com.example.demo.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.*;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @InjectMocks
    private UserService userService;
    
    private User testUser;
    
    @BeforeEach
    void setUp() {
        testUser = User.builder()
                .id(1L)
                .name("John Doe")
                .email("john@example.com")
                .active(true)
                .build();
    }
    
    @Test
    @DisplayName("Should return user when ID exists")
    void getUserById_WhenExists_ReturnsUser() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        
        UserDTO result = userService.getUserById(1L);
        
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("John Doe");
        assertThat(result.getEmail()).isEqualTo("john@example.com");
        verify(userRepository).findById(1L);
    }
    
    @Test
    @DisplayName("Should throw exception when ID not found")
    void getUserById_WhenNotExists_ThrowsException() {
        when(userRepository.findById(999L)).thenReturn(Optional.empty());
        
        assertThatThrownBy(() -> userService.getUserById(999L))
                .isInstanceOf(UserNotFoundException.class)
                .hasMessageContaining("999");
    }
    
    @Test
    @DisplayName("Should create user with valid data")
    void createUser_WithValidData_ReturnsCreatedUser() {
        UserCreateRequest request = new UserCreateRequest("Jane Doe", "jane@example.com");
        User savedUser = User.builder()
                .id(2L)
                .name("Jane Doe")
                .email("jane@example.com")
                .active(true)
                .build();
        
        when(userRepository.existsByEmail("jane@example.com")).thenReturn(false);
        when(userRepository.save(any(User.class))).thenReturn(savedUser);
        
        UserDTO result = userService.createUser(request);
        
        assertThat(result.getId()).isEqualTo(2L);
        assertThat(result.getName()).isEqualTo("Jane Doe");
        verify(userRepository).save(any(User.class));
    }
    
    @Test
    @DisplayName("Should throw exception when email already exists")
    void createUser_WithDuplicateEmail_ThrowsException() {
        UserCreateRequest request = new UserCreateRequest("Jane", "john@example.com");
        
        when(userRepository.existsByEmail("john@example.com")).thenReturn(true);
        
        assertThatThrownBy(() -> userService.createUser(request))
                .isInstanceOf(EmailAlreadyExistsException.class);
        
        verify(userRepository, never()).save(any());
    }
    
    @Test
    @DisplayName("Should return paginated search results")
    void searchUsers_ReturnsPage() {
        Pageable pageable = PageRequest.of(0, 10);
        List<User> users = List.of(testUser);
        Page<User> userPage = new PageImpl<>(users, pageable, 1);
        
        when(userRepository.searchUsers("john", pageable)).thenReturn(userPage);
        
        Page<UserDTO> result = userService.searchUsers("john", pageable);
        
        assertThat(result.getContent()).hasSize(1);
        assertThat(result.getContent().get(0).getName()).isEqualTo("John Doe");
    }
    
    @Test
    @DisplayName("Should delete user when exists")
    void deleteUser_WhenExists_DeletesUser() {
        when(userRepository.existsById(1L)).thenReturn(true);
        doNothing().when(userRepository).deleteById(1L);
        
        userService.deleteUser(1L);
        
        verify(userRepository).deleteById(1L);
    }
    
    @Test
    @DisplayName("Should throw exception when deleting non-existent user")
    void deleteUser_WhenNotExists_ThrowsException() {
        when(userRepository.existsById(999L)).thenReturn(false);
        
        assertThatThrownBy(() -> userService.deleteUser(999L))
                .isInstanceOf(UserNotFoundException.class);
        
        verify(userRepository, never()).deleteById(any());
    }
}

// UserControllerIntegrationTest.java
package com.example.demo.controller;

import com.example.demo.dto.UserCreateRequest;
import com.example.demo.repository.UserRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class UserControllerIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    void createUser_WithValidData_Returns201() throws Exception {
        UserCreateRequest request = new UserCreateRequest("Test User", "test@example.com");
        
        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Test User"))
                .andExpect(jsonPath("$.email").value("test@example.com"));
    }
    
    @Test
    void createUser_WithInvalidEmail_Returns400() throws Exception {
        UserCreateRequest request = new UserCreateRequest("Test", "invalid-email");
        
        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }
    
    @Test
    void getUserById_WhenExists_ReturnsUser() throws Exception {
        // First create a user
        UserCreateRequest request = new UserCreateRequest("Find Me", "find@example.com");
        String response = mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andReturn().getResponse().getContentAsString();
        
        String userId = objectMapper.readTree(response).get("id").asText();
        
        // Then find it
        mockMvc.perform(get("/api/v1/users/" + userId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Find Me"));
    }
    
    @Test
    void getUserById_WhenNotExists_Returns404() throws Exception {
        mockMvc.perform(get("/api/v1/users/99999"))
                .andExpect(status().isNotFound());
    }
    
    @Test
    void searchUsers_ReturnsPaginatedResults() throws Exception {
        // Create some users
        for (int i = 0; i < 5; i++) {
            UserCreateRequest request = new UserCreateRequest("Search" + i, "search" + i + "@example.com");
            mockMvc.perform(post("/api/v1/users")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(request)));
        }
        
        mockMvc.perform(get("/api/v1/users/search")
                .param("query", "Search")
                .param("page", "0")
                .param("size", "3"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(3)))
                .andExpect(jsonPath("$.totalElements").value(5));
    }
}
```

## Key Features

1. **JPA Entity with Validation** - Hibernate validation annotations
2. **DTO Pattern** - Separate request/response objects
3. **Repository Layer** - Custom JPQL queries with pagination
4. **Service Layer** - Business logic with caching (Spring Cache)
5. **Global Exception Handling** - Centralized error responses
6. **REST Controller** - Swagger documentation, pagination support
7. **Unit Tests** - Mockito for service layer
8. **Integration Tests** - Full Spring context with MockMvc
9. **Caching** - Redis-ready with Hibernate second-level cache
10. **Transaction Management** - @Transactional annotations
