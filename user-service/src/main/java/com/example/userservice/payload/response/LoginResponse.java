// user-service/src/main/java/com/example/userservice/payload/response/LoginResponse.java

package com.example.userservice.payload.response;

// This DTO holds the JWT token and a message after a successful login.
public class LoginResponse {

    private String token;
    private String message;

    public LoginResponse(String token, String message) {
        this.token = token;
        this.message = message;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
