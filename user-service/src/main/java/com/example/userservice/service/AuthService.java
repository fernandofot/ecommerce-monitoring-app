// user-service/src/main/java/com/example/userservice/service/AuthService.java

package com.example.userservice.service;

import com.example.userservice.model.User;
import com.example.userservice.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

// @Service annotation marks this class as a Spring Service, a component that contains business logic.
@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    // The constructor is used for dependency injection. Spring automatically provides the required
    // beans (UserRepository and PasswordEncoder).
    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    /**
     * Registers a new user.
     * @param user The user object to be registered.
     * @return The saved user object.
     * @throws IllegalStateException if a user with the given email or username already exists.
     */
    public User registerUser(User user) {
        // Check if a user with the same email or username already exists.
        Optional<User> existingUserByEmail = userRepository.findByEmail(user.getEmail());
        if (existingUserByEmail.isPresent()) {
            throw new IllegalStateException("Email already in use.");
        }

        Optional<User> existingUserByUsername = userRepository.findByUsername(user.getUsername());
        if (existingUserByUsername.isPresent()) {
            throw new IllegalStateException("Username already in use.");
        }

        // Hash the user's password before saving it to the database for security.
        String encodedPassword = passwordEncoder.encode(user.getPassword());
        user.setPassword(encodedPassword);

        // Save the new user to the database.
        return userRepository.save(user);
    }

    /**
     * Authenticates a user.
     * @param email The user's email.
     * @param password The user's plain-text password.
     * @return An Optional containing the authenticated User if credentials are valid, or empty otherwise.
     */
    public Optional<User> authenticateUser(String email, String password) {
        // Find the user by their email address.
        Optional<User> userOptional = userRepository.findByEmail(email);

        // If the user is found, check if the provided password matches the stored hashed password.
        if (userOptional.isPresent()) {
            User user = userOptional.get();
            // passwordEncoder.matches() compares the plain-text password with the stored hash.
            if (passwordEncoder.matches(password, user.getPassword())) {
                return userOptional;
            }
        }
        // Return an empty Optional if the user is not found or the password doesn't match.
        return Optional.empty();
    }
}
