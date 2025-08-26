// user-service/src/main/java/com/example/userservice/config/SecurityConfig.java

package com.example.userservice.config;

import com.example.userservice.security.JwtAuthenticationFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

// @Configuration marks this class as a source of bean definitions.
@Configuration
// @EnableWebSecurity enables Spring Security's web security support.
@EnableWebSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    // The constructor is used for dependency injection of the JWT filter.
    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    }

    // This bean provides a secure password encoder (BCrypt).
    // Spring Boot will use this for password hashing in our AuthService.
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    // The SecurityFilterChain bean is the core of Spring Security configuration.
    // It defines the security rules for different request paths.
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            // Disable CSRF protection. This is a common practice for stateless REST APIs
            // that use token-based authentication (like JWT).
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(authorize -> authorize
                // Allow public access to the /api/auth/** endpoints (login, register).
                .requestMatchers("/api/auth/**").permitAll()
                // All other requests require authentication.
                .anyRequest().authenticated()
            )
            // Set the session management to STATELESS. This is critical for JWT-based
            // authentication, as we don't store user state in the session.
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS));

        // Add our custom JWT filter before the standard authentication filter.
        // This ensures our filter checks for the JWT token on every request.
        http.addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
