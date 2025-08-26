// File: user-service/src/main/java/com/example/userservice/payload/request/LoginRequest.java
// This DTO is for handling the login request from the client.

package com.example.userservice.payload.request;

public class LoginRequest {

    // Added the username field to match the login request payload.
    private String username;
    private String password;

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    // Note: This DTO no longer needs the email field as the login is based on username.
    // If you need to support login by email, you could keep it and update the controller.

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
