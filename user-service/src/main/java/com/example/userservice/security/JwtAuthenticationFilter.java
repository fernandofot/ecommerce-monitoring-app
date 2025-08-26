// user-service/src/main/java/com/example/userservice/security/JwtAuthenticationFilter.java

package com.example.userservice.security;

import com.example.userservice.service.JwtService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

// @Component annotation marks this class as a Spring component, so it can be automatically detected.
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    // Dependency injection via constructor.
    public JwtAuthenticationFilter(JwtService jwtService, UserDetailsService userDetailsService) {
        this.jwtService = jwtService;
        this.userDetailsService = userDetailsService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        // Get the "Authorization" header from the request.
        final String authHeader = request.getHeader("Authorization");
        final String jwt;
        final String userEmail;

        // Check if the header exists and starts with "Bearer ".
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            // If not, pass the request to the next filter in the chain.
            filterChain.doFilter(request, response);
            return;
        }

        // Extract the JWT token (the part after "Bearer ").
        jwt = authHeader.substring(7);
        // Extract the username (email) from the JWT.
        userEmail = jwtService.extractUsername(jwt);

        // Check if the username is not null and the user is not already authenticated.
        if (userEmail != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            // Load user details from the database.
            UserDetails userDetails = this.userDetailsService.loadUserByUsername(userEmail);

            // Validate the token.
            if (jwtService.isTokenValid(jwt, userDetails)) {
                // Create an authentication object.
                UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                        userDetails, null, userDetails.getAuthorities()
                );
                authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));

                // Update the security context with the authenticated user.
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }

        // Continue the filter chain.
        filterChain.doFilter(request, response);
    }
}
