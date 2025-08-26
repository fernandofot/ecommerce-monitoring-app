// user-service/src/main/java/com/example/userservice/service/CustomUserDetailsService.java

package com.example.userservice.service;

import com.example.userservice.repository.UserRepository;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.ArrayList; // Used to create an empty list of authorities

// @Service marks this class as a service component in Spring.
@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    // Dependency injection via constructor.
    public CustomUserDetailsService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    /**
     * Locates the user based on the username. In our case, the username is the user's email.
     * @param email The email identifying the user whose data is required.
     * @return A fully populated user record (UserDetails object).
     * @throws UsernameNotFoundException if the user could not be found or the user has no GrantedAuthority.
     */
    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        // Find the user by their email using the UserRepository.
        return userRepository.findByEmail(email)
                .map(user -> new org.springframework.security.core.userdetails.User(
                        user.getEmail(),
                        user.getPassword(),
                        new ArrayList<>() // Empty list of authorities for now.
                ))
                .orElseThrow(() -> new UsernameNotFoundException("User not found with email: " + email));
    }
}
