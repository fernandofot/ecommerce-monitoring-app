// File: user-service/src/main/java/com/example/userservice/controller/AuthController.java
// This is the corrected controller with the login logic fix.

package com.example.userservice.controller;

import com.example.userservice.model.User;
import com.example.userservice.payload.request.LoginRequest;
import com.example.userservice.payload.request.RegisterRequest;
import com.example.userservice.payload.response.LoginResponse;
import com.example.userservice.payload.response.MessageResponse;
import com.example.userservice.service.AuthService;
import com.example.userservice.service.JwtService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

// @RestController marks this class as a RESTful controller.
@RestController
// @RequestMapping defines the base path for all endpoints in this controller.
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;
    private final JwtService jwtService;

    // The constructor is used for dependency injection.
    public AuthController(AuthService authService, JwtService jwtService) {
        this.authService = authService;
        this.jwtService = jwtService;
    }

    /**
     * Handles user registration.
     * @param request The registration request body.
     * @return A ResponseEntity with a success message or an error message.
     */
    @PostMapping("/register")
    public ResponseEntity<?> registerUser(@RequestBody RegisterRequest request) {
        try {
            // Create a new User object from the request data.
            User user = new User();
            user.setEmail(request.getEmail());
            user.setUsername(request.getUsername());
            user.setPassword(request.getPassword());

            // Call the service to register the user.
            authService.registerUser(user);
            return new ResponseEntity<>(new MessageResponse("User registered successfully!"), HttpStatus.CREATED);
        } catch (IllegalStateException e) {
            // Return a 409 Conflict if the user already exists.
            return new ResponseEntity<>(new MessageResponse(e.getMessage()), HttpStatus.CONFLICT);
        }
    }

    /**
     * Handles user login.
     * @param request The login request body.
     * @return A ResponseEntity with a JWT token or an error message.
     */
    @PostMapping("/login")
    public ResponseEntity<?> loginUser(@RequestBody LoginRequest request) {
        // Authenticate the user by username, not email.
        Optional<User> userOptional = authService.authenticateUser(request.getUsername(), request.getPassword());
        
        if (userOptional.isPresent()) {
            User user = userOptional.get();
            // Generate a JWT token for the authenticated user.
            String jwt = jwtService.generateToken(
                new org.springframework.security.core.userdetails.User(user.getEmail(), user.getPassword(), null)
            );
            // Return the JWT token in the response.
            return new ResponseEntity<>(new LoginResponse(jwt, "Login successful!"), HttpStatus.OK);
        } else {
            // Return a 401 Unauthorized if authentication fails.
            return new ResponseEntity<>(new MessageResponse("Invalid username or password."), HttpStatus.UNAUTHORIZED);
        }
    }

    /**
     * Protected endpoint to get user profile. Requires a valid JWT.
     * @param user The authenticated user from the SecurityContext.
     * @return A ResponseEntity with the user's details.
     */
    @GetMapping("/profile")
    public ResponseEntity<User> getProfile(@RequestHeader("Authorization") String token) {
        String jwt = token.substring(7); // Remove "Bearer " prefix
        String email = jwtService.extractUsername(jwt);
        return authService.authenticateUser(email, "") // Authenticate with a fake password since token is valid
            .map(user -> ResponseEntity.ok(user))
            .orElseGet(() -> ResponseEntity.status(HttpStatus.UNAUTHORIZED).build());
    }
}
