// user-service/src/main/java/com/example/userservice/payload/request/LoginRequest.java

package com.example.userservice.payload.request;

// This DTO is for handling the login request from the client.
public class LoginRequest {

    private String email;
    private String password;

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
